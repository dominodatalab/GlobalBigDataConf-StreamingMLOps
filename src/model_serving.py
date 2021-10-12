import random

import ray
from ray import serve
import model_utils
import time


@serve.deployment(route_prefix="/predict")
class ModelServing:
  def __init__(self,check_for_model_update_frequency=10):
      self.model = model_utils.get_model()
      self.consumer = model_utils.get_kafka_consumer('grp-'+str(time.time()), 'cc_control', [0],offset='earliest')
      self.last_checked = time.time()
      self.check_for_model_update_frequency = check_for_model_update_frequency

  def update_model_if_new(self):
      # only check every 10 seconds
      current_time = time.time()
      if(current_time-self.last_checked)< self.check_for_model_update_frequency:
          return
      msg = self.consumer.poll(timeout=1.0)
      if msg is None:
          return
      if msg.error():
          #Need better error handling for real world use cases.
          print('Error consuming control topic in model serving')
          return
      else:
          print('Recieve model update')
          #Simply update the model
          self.model = model_utils.get_model()

  @serve.batch(max_batch_size=100)
  async def handle_batch(self, requests):
      self.update_model_if_new()
      results = []
      for request in requests:
          body = await request.json()
          features = model_utils.get_features(body)
          if ('version' in body):
              version = body["version"]
              self.model = model_utils.get_model(version=version)
              body["result"] = str(self.model.score_one(features))
          else:
              body["version"] = model_utils.get_current_model_version()
              body["result"] = str(self.model.score_one(features))
          event_time = int(body["ingest_ts"])
          predict_time = time.time()
          body["prediction_ts"] = predict_time
          body["prediction_latency"] = predict_time-event_time
          results.append(body)
      return results

  async def __call__(self, request):
    return await self.handle_batch(request)


ray.init(num_cpus=2)
serve.start()
ModelServing.deploy()
print('Now waiting')
time.sleep(10000)


