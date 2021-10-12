from src import model_utils
import random
import os
import boto3

def predict(msg):
    os.environ["DOMINO_S3_BUCKET"] = msg["DOMINO_S3_BUCKET"]
    os.environ["DOMINO_PROJECT_NAME"] = msg["MODEL_REGISTRY_ROOT"]
    os.environ["DOMINO_STARTING_USERNAME"] = msg["MODEL_REGISTRY_USER"]

    objs = boto3.client.list_objects(Bucket=msg["DOMINO_S3_BUCKET"])
    while 'Contents' in objs.keys():
        objs_contents = objs['Contents']
        for i in range(len(objs_contents)):
            filename = objs_contents[i]['Key']

    with (open(models_path, "rb")) as f:
        return pickle.load(f)

    features = model_utils.get_features(msg)
    if ('version' not in msg):
        msg["version"] = model_utils.get_current_model_version()
    version = msg["version"]
    model = model_utils.get_model(version=version)
    msg["result"] = str(model.score_one(features))
    return msg

if __name__ == '__main__':
    msg={'version':0}
    msg = {'V'+str(i):float(random.random()) for i in range(1,29)}
    msg['Amount'] =1000.0
    #msg['version'] = 0
    print(predict(msg))