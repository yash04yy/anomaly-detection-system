import os,json
from confluent_kafka import KafkaError
from src.consumer import create_consumer
from src.detector import MovingAverageDetector
from src.ml_detector import IsolationForestDetector
from src.notifier import Notifier
from dotenv import load_dotenv
from prometheus_client import start_http_server, Gauge, Counter

BROKER = "127.0.0.1:9092"
TOPIC = os.getenv("KAFKA_TOPIC", "metrics")
GROUP_ID = "anomaly-worker"

cpu_usage_gauge = Gauge('cpu_usage_percent', 'Current CPU Usage in %')
anomaly_gauge = Gauge('cpu_anomaly_detected', 'Anomaly Detected (1 for yes, 0 for no)')
anomaly_counter = Counter('cpu_anomaly_total', 'Number of anomalies detected')

def run():
    load_dotenv() 

    start_http_server(8000)
    print("[Prometheus] Metrics server started at http://localhost:8000/metrics")

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
                cpu_usage_gauge.set(cpu)
                anomaly_gauge.set(1)
                anomaly_counter.inc()
            if not anomalies:
                print("[OK]", metric)
                cpu_usage_gauge.set(cpu)
                anomaly_gauge.set(0)
        else:
            if detector.detect(cpu):
                alert_msg = f"Anomaly detected: {metric}"
                print("[ALERT]", alert_msg)
                notifier.notify(alert_msg)
                cpu_usage_gauge.set(cpu)
                anomaly_gauge.set(1)
                anomaly_counter.inc()
            else:
                print("[OK]", metric)
                cpu_usage_gauge.set(cpu)
                anomaly_gauge.set(0)
    consumer.close()
if __name__ == "__main__":
    run()