import json
import requests
from collections import namedtuple

# api is a basic representation of an API. It has an API endpoint and key.
class api:
  def __init__(self, endpoint, key):
    self.endpoint = endpoint
    self.key = key

# authenticate_api is the authentication API. It is used for user
# authentication. The API key seems to be global and not user specific. It
# accepts POST requests.
authenticate_api = api(
  endpoint="https://www.transperth.wa.gov.au/DesktopModules/JJPApiService/API/JJPApi",
  key="CB7EF0B64DEF4641A6054F4685489D8D")

# journey_planner_api is the JourneyPlanner API. It is used to request
# information about stops and trips. It accepts GET requests.
journey_planner_api = api(
  endpoint="https://au-journeyplanner.silverrail.io/journeyplannerservice/v2/REST/DataSets/PerthRestricted",
  key=None)

# journey_planner_realtime_api is the JourneyPlanner realtime API. It is used
# to request potentially realtime information about stops and trips. It accepts
# POST requests.
journey_planner_realtime_api = api(
  endpoint="https://realtime.transperth.info/SJP",
  key=None)

# user_api is the User API. It is the same API as the authentication API in
# terms of its endpoint and API key.
user_api = api(
  endpoint="https://www.transperth.wa.gov.au/DesktopModules/JJPApiService/API/JJPApi",
  key="CB7EF0B64DEF4641A6054F4685489D8D")

# device_id is a version 4 (random) universally unique identifier (UUID) used
# for device authentication. It doesn't seem to be generated through the API,
# rather it seems to be generated on the device itself. You can get your device
# ID empirically using a proxy server with the Transperth app. It's contained
# in the data of one of the first POST requests.
device_id = None

params_base = {
  "format": "json",
}

headers_base = {
  "Content-Type": "application/json"
}

# authenticate_with_device_id authenticates a device ID "d_id". On
# authentication success, the response contains the JourneyPlanner API key.
def authenticate_with_device_id(d_id):
  headers = headers_base
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
    params_base["ApiKey"] = journey_planner_api.key = r_json["jjpapikey"]
    device_id = r_json["deviceID"]
  return r

# fetch_stops_near_me returns transit stops relative to a position, "lat", and
# "long". The remaining request parameters: "max_distance", "max_stops", and
# "speed" specify constraints on these transit stops.
def fetch_stops_near_me(lat, long, max_distance=6500, max_stops=15, speed=4):
  headers = headers_base
  params = params_base
  params |= {
    "maximumWalkDistanceInMetres": max_distance,
    "maximumStopsToReturn": max_stops,
    "walkSpeed": speed,
    "GeoCoordinate": f"{lat}, {long}"
  }
  return requests.get(f"{journey_planner_api.endpoint}/NearbyTransitStops", headers=headers, params=params)

# check_available_reference_data returns reference data used by the app. On
# success, the response contains several AWS URLs to structured reference data
# for landmarks, routes, route timetable groups, service providers, transit
# stops, transport modes, park and rides, data set information, trip
# attributes, products, and vehicle categories. Some structured data may be
# empty.
def check_available_reference_data():
  headers = headers_base
  params = params_base
  return requests.get(f"{journey_planner_api.endpoint}/AvailableReferenceData", headers=headers, params=params)
