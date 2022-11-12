#!/usr/bin/python3
import pika, sys
import actionreply


def callback(ch, method, properties, body):
 actionreply.do(str(body))


myip=sys.argv[1]
cred = pika.PlainCredentials('rabbmezo', 'HIHIHI')
param = pika.ConnectionParameters('rmq',5672, '/', cred)
conn = pika.BlockingConnection(param)
chann= conn.channel()
chann.queue_declare(queue='recvreply')
chann.basic_consume(callback, queue='recvreply', no_ack=True)
chann.start_consuming()
