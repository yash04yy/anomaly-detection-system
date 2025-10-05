import psycopg2
from datetime import datetime

def get_connection():
    return psycopg2.connect(
        dbname="monitoring",
        user="postgres",
        password="postgres",
        host="192.168.1.101",
        port="5432"
    )

def save_anomaly(
    metric_name,
    value,
    threshold,
    status,
    detection_method=None,
    anomaly_score=None,
    context=None,
    config=None
):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO anomalies (
            timestamp,
            metric_name,
            metric_value,
            threshold,
            status,
            detection_method,
            anomaly_score,
            context,
            config
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            datetime.now(),
            metric_name,
            value,
            threshold,
            status,
            detection_method,
            anomaly_score,
            context,
            config
        )
    )
    conn.commit()
    cur.close()
    conn.close()
