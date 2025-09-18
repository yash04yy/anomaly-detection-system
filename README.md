# Real-time Event-Driven Anomaly Detection System

## Project Purpose
This project is a **real-time anomaly detection system** built using an event-driven architecture.
It ingests metrics/events, processes them through anomaly detection algorithms, and (in future) raises alerts and visualizes trends on a dashboard.

The main goals:
- Demonstrate event-driven design with Kafka.
- Build scalable anomaly detection using streaming data.
- Extend with alerting, persistence, and monitoring.

---

## Tech Stack
- **Apache Kafka** → Event streaming backbone
- **Node.js** → Ingestion Service (simulates and publishes metrics/events)
- **Python** → Anomaly Detection Worker (consumes events and detects anomalies)
- **MongoDB** → Storage for detected anomalies and historical data
- **Prometheus + Grafana** → Metrics collection and visualization
- **Notification Service** → Alerts (Slack, email, etc.)

---

## High-Level Architecture

```mermaid
flowchart LR
    Producer(Node.js Ingestion Service) -->|metrics| Kafka[(Kafka Topic)]
    Kafka --> Consumer(Python Anomaly Worker)
    Consumer --> Alerts[Notification Service]
    Consumer --> DB[(Storage)]
    DB --> Grafana[(Dashboard)]
