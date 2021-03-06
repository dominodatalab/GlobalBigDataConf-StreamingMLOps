import ray
import requests
from ray import serve
import model_utils


@serve.deployment
def hello(request):
    name = request.query_params["name"]
    return f"Hello {name}!"


ray.init(num_cpus=1)
serve.start()
hello.deploy()
# Query our endpoint over HTTP.
response = requests.get("http://127.0.0.1:8000/hello?name=serve").text
print(response)

headers = {"content-type":"application/json"}
d = {}
for i in range(1,29):
    d['V'+str(i)]=0.0
d['Amount']=0
response = requests.post("http://127.0.0.1:8000/ModelServing?version=0",json=d,headers=headers).text
print(response)
