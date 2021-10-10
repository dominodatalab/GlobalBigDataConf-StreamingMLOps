import csv
import os
import random
from collections import deque
if __name__ == '__main__':
    random.seed(1000)
    original_ds_file = os.path.join(os.getcwd(), '../raw_dataset', 'creditcard.csv')
    destination_ds_folder = os.path.join(os.getcwd(), '../training_datasets', 'v0')
    ds_file = os.path.join(os.getcwd(), '../training_datasets', 'v0', 'ds.csv')
    if(not os.path.isdir(destination_ds_folder)):
        os.makedirs(destination_ds_folder)
    if(os.path.isfile(ds_file)):
        os.remove(ds_file)
    with open(ds_file, 'w') as fp:
        pass


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