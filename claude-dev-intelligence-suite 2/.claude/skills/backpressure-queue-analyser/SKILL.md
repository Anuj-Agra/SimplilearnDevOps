---
name: backpressure-queue-analyser
description: >
  Analyse event-driven systems (Kafka, RabbitMQ, SQS) for producers without
  back-pressure, consumers without dead-letter queues, missing retention policies,
  and unbounded queue growth. Use when asked: 'back pressure', 'queue depth',
  'Kafka analysis', 'message queue', 'consumer lag', 'dead letter queue', 'DLQ',
  'unbounded queue', 'message backlog', 'producer throttling', 'queue overflow',
  'event-driven issues'. Under parallel load, an unbounded queue is a memory bomb.
---
# Back-pressure & Queue Depth Analyser

Detect event-driven system risks that cause memory exhaustion and message loss.

## Step 1 — Discover Messaging Infrastructure
```bash
# Kafka
grep -rn "spring.kafka\|@KafkaListener\|@EnableKafka\|KafkaTemplate\|\
  ProducerConfig\|ConsumerConfig" \
  . --include="*.yml" --include="*.properties" --include="*.java" | head -40

# RabbitMQ
grep -rn "spring.rabbitmq\|@RabbitListener\|RabbitTemplate\|@Queue\|@Exchange" \
  . --include="*.yml" --include="*.properties" --include="*.java" | head -30

# SQS / SNS
grep -rn "SqsClient\|SnsClient\|@SqsListener\|AmazonSQS" \
  <java_path> --include="*.java" | head -20
```

## Step 2 — Check Each Queue/Topic

### Producer Side
```bash
# Missing back-pressure (producer sends without waiting for consumer capacity)
grep -rn "kafkaTemplate\.send\|rabbitTemplate\.send\|sqsClient\.sendMessage" \
  <java_path> --include="*.java" | \
  grep -v "ListenableFuture\|CompletableFuture\|\.get()\|callback\|onSuccess\|onFailure" \
  | head -20

# Max in-flight messages (producer-side throttle)
grep -rn "max.in.flight.requests\|max\.block\.ms\|buffer.memory" \
  . --include="*.yml" --include="*.properties" | head -10
```

### Consumer Side
```bash
# Dead-letter queue configuration
grep -rn "deadLetterExchange\|dead-letter\|DLQ\|DLT\|@DltHandler\|\
  RetryTopicConfiguration\|DeadLetterPublishingRecoverer" \
  . --include="*.yml" --include="*.properties" --include="*.java" | head -20

# Consumer concurrency
grep -rn "concurrency\|@KafkaListener.*concurrency\|spring.kafka.listener.concurrency" \
  . --include="*.yml" --include="*.properties" --include="*.java" | head -20

# Error handling / retry
grep -rn "SeekToCurrentErrorHandler\|DefaultErrorHandler\|BackOff\|\
  @RetryableTopic\|attempts\|backoff" \
  <java_path> --include="*.java" | head -20
```

### Retention & Overflow
```bash
# Topic retention config
grep -rn "retention.ms\|retention.bytes\|log.retention\|max.message.bytes" \
  . --include="*.yml" --include="*.properties" | head -10
```

## Step 3 — Output

```
BACK-PRESSURE & QUEUE ANALYSIS: [System]

CRITICAL:
  BQ-001: Producer [topic] sends fire-and-forget with no back-pressure
    Risk: Consumer lag grows unboundedly → out of memory or message loss
    Fix: Set max.block.ms and handle send failures; implement producer throttle

  BQ-002: No Dead-Letter Queue for [consumer group]
    Risk: Poison pill message blocks consumer forever; processing stops
    Fix: Configure DLT with @RetryableTopic or DefaultErrorHandler + DLT

HIGH:
  BQ-003: Consumer concurrency = 1 for high-volume topic [name]
    Risk: Cannot keep up with producer under load
    Fix: Set spring.kafka.listener.concurrency = [num partitions]

  BQ-004: No retention policy on topic [name]
    Risk: Unbounded disk growth
    Fix: Set retention.ms = 604800000 (7 days) or appropriate business retention

RECOMMENDED CONFIG:
  [Ready-to-paste Kafka/RabbitMQ configuration]
```
