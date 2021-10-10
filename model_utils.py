import os
import json
import pickle


def initialize_artifact_destination(folder,file):
    if(not os.path.isdir(folder)):
        os.makedirs(folder)
    if(os.path.isfile(file)):
        os.remove(file)

def get_model_metadata():
    f = open(os.path.join(os.getcwd(),'config','model_metadata.json'))
    data = json.load(f)
    return data


def get_current_model_version():
    f = open(os.path.join(os.getcwd(),'config','model_metadata.json'))
    data = json.load(f)
    return data['current_version']

def get_next_model_version():
    f = open(os.path.join(os.getcwd(),'config','model_metadata.json'))
    data = json.load(f)
    return data['current_version'] + 1

def increment_model_version():
    path = os.path.join(os.getcwd(),'config','model_metadata.json')
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
    base_folder = model_metadata['base_folder']
    if (base_folder==''):
        base_folder = os.getcwd()
    models_path = os.path.join(base_folder,'models','v'+str(version),'model.pkl')
    with (open(models_path, "rb")) as f:
        return pickle.load(f)

def get_features(data):
    features = {'V'+str(i):float(data['V'+str(i)]) for i in range(1,29)}
    features['Amount'] = float(data['Amount'])
    return features

def get_inf_truth_join_folder():
    config = get_model_metadata()
    return os.path.join(config['base_folder'],config['inf_truth_join_folder'])

if __name__ == '__main__':
    i = get_current_model_version()
    print(get_model())
