import model_utils
import random
import os


def predict(msg):
    version = msg["version"]
    model = model_utils.get_model_local(version=version)
    features = model_utils.get_features(msg)
    msg["result"] = str(model.score_one(features))
    return msg


if __name__ == '__main__':
    msg={'version':0}
    msg = {'V'+str(i):float(random.random()) for i in range(1,29)}
    msg['Amount'] =1000.0
    #msg['version'] = 0
