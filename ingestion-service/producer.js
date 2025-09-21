const {Kafka} = require("kafkajs");

const kafka = new Kafka({
    clientId: "metrics-producer",
    brokers: ["localhost:9092"]
});

const producer = kafka.producer();

async function produce(){
    await producer.connect();
    setInterval(async() => {
        const metric = {
            timestamp: new Date().toISOString(),
            cpu: (Math.random() * 100).toFixed(2),
            memory: (Math.random() * 100).toFixed(2)
        };
        await producer.send({
            topic: "metrics",
            messages: [{value: JSON.stringify(metric)}]
        });
        console.log("Sent:", metric);
    },2000);
}
produce().catch(console.error);