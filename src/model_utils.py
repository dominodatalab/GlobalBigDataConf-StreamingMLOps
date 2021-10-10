import os
import json
import pickle
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
    if(os.getenv(BASE_FOLDER_ENV_NAME) is not None):
        return os.getenv(BASE_FOLDER_ENV_NAME)
    else:
        return "/Users/sameerwadkar/PycharmProjects/StreamingMLOps/"


def get_current_model_version():
    return get_model_metadata()['current_version']

def create_if_not_exists_dataset_next_version_folder():
    config = get_model_metadata()
    fldr = os.path.join(get_base_folder(), config['training_datasets_folder'],'v'+str(config['current_version']+1))
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

def get_features(data):
    features = {'V'+str(i):float(data['V'+str(i)]) for i in range(1,29)}
    features['Amount'] = float(data['Amount'])
    return features

def get_inf_truth_join_folder():
    config = get_model_metadata()
    return os.path.join(get_base_folder(),config['inf_truth_join_folder'])

if __name__ == '__main__':
    i = get_current_model_version()
    print(get_model())
