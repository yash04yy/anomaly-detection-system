import os,json
from confluent_kafka import KafkaError
from src.consumer import create_consumer
from src.detector import MovingAverageDetector
from src.ml_detector import IsolationForestDetector
from src.notifier import Notifier
from dotenv import load_dotenv

BROKER = "127.0.0.1:9092"
TOPIC = os.getenv("KAFKA_TOPIC", "metrics")
GROUP_ID = "anomaly-worker"

def run():
    load_dotenv() 
    consumer = create_consumer(BROKER, GROUP_ID, TOPIC)
    # Choose which detector to use
    use_ml = os.getenv("USE_ISOLATION_FOREST", "false").lower() == "true"
    if use_ml:
        detector = IsolationForestDetector(batch_size=20, contamination=0.1)
        print("[Worker] Using Isolation Forest Detector")
    else:
        detector = MovingAverageDetector(window_size=5, threshold=20)
        print("[Worker] Using Moving Average Detector")

    notifier = Notifier()
    print("[Worker] Listening for metrics...")
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(msg.error())
            continue

        metric = json.loads(msg.value().decode("utf-8"))
        cpu = float(metric["cpu"])

        if use_ml:
            anomalies = detector.add_metric(cpu)
            for a in anomalies:
                alert_msg = f"Anomaly detected (CPU={a})"
                print("[ALERT]", alert_msg)
                notifier.notify(alert_msg)
        else:
            if detector.detect(cpu):
                alert_msg = f"Anomaly detected: {metric}"
                print("[ALERT]", alert_msg)
                notifier.notify(alert_msg)
            else:
                print("[OK]", metric)
    consumer.close()

if __name__ == "__main__":
    run()