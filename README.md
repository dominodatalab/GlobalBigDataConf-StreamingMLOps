##Introduction
This repo was created as a part of my presentation at the Global Artificial Intelligence Virtual Conference
The presentation is available in this repo at [docs/StreamingMLOps.pdf](docs/StreamingMLOps.pdf)

The use-case is credit card fraud detections based on an Unsupervised Learning based Anomaly Detection algorithm
[Half Space Trees](https://www.ijcai.org/Proceedings/11/Papers/254.pdf)

Additional context around the ML methodology can be found at this [link](https://github.com/dominodatalab/streaming-online-learning) 

### Versions
Python 3.8
Check for library dependencies in the ./requirements.txt file
```
river~=0.7.1
ray~=1.6.0
certifi~=2021.5.30
requests~=2.25.1
numpy~=1.21.2
```
### Installation 

1. Go to the project root folder and run
`python src/install.sh` .This downloads the raw credit card fraud dataset from [source](https://maxhalford.github.io/files/datasets/creditcardfraud.zip) location
2. The root location of the Model Registry is project folder
3. Initialize it by running the following command `cp config/model_metadata_initial.json config/model_metadata.json`
4. Download and start [Confluent Kafka](https://www.confluent.io/installation). You could another flavor by your `src/model_utils.py` will need to change the config settings to be compatible. I used the $200 free credits from [Confluent Cloud](https://confluent.cloud/). If you do that run `cp src/sample_credentials.json src/credentials.json` and update the three entries for bootstrap servers, username and secret
5. Create three [topics](./images/ConfluentKafka.png)
   1. cc_events (Raw transaction topic) with 6 partitions
   2. cc_prediction_truth_join (Where the predictions and ground truth joins) with 6 partitions
   3. cc_control (to send model update events) with 1 partition

### Run the application
1. First create the initial version 0 dataset `python create_training_dataset_v0.py`. Check the folder `./training_datasets/v0` for the file `ds.csv`. Also check the `config/model_metadata.json` file to verify that the current version of the model has changed from -1 to 0
2. Start the model serving layer. We use [Ray Serving](https://docs.ray.io/en/latest/serve/index.html) with batching for improved throughput
3. Start Event Producer. This is the external entity which publishes the events to Kafka topics `cc_events`
`python src/event_producer.py` . You should [see](./images/cc_events_snapshot.png) the events in the `cc_events` topic. For convenience we have assumed that this topic receives the engineered features. Normally there will be a robust feature engineering pipeline consuming the raw events and publishing engineered features to this topic   
4. Start the inference generator. This listens to the `cc_events` topic and publishes the inferences to the topic `cc_prediction_truth_join`. Again we have conveniently published by the inference and the prediction to this topic. Typically they will need to be joined because the ground truth arrives later. We start two of these instances listening to separate kakfa partitions 
`python src/predict_on_a_stream.py 0 1 2` and `python src/predict_on_a_stream.py 3 4 5` 
5. Now start the `python inference_and_truth_join_consumer.py 5` where `0` is an <id> we provide this consumer. We can have upto 6 consumers (6 paritions on the source topic) like this. Give each a unique id.   which writes the results to the shared folder in the model_registry setup `inf_truth_join_folder`
6. Now you can periodically re-run the model training on schedule or manually as `python model_training.py`. This will consolidate all the files from the `inf_truth_join_folder` in a versioned (current_version+1) folder inside `training_datasets` folder and the the model training will create a new version of the model and metrics
7. Everytime the model version is incremented a message is sent to the `cc_control` topic and the REST endpoints update the underlying model they are serving
8. You can also test the endpoint using any REST client
```

import requests
data = {
			"V1": "-0.657616087911944",
			"V2": "1.03537183836808",
			"V3": "2.29914192080499",
			"V4": "2.92166956184269",
			"V5": "-0.0947451969010652",
			"V6": "0.895020410627401",
			"V7": "0.26712551321791",
			"V8": "0.10211863863235",
			"V9": "-0.403654482114575",
			"V10": "1.17958694969639",
			"V11": "-0.578225593091631",
			"V12": "-0.0116635307789695",
			"V13": "0.525398852635495",
			"V14": "-0.697505316529036",
			"V15": "0.528394041391276",
			"V16": "-0.710354526236512",
			"V17": "0.391328780674197",
			"V18": "-0.312695021187024",
			"V19": "0.508641970173187",
			"V20": "0.435907790459771",
			"V21": "0.0775634904512596",
			"V22": "0.910979503913737",
			"V23": "-0.0666810861509485",
			"V24": "0.130745821748665",
			"V25": "-0.286511940980507",
			"V26": "0.355409652284987",
			"V27": "0.425114064984828",
			"V28": "0.0439624237623181",
			"Amount": "33.62",
            "ingest_ts": 1,
            "version": 20

}
response = requests.post('http://127.0.0.1:8000/predict', json=data)
print(response.status_code)
print(response.text)
```
