from confluent_kafka import Consumer, KafkaError

def create_consumer(broker, group_id, topic):
    consumer = Consumer({
        "bootstrap.servers": broker,
        "group.id": group_id,
        "auto.offset.reset": "earliest"
    })
    consumer.subscribe([topic])
    return consumer
