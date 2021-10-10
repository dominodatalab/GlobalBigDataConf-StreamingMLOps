import ray
import requests
import time


@ray.remote
def send_query(json):
    headers = {"content-type": "application/json"}
    resp = requests.post("http://127.0.0.1:8000/predict",json=json,headers=headers).text
    return resp


d = {}
for i in range(1,29):
    d['V'+str(i)]=0.0
d['Amount']=0


ray.init()
st = time.time()
results = ray.get([send_query.remote(d) for i in range(1000)])
end = time.time()
print('Total time ' + str(end-st))
print(len(results))

print('example result ' + results[0])