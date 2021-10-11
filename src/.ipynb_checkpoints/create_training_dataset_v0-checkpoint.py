import csv
import os
import random
from collections import deque
import model_utils

def create_v0_ds():
    random.seed(1000)
    original_ds_file = model_utils.get_raw_dataset_file()
    ds_fldr = model_utils.create_if_not_exists_dataset_version_folder(0)
    ds_file = os.path.join(ds_fldr,model_utils.get_model_metadata()['dataset_file'])


    with open(original_ds_file, 'r') as cc_file:
        csv_reader = csv.reader(cc_file)
        with open(ds_file, 'w') as ds_file:
            csv_writer = csv.writer(ds_file)
            next(csv_reader)
            for row in csv_reader:
                account_number = random.randrange(1000000,2000000)
                row = deque(row)
                row.appendleft(account_number)
                csv_writer.writerow(row)
                
if __name__ == '__main__':
    create_v0_ds()