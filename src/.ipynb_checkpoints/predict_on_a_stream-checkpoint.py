import json
import sys
import os

from json import dumps, loads

import certifi

import ray as ray
import requests
from confluent_kafka.cimpl import Producer, Consumer, KafkaException, KafkaError, TopicPartition
import model_utils

def process_cc_events(request_topic,partition_ids,result_topic,group_id):
    print('Start')
    consumer = EventConsumer(my_id=0,  list_of_partitions=partition_ids,
                              request_topic=request_topic, result_topic=result_topic, group_id=group_id)
    consumer.run()

@ray.remote
def send_query(json):
    headers = {"content-type": "application/json"}
    resp = requests.post("http://127.0.0.1:8000/predict", json=json, headers=headers).text
    return resp

class EventConsumer(object):
    def __init__(self, my_id=1, list_of_partitions=[0], request_topic='cc_events', result_topic='cc_prediction_truth_join',
                 group_id='my_grp'):
        ray.init()
        self.msg_list=[]
        self.my_id = my_id
        self.result_t = result_topic
        self.producer = model_utils.get_kafka_producer('predict-on-stream-1')
        self.consumer = model_utils.get_kafka_consumer(group_id,request_topic,list_of_partitions,'latest')


    def __del__(self):
        print('closing')
        # self.consumer.close()
        self.consumer.commit()
        self.consumer.close()
        self.producer.flush()
        self.producer.close()


    def execute_model(self):

        if(len(self.msg_list)>0):
            print('executing model for req count ' + str(len(self.msg_list)))
            results = ray.get([send_query.remote(d)  for d in  self.msg_list])
            for r in results:
                r = json.loads(r)
                v = json.dumps(r).encode('utf-8')
                k = str(r["message_id"])
                self.producer.produce(self.result_t, value=v, key=k)
            self.producer.flush()
            self.consumer.commit()
            self.msg_list = []
        else:
            print('No messages on the topic. Nothing to execute')

    def run(self):
        ### Set up model, metric, and starting timestamp for this model instance ###
        try:
            i = 1
            while (True):
                msg = self.consumer.poll(timeout=5.0)
                if msg is None:
                    #print('Invoking on timeout')
                    #self.execute_model()
                    continue
                else:
                    if msg.error():
                        print('Error consuming messages')
                        #self.execute_model()
                        if msg.error().code() == KafkaError._PARTITION_EOF:
                            # End of partition event
                            sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                             (msg.topic(), msg.partition(), msg.offset()))
                        elif msg.error():
                            raise KafkaException(msg.error())
                    else:
                        message = loads(msg.value().decode("utf-8"))
                        self.msg_list.append(message)
                        #y_hat = model.score_one(x)  # model.predict_one(x) # make a prediction
                        if (len(self.msg_list) % 100 == 0):
                            print('Invoking on max msg limit ')
                            self.execute_model()
        finally:
            pass



if __name__ == '__main__':
    list_of_partitions = [0,1,2,3,4,5]
    src_topic = 'cc_events'
    dest_topic = 'cc_prediction_truth_join'
    grp_id = 'cc-grp-1'

    process_cc_events('cc_events',list_of_partitions,'cc_prediction_truth_join','cc-grp-1')
    #results = ray.get([process_cc_events.remote('cc_events',[x],'cc_prediction_truth_join','cc-grp-1') for x in range(6)])
    #print(results)


    #time.sleep(10000)