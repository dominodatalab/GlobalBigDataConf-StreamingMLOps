import os
import model_utils
import fileinput

def create_ds():
    inf_truth_join_folder = model_utils.get_inf_truth_join_folder()
    files = os.listdir(inf_truth_join_folder)
    inp_files = []
    for f in files:
        inp_files.append(os.path.join(inf_truth_join_folder,f))
    
    
    fldr = model_utils.create_if_not_exists_dataset_next_version_folder()
    ds_file = os.path.join(fldr,model_utils.get_model_metadata()['dataset_file'])
    if(not os.path.isfile(ds_file)):
        with open(os.path.join(fldr,model_utils.get_model_metadata()['dataset_file']), 'w') as ds_file:
            with fileinput.input(files=inp_files) as inputs:
                for line in inputs:
                    ds_file.write(line)
        for f in inp_files:
            os.remove(f)

if __name__ == '__main__':
    create_ds()