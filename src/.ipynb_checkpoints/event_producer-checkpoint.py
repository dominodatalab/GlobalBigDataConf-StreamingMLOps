import os
import random

import certifi
from confluent_kafka import Producer, SerializingProducer
import csv
import time
import json
import model_utils
EVENT_TOPIC='cc_events'
if __name__ == '__main__':
    topic = EVENT_TOPIC
    random.seed(1000)
    producer = model_utils.get_kafka_producer('test-sw-1')


    original_ds_file = model_utils.get_original_ds_file()

    i = 0
    while(True):
        with open(original_ds_file, encoding='utf-8') as csvf:
            csvReader = csv.DictReader(csvf)
            #"Time", "V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8", "V9", "V10", "V11", "V12", "V13", "V14", "V15", "V16", "V17", "V18", "V19",
            # "V20", "V21", "V22", "V23", "V24", "V25", "V26", "V27", "V28", "Amount", "Class"
            # Convert each row into a dictionary
            # and add it to data

            for rows in csvReader:
                account_number = random.randrange(1000000, 2000000)
                i = i + 1
                t = time.time()
                rows['account_number'] =account_number
                rows['Time'] = t
                rows['message_id'] = i
                rows['ingest_ts'] = t


                k = str(i);
                v = json.dumps(rows).encode('utf-8')

                producer.produce(topic, value=v, key=k)

                if(i%100==0):
                    print('Flushing. Processed records ' + str(i))
                    producer.flush()
                    #time.sleep(10)
                producer.flush()

    producer.flush()
    producer.close()
    print('done')

