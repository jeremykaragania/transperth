import json
import requests
from collections import namedtuple

class api:
  def __init__(self, endpoint, key):
    self.endpoint = endpoint
    self.key = key

authenticate_api = api(
  endpoint="https://www.transperth.wa.gov.au/DesktopModules/JJPApiService/API/JJPApi",
  key="CB7EF0B64DEF4641A6054F4685489D8D")

journey_planner_api = api(
  endpoint="https://au-journeyplanner.silverrail.io/journeyplannerservice/v2/REST/DataSets/PerthRestricted",
  key=None)

journey_planner_realtime_api = api(
  endpoint="https://realtime.transperth.info/SJP",
  key=None)

user_api = api(
  endpoint="https://www.transperth.wa.gov.au/DesktopModules/JJPApiService/API/JJPApi",
  key="CB7EF0B64DEF4641A6054F4685489D8D")

device_id = None

def authenticate_with_device_id(d_id):
  headers = {
    "Content-Type": "application/json"
  }
  data = {
    "AppApiKey": authenticate_api.key,
    "authMode": 1,
    "Device": {
      "DeviceId": d_id,
      }
  }
  r = requests.post(f"{authenticate_api.endpoint}/authenticate", headers=headers, data=json.dumps(data))
  if r.status_code == 200:
    r_json = r.json()
    journey_planner_api.key = r_json["jjpapikey"]
    device_id = r_json["deviceID"]
  return r
