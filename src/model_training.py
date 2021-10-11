#Use numpy 1.21.2 pip3 install --upgrade numpy
from river import metrics
import os
import csv
from river import anomaly
from river import compose
from river import preprocessing
import pickle
import model_utils
from create_versioned_dataset import create_ds

def train_model():
    metric = model_utils.get_metric('ROCAUC')
    model = model_utils.get_model()
    next_version = model_utils.get_next_model_version()
    if(int(next_version)>0):
        create_ds()
    '''
    model = compose.Pipeline(
            preprocessing.MinMaxScaler(),
            anomaly.HalfSpaceTrees(seed=42)
        )  # tree.HoeffdingTreeClassifier(max_depth=10)
    '''
    ds_file = os.path.join(model_utils.get_base_folder(), 'training_datasets', 'v'+str(next_version), 'ds.csv')
    model_folder = os.path.join(model_utils.get_base_folder(), 'models', 'v'+str(next_version))
    model_file = os.path.join(model_utils.get_base_folder(), 'models', 'v'+str(next_version), 'model.pkl')
    metric_rocauc_file = os.path.join(model_utils.get_base_folder(), 'models', 'v' + str(next_version), 'rocauc.pkl')
    model_utils.initialize_artifact_destination(model_folder, model_file)

    with open(ds_file, 'r') as cc_file:
        csv_reader = csv.reader(cc_file)
        i=0
        for row in csv_reader:
            i=i+1
            x_vs = row[2:30]
            x = {'V'+str(i):float(x_vs[i]) for i in range(0, len(x_vs))}
            x['Amount'] = float(row[30])
            model = model.learn_one(x)
            y = row[31]
            metric.update(int(y),  round(model.score_one(x)))
            if(i%10000==0):
                print(str(i) + "=" + str(metric.get()))
    print(str(metric.get()))
    pickle.dump(model, open(model_file, "wb"))
    pickle.dump(metric, open(metric_rocauc_file, "wb"))
    model_utils.increment_model_version()
    topic = 'cc_control'
    producer = model_utils.get_kafka_producer('test-sw-1')
    current_version = str(model_utils.get_current_model_version())
    producer.produce(topic, value=current_version)
    producer.flush()
    print('Publish model update')
    #self.consumer = model_utils.get_kafka_consumer('model-training', request_topic, list_of_partitions, 'latest')
    #Produce message
    
if __name__ == '__main__':
    train_model()