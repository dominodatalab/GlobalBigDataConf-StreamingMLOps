rm -rf /mnt/data/my_model_registry/
mkdir /mnt/data/my_model_registry/
mkdir /mnt/data/my_model_registry/config
mkdir /mnt/data/my_model_registry/models
mkdir /mnt/data/my_model_registry/raw_datasets
mkdir /mnt/data/my_model_registry/training_datasets
mkdir /mnt/data/my_model_registry/inf_truth_join_folder
cp /mnt/data/bigdata-conference-streamingml/sameer_wadkar/raw_dataset/creditcard.csv /mnt/data/my_model_registry/raw_datasets/

cp ./config/model_metadata_initial.json /mnt/data/my_model_registry/config/model_metadata.json