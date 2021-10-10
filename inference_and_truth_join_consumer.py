import csv
import json
import sys
import os

from json import dumps, loads

import certifi
import ray
import ray as ray
import requests
from confluent_kafka.cimpl import Producer, Consumer, KafkaException, KafkaError, TopicPartition

from datetime import datetime
import time


from river import datasets
from river import evaluate
from river import metrics
from river import tree
from river import anomaly
from river import compose
from river import preprocessing

import numpy as np
import pickle

import model_utils


class InferenceAndTruthConsumer(object):
    def __init__(self, my_id=1, list_of_partitions=[], request_topic='cc_events', result_folder='/tmp/',
                 group_id='my_grp'):
        json_file_path = os.path.join(os.getcwd(), "config/credentials.json")
        with open(json_file_path, 'r') as j:
            creds = json.loads(j.read())

        #self.metric = metrics.ROCAUC()  # metrics.Accuracy() #
        self.my_id = my_id
        self.t = request_topic
        self.result_folder = result_folder

        #self.result_t_p = 8

        self.tls = []
        self.msg_list = []
        self.file_index = 0
        x = 0
        for i in list_of_partitions:
            self.tls.insert(x, TopicPartition(self.t, i))
            x = x + 1
        # self.tls=list_of_partitions
        print(self.tls)


        conf = {'bootstrap.servers': creds['BOOTSTRAP_SERVERS'],
                'sasl.mechanism': 'PLAIN',
                'security.protocol': 'SASL_SSL',
                'ssl.ca.location': certifi.where(),
                'sasl.username': creds['CLUSTER_API_KEY'],
                'sasl.password': creds['CLUSTER_API_SECRET'],
                'group.id': group_id,
                'enable.auto.commit' : False,
                'auto.offset.reset': 'latest'}
        self.consumer = consumer = Consumer(conf)
        self.consumer.assign(self.tls)

    def __del__(self):
        print('closing')
        # self.consumer.close()
        self.consumer.commit()
        self.consumer.close()

    def save_to_file(self):
        file_name = os.path.join(self.result_folder,'part_'+str(self.file_index)+'.csv')
        with open(file_name, 'w') as f:
            csv_writer = csv.writer(f)
            for r in self.msg_list:
                csv_writer.writerow(r)
        self.file_index = self.file_index + 1
        print('Saved to file ' + file_name)

    def process_msg(self,msg):
        my_msg = []
        my_msg.append(msg['account_number'])
        my_msg.append(msg['Time'])
        for i in range(1,29):
            idx = 'V'+str(i)
            my_msg.append(idx)
        my_msg.append(msg['Amount'])
        my_msg.append(msg['Class'])
        my_msg.append(msg['Result'])
        my_msg.append(int(round(float(msg['Result']))))
        my_msg.append(msg['PredictionLatency'])
        return my_msg

    def run(self):
        ### Set up model, metric, and starting timestamp for this model instance ###
        try:
            self.consumer.assign(self.tls)
            i = 1
            while (True):
                msg = self.consumer.poll(timeout=5.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # End of partition event
                        sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                         (msg.topic(), msg.partition(), msg.offset()))
                    elif msg.error():
                        raise KafkaException(msg.error())
                else:
                    message = loads(msg.value().decode("utf-8"))
                    self.msg_list.append(self.process_msg(message))
                    if (len(self.msg_list) % 1000 == 0):
                        print('Invoking on max msg limit ')
                        self.save_to_file()
                        self.consumer.commit()

            self.save_to_file()
            self.consumer.commit()
        finally:
            pass


def process_events(request_topic,partition_ids,result_folder,group_id):
    print('Start')
    consumer = InferenceAndTruthConsumer(my_id=0,  list_of_partitions=partition_ids,
                              request_topic=request_topic, result_folder=result_folder, group_id=group_id)
    consumer.run()

if __name__ == '__main__':
    list_of_partitions = [0,1,2,3,4,5]
    src_topic = 'cc_prediction_truth_join'
    grp_id = 'cc-inf-trutg-grp-1'
    output_folder = model_utils.get_inf_truth_join_folder()
    process_events(src_topic,list_of_partitions,output_folder,grp_id)
    #results = ray.get([process_cc_events.remote('cc_events',[x],'cc_prediction_truth_join','cc-grp-1') for x in range(6)])
    #print(results)


    #time.sleep(10000)