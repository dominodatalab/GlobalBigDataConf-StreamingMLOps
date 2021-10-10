import ray
from ray import serve
import model_utils
import time




@serve.deployment(route_prefix="/predict")
class ModelServing:
  def __init__(self):
      self.model = model_utils.get_model()

  @serve.batch(max_batch_size=100)
  async def handle_batch(self, requests):
      results = []
      for request in requests:
          body = await request.json()
          features = model_utils.get_features(body)
          if ('version' in body):
              version = body["version"]
              model = model_utils.get_model(version=version)
              body["Result"] = str(self.model.score_one(features))
              results.append(body)
          else:
              body["version"] = model_utils.get_current_model_version()
              body["Result"] = str(self.model.score_one(features))
          event_time = int(body["Time"])
          predict_time = time.time()
          body["PredictionTime"] = predict_time
          body["PredictionLatency"] = predict_time-event_time
          results.append(body)
      return results

  async def __call__(self, request):
    return await self.handle_batch(request)


ray.init(num_cpus=8)
serve.start()
ModelServing.deploy()
print('Now waiting')
time.sleep(10000)


