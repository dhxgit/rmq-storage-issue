### RabbitMQ Quorum Storage Escalation Bug

#### What we do

- A queue where no ingress of messages is happening
- Client is connecting to the queue, start consume
- Client kills their connection if nothing is received after a few seconds
  - this happens every 3 seconds from several devices

#### What happens

- Every Connection attempts seems to be stored in quorum segment files
  - This gets cleaned up if a message flows through the queue
    - (stop test-container and publich / get through management interface)
      - -> all segment files are cleaned up
  - The needed storage grows and grows until full

#### Reproduction Setup

- We start the official rabbitmq container (see docker-compose.yaml)
- We start a python test container which in a loop with a lot of workers does
  - connect to a queue with basic_consume
  - kills basic_consume after a short 2~3 second timeout
- After a few minutes of runtime we can restart the rabbitmq-container
  - this will write out the segments files into the quorum directory
  - this will also happen without restart when the wal-file gets rotated

#### See the segments accumulating

```./update-container.sh
# wait for a few minutes
docker restart rmq_9b64-rabbitmq-1
# check out segment files (after rabbitmq is up again, can take a minute)
ls -alh rabbitmq-data/mnesia/rabbit@rabbitmq/quorum/rabbit@rabbitmq/RMQ-*
```

#### Cleanup the segments with a message

```# enable management
docker exec rmq_9b64-rabbitmq-1 rabbitmq-plugins enable rabbitmq_management
# stop rmq-test container
docker stop rmq_9b64-rmq-test-py-1
```

- open management in browser with rmq-user // rmq-pass
- go to queue rmq-queue
- publish a message
- get the message WITH acknowledge
- -> segments are gone
