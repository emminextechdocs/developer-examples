import java.time.Duration;
import java.util.*;
import org.apache.kafka.clients.consumer.*;
import org.apache.kafka.clients.producer.*;
import org.apache.kafka.common.TopicPartition;

class Replay {
  static final TopicPartition PARTITION = new TopicPartition("orders", 0);
  static Properties consumerProperties() {
    Properties p = new Properties();
    p.put("bootstrap.servers", "localhost:9092");
    p.put("group.id", "recovery-lab");
    p.put("key.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
    p.put("value.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
    p.put("enable.auto.commit", "false");
    p.put("auto.offset.reset", "earliest");
    p.put("max.poll.records", "1");
    return p;
  }
  static ConsumerRecord<String,String> next(KafkaConsumer<String,String> consumer) {
    long deadline = System.nanoTime() + Duration.ofSeconds(30).toNanos();
    while (System.nanoTime() < deadline) {
      var records = consumer.poll(Duration.ofMillis(500));
      if (!records.isEmpty()) return records.iterator().next();
    }
    throw new AssertionError("No record before deadline");
  }
  static void require(boolean condition, String message) {
    if (!condition) throw new AssertionError(message);
  }
  public static void main(String[] args) throws Exception {
    Properties p = new Properties();
    p.put("bootstrap.servers", "localhost:9092");
    p.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
    p.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer");
    p.put("acks", "all");
    p.put("enable.idempotence", "true");
    try (var producer = new KafkaProducer<String,String>(p)) {
      producer.send(new ProducerRecord<>("orders", 0, "ord-1", "created")).get();
      producer.send(new ProducerRecord<>("orders", 0, "ord-2", "created")).get();
    }
    long first;
    try (var c = new KafkaConsumer<String,String>(consumerProperties())) {
      c.assign(List.of(PARTITION));
      var record = next(c);
      first = record.offset();
      System.out.println("READ without commit: offset=" + first + " key=" + record.key());
    }
    try (var c = new KafkaConsumer<String,String>(consumerProperties())) {
      c.assign(List.of(PARTITION));
      var replay = next(c);
      require(replay.offset() == first, "Uncommitted record must replay");
      System.out.println("REPLAY after consumer close: offset=" + replay.offset());
      // This marks progress only. Business effects must already be durable.
      c.commitSync(Map.of(PARTITION, new OffsetAndMetadata(replay.offset() + 1)));
      System.out.println("COMMIT next offset=" + (replay.offset() + 1));
    }
    try (var c = new KafkaConsumer<String,String>(consumerProperties())) {
      c.assign(List.of(PARTITION));
      var next = next(c);
      require(next.offset() == first + 1, "Committed position must be the next record");
      System.out.println("RESUME next record: offset=" + next.offset() + " key=" + next.key());
    }
  }
}
