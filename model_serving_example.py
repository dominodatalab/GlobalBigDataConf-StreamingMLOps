import ray
import requests
from ray import serve
import model_utils
import time



@serve.deployment
def hello(request):
    name = request.query_params["name"]
    return f"Hello {name}!"

@serve.deployment
async def predict(request):
    body = await request.json()
    if('version' in request.query_params):
        version = request.query_params["version"]
        model = model_utils.get_model(version=version)
        return model.score_one(body);
    else:
        model = model_utils.get_model()
        result = model.score_one(body)
        model.score_one(body)


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
