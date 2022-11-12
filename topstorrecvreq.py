#!/usr/bin/python3
import pika, sys
import actionreq


def callback(ch, method, properties, body):
 print(body)
 actionreq.do(str(body), sys.argv[1])
 


myip=sys.argv[1]
cred = pika.PlainCredentials('rabbmezo', 'HIHIHI')
param = pika.ConnectionParameters(myip,5672, '/', cred)
conn = pika.BlockingConnection(param)
chann= conn.channel()
chann.queue_declare(queue='recvreq')
chann.basic_consume(callback, queue='recvreq', no_ack=True)
chann.start_consuming()
