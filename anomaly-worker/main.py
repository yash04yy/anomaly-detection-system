import os,json
from confluent_kafka import KafkaError
from consumer import create_consumer
from detector import MovingAverageDetector

BROKER = "127.0.0.1:9092"
TOPIC = os.getenv("KAFKA_TOPIC", "metrics")
GROUP_ID = "anomaly-worker"

def run():
    consumer = create_consumer(BROKER, GROUP_ID, TOPIC)
    detector = MovingAverageDetector(window_size=5, threshold=3.0)

    print("[Worker] Listening for metrics...")
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(msg.error())
                break

        raw = msg.value()
        if not raw:
            print("[WARN] Received empty message, skipping.")
            continue
        try:
            metric = json.loads(raw.decode("utf-8"))
            cpu = float(metric["cpu"])
        except Exception as e:
            print(f"[ERROR] Failed to decode/process message: {raw!r}; error: {e}")
            continue

        if detector.detect(cpu):
            print("[ANOMALY] CPU spike detected:", metric)
        else:
            print("[OK]", metric)

    consumer.close()

if __name__ == "__main__":
    run()
