#Use numpy 1.21.2 pip3 install --upgrade numpy
from river import tree, metrics
import os
import csv
from river import anomaly
from river import compose
from river import preprocessing
import pickle
import model_utils
import json
if __name__ == '__main__':
    metric = metrics.ROCAUC()
    next_version=model_utils.get_next_model_version()
    model = compose.Pipeline(
        preprocessing.MinMaxScaler(),
        anomaly.HalfSpaceTrees(seed=42)
    )  # tree.HoeffdingTreeClassifier(max_depth=10)
    ds_file = os.path.join(os.getcwd(), 'training_datasets', 'v0', 'ds.csv')
    model_folder = os.path.join(os.getcwd(), 'models', 'v0')
    model_file = os.path.join(os.getcwd(), 'models', 'v0','model.pkl')
    model_utils.initialize_artifact_destination(model_folder,model_file)

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
            if(i%1000==0):
                print(str(i) + "=" + str(metric.get()))
    print(str(metric.get()))
    pickle.dump(model, open(model_file, "wb"))
    model_utils.increment_model_version()