echo $1
rm -rf $1
mkdir -R $1

mkdir $1/config
mkdir $1/models
mkdir $1raw_datasets
mkdir $1/training_datasets
mkdir $1/inf_truth_join_folder
cp /mnt/data/bigdata-conference-streamingml/sameer_wadkar/raw_dataset/creditcard.csv /mnt/data/my_model_registry/raw_datasets/

cp ./config/model_metadata_initial.json $1/config/model_metadata.json