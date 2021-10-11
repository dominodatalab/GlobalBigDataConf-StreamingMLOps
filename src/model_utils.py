import os
import json
import pickle

import certifi
from confluent_kafka import TopicPartition, Consumer, Producer
from river import metrics
from river import anomaly
from river import compose
from river import preprocessing
BASE_FOLDER_ENV_NAME='STREAMING_CONFIG_BASE_FOLDER'

def initialize_artifact_destination(folder,file):
    if(not os.path.isdir(folder)):
        os.makedirs(folder)
    if(os.path.isfile(file)):
        os.remove(file)

def get_model_metadata():
    f = open(os.path.join(get_base_folder(), 'config', 'model_metadata.json'))
    data = json.load(f)
    return data

def get_base_folder():
    if(os.getenv('DOMINO_PROJECT_NAME') is not None):
        return '/mnt/data/'+os.getenv('DOMINO_PROJECT_NAME')+"/"
    else:
        return os.getcwd() + "/../"


def get_current_model_version():
    return get_model_metadata()['current_version']

def get_raw_dataset_file():
    original_ds_file = os.path.join(get_base_folder(), 'raw_dataset', 'creditcard.csv')
    return original_ds_file

def create_if_not_exists_dataset_next_version_folder():
    config = get_model_metadata()
    fldr = os.path.join(get_base_folder(), config['training_datasets_folder'],'v'+str(config['current_version']+1))
    if (not os.path.isdir(fldr)):
        os.makedirs(fldr)
    return fldr

def create_if_not_exists_dataset_version_folder(version):
    config = get_model_metadata()
    fldr = os.path.join(get_base_folder(), config['training_datasets_folder'],'v'+str(version))
    if (not os.path.isdir(fldr)):
        os.makedirs(fldr)
    return fldr

def get_next_model_version():
    f = open(os.path.join(get_base_folder(), 'config', 'model_metadata.json'))
    data = json.load(f)
    return data['current_version'] + 1

def increment_model_version():
    path = os.path.join(get_base_folder(), 'config', 'model_metadata.json')
    data={}
    with open(path,'r') as f:
        data = json.load(f)
    with open(path, 'w') as f:
        data['current_version'] = data['current_version'] + 1
        json.dump(data,f)
    return data['current_version']

def get_model(version=None):
    model_metadata = get_model_metadata()
    version = 0
    if(version==None):
        version = get_current_model_version()
    if(version==-1):
        model = compose.Pipeline(
            preprocessing.MinMaxScaler(),
            anomaly.HalfSpaceTrees(seed=42)
        )  # tree.HoeffdingTreeClassifier(max_depth=10)
        return model
    else:
        base_folder = get_base_folder()
        if (base_folder==''):
            base_folder = os.getcwd()
        models_path = os.path.join(base_folder, 'models', 'v' + str(version), 'model.pkl')
        with (open(models_path, "rb")) as f:
            return pickle.load(f)

def get_metric(name,version=None):

    if(version==None):
        version = get_current_model_version()
    print(version)
    if(version==-1):
        if(name=='ROCAUC'):
            metric = metrics.ROCAUC()
            return metric
        else:
            ##Default metric
            metric = metrics.ROCAUC()
            return metric
    else:
        base_folder = get_base_folder()
        if (base_folder==''):
            base_folder = os.getcwd()
        metrics_path = os.path.join(base_folder, 'models', 'v' + str(version),name+'.pkl')
        with (open(metrics_path, "rb")) as f:
            return pickle.load(f)

def get_features(data):
    features = {'V'+str(i):float(data['V'+str(i)]) for i in range(1,29)}
    features['Amount'] = float(data['Amount'])
    return features

def get_inf_truth_join_folder():
    config = get_model_metadata()
    return os.path.join(get_base_folder(),config['inf_truth_join_folder'])

def get_kafka_consumer(group_id, topic, partitions,offset='latest'):
    json_file_path = os.path.join(get_base_folder(), "config/credentials.json")
    with open(json_file_path, 'r') as j:
        creds = json.loads(j.read())
    tls = []
    for p in partitions:
        tls.append(TopicPartition(topic, p))
    conf = {'bootstrap.servers': creds['BOOTSTRAP_SERVERS'],
            'sasl.mechanism': 'PLAIN',
            'security.protocol': 'SASL_SSL',
            'ssl.ca.location': certifi.where(),
            'sasl.username': creds['CLUSTER_API_KEY'],
            'sasl.password': creds['CLUSTER_API_SECRET'],
            'group.id': group_id,
            'enable.auto.commit': False,
            'auto.offset.reset': offset}
    consumer = Consumer(conf)
    consumer.assign(tls)
    return consumer


def get_kafka_producer(client_id):
    json_file_path = os.path.join(get_base_folder(), "config/credentials.json")
    with open(json_file_path, 'r') as j:
        creds = json.loads(j.read())
    conf = {'bootstrap.servers': creds['BOOTSTRAP_SERVERS'],
            'sasl.mechanism': 'PLAIN',
            'security.protocol': 'SASL_SSL',
            'ssl.ca.location': certifi.where(),
            'sasl.username': creds['CLUSTER_API_KEY'],
            'sasl.password': creds['CLUSTER_API_SECRET'],
            'client.id': client_id}
    producer = Producer(conf)
    return producer


def get_original_ds_file():
    return os.path.join(get_base_folder(), 'raw_dataset', 'creditcard.csv')

if __name__ == '__main__':
    print(get_base_folder())
