mkdir /mnt/data/$(DOMINO_PROJECT_NAME)/$(DOMINO_STARTING_USERNAME)
mkdir /mnt/data/$(DOMINO_PROJECT_NAME)/$(DOMINO_STARTING_USERNAME)config
mkdir /mnt/data/$(DOMINO_PROJECT_NAME)/$(DOMINO_STARTING_USERNAME)models
mkdir /mnt/data/$(DOMINO_PROJECT_NAME)/$(DOMINO_STARTING_USERNAME)/raw_datasets
mkdir /mnt/data/$(DOMINO_PROJECT_NAME)/$(DOMINO_STARTING_USERNAME)/training_datasets
mkdir /mnt/data/$(DOMINO_PROJECT_NAME)/$(DOMINO_STARTING_USERNAME)/inf_truth_join_folder


cp ./config/model_metadata_initial.json /mnt/data/$(DOMINO_PROJECT_NAME)/$(DOMINO_STARTING_USERNAME)/config/model_metadata.json