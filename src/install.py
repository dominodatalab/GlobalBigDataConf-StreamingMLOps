import requests, zipfile, io, os
zip_file_url = 'https://maxhalford.github.io/files/datasets/creditcardfraud.zip'
r = requests.get(zip_file_url)
z = zipfile.ZipFile(io.BytesIO(r.content))
z.extractall(os.path.join(os.getcwd(),'raw_dataset'))