from src import model_utils
import random

def predict(msg):
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