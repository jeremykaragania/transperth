from base64 import b64encode
from datetime import datetime
from hashlib import sha1
import json
from random import randint
import requests

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

# realtime_api is the realtime API. It is used to request potentially realtime
# information about stops and trips. It accepts POST requests.
realtime_api = api(
  endpoint="https://realtime.transperth.info",
  key="8acb640c-36cd-42f5-be67-109492f1b093")

# user_api is the user API. It is the same API as the authentication API in
# terms of its endpoint and API key.
user_api = api(
  endpoint="https://www.transperth.wa.gov.au/DesktopModules/JJPApiService/API/JJPApi",
  key="CB7EF0B64DEF4641A6054F4685489D8D")

device_id = None

headers_base = {
  "Content-Type": "application/json"
}

params_base = {
  "format": "json",
  "ApiKey": None
}

# data_base["DeviceId"] is generated using getUniqueId from the
# react-native-device-info package. The method in which it is generated is OS
# specific. You can get your device ID empirically using a proxy server with
# the Transperth app. It's contained in the data of one of the first POST
# requests.
data_base = {
  "format": "json",
  "AppApiKey": authenticate_api.key,
  "authMode": 1,
  "Device": {
    "DeviceId": None,
    },
  "ApiKey": journey_planner_api.key,
  "Email": None
}

# authenticate_with_user authenticates a user with an email address and a
# password. On authentication success, the response contains an access token
# for the user API.
def authenticate_with_user(email, password):
  headers = dict(headers_base)
  data = dict(data_base)
  data |= {
    "Email": email,
    "Password": password
  }
  r = requests.post(f"{authenticate_api.endpoint}/Authenticate", headers=headers, data=json.dumps(data))
  r_json = r.json()
  data_base["AuthToken"] = r_json["hash"]
  data_base["Email"] = email
  return r

# fetch_transaction_history returns "max_transactions" past transactions of a
# SmartRider, specified by its number "psn", between "from_date" until
# "to_date". The SmartRider must be connected to the user's account.
#
# Each transaction contains a transaction date and time; transaction number;
# the type of transaction; tag on location; bus number if applicable;
# travel zone; transaction amount; remaining balance; and some additional
# information.
def fetch_transaction_history(psn, from_date, to_date, max_transactions=500):
  headers = dict(headers_base)
  data = dict(data_base)
  data |= {
    "PSN": psn,
    "fromDate": from_date,
    "toDate": to_date,
    "tPageNumber": 0,
    "tPageSize": max_transactions,
    "mode": 4
  }
  return requests.post(f"{authenticate_api.endpoint}/MyAccountGetSmartRiderDetails", headers=headers, data=json.dumps(data))

# get_smartrider_list returns a list of SmartRiders linked to the user's
# account.
#
# Each SmartRider contains its link information and its status. The link
# information contains the card's number; account name; if it is the default
# card; and if it the card is hidden.
def get_smartrider_list():
  headers = dict(headers_base)
  data = dict(data_base)
  return requests.post(f"{authenticate_api.endpoint}/MyAccountGetSmartRiderList", headers=headers, data=json.dumps(data))

# authenticate_with_device_id authenticates a device ID "d_id". On
# authentication success, the response contains the JourneyPlanner API key.
def authenticate_with_device_id(d_id):
  global device_id
  headers = dict(headers_base)
  data = dict(data_base)
  data["Device"]["DeviceId"] = d_id
  r = requests.post(f"{authenticate_api.endpoint}/authenticate", headers=headers, data=json.dumps(data))
  r_json = r.json()
  params_base["ApiKey"] = data_base["ApiKey"] = journey_planner_api.key = r_json["jjpapikey"]
  data_base["Device"]["DeviceId"] = device_id = r_json["deviceID"]
  return r

# fetch_stops_near_me returns transit stops relative to a position, "lat", and
# "long". The remaining request parameters: "max_distance", "max_stops", and
# "speed" specify constraints on these transit stops.
def fetch_stops_near_me(lat, long, max_distance=6500, max_stops=15, speed=4):
  headers = dict(headers_base)
  params = dict(params_base)
  params |= {
    "maximumWalkDistanceInMetres": max_distance,
    "maximumStopsToReturn": max_stops,
    "walkSpeed": speed,
    "GeoCoordinate": f"{lat}, {long}"
  }
  return requests.get(f"{journey_planner_api.endpoint}/NearbyTransitStops", headers=headers, params=params)

# fetch_route_lookup returns route information from a search term "code" which
# is the code of the route. The response contains the information of routes
# where their code matches "code". It seems that the match function is not
# strict, "code" just has to be a subsequence. Notably, the information of a
# route contains its UID and transport mode.
def fetch_route_lookup(code):
  headers = dict(headers_base)
  params = dict(params_base)
  params |= {
    "SearchTerm": code
  }
  return requests.get(f"{journey_planner_api.endpoint}/Routes", headers=headers, params=params)

# fetch_route_timetable returns the timetable information of a route "route"
# between "begin_date" and "end_date", and may return some additional
# information depending on "return_notes". "route" is the UID of the route, and
# "begin_date" and "end_date" are in ISO 8601 format and are usually equal. The
# notable objects of the response include timetable trips and stop patterns.
# The timetable trips information is the bulk of the response and contains
# information for each trip on the route within the interval.
#
# Each trip contains the arrival and departure timings for each stop. The stop
# patterns information contains all of the possible stop arrangements the route
# can take, usually there are just two, one for each direction: backwards and
# forwards.
def fetch_route_timetable(route, begin_date, end_date, return_notes=True):
  headers = dict(headers_base)
  params = dict(params_base)
  params |= {
    "Route": route,
    "StartDate": begin_date,
    "EndDate": end_date,
    "ReturnNotes": return_notes
  }
  return requests.get(f"{journey_planner_api.endpoint}/Timetable", headers=headers, params=params)

# fetch_journeys returns possible journeys between an origin position "origin"
# and a destination position "destination" on a certain date and time "dt".
# The positions can be specified as a stop UID or a coordinate and "dt" is in
# ISO 8601 format: "YYYY-MM-DDTHH:MM". There are several other optional
# parameters. "return_notes" optionally returns additional information;
# "mapping_data_required" seems determines if the points which make up the
# journey are returned; "time_mode" changes how "dt" is interpreted;
# "max_changes" is the maximum number of changes on the trip; "max_distance" is
# the maximum walking distance in the journey, likely in meters;
# "transport_modes" is a semicolon separated list of modes of transport for the
# journey, "School Bus" is also accepted; "check_realtime" seems to have no
# effect; "speed" is the maximum walking speed in the journey, likely in
# kilometers per hour; and "max_journeys" seems to have an effect on the number
# of journeys returned though it isn't strict.
#
# Each journey contains an ID; departure and arrival time; additional
# information about the origin and destination; information about the legs of
# the journey; number of changes; and estimated carbon dioxide emissions.
# Supplementary location information is also returned to be referenced by a
# journey.
def fetch_journeys(origin, destination, dt, return_notes=True, mapping_data_required=True, time_mode="LeaveAfter", max_changes=2147483647, max_distance=2000, transport_modes="Bus;Rail;Ferry", check_realtime=False, speed=4, max_journeys=5):
  headers = headers_base
  params = dict(params_base)
  params |= {
    "ReturnNotes": return_notes,
    "mappingdatarequired": mapping_data_required,
    "To": origin,
    "From": destination,
    "TimeMode": time_mode,
    "MaxChanges": max_changes,
    "MaxWalkDistanceMetres": max_distance,
    "TransportModes": transport_modes,
    "Date": dt,
    "CheckRealTime": check_realtime,
    "WalkSpeed": speed,
    "MaxJourneys": max_journeys
  }
  return requests.get(f"{journey_planner_api.endpoint}/JourneyPlan", headers=headers, params=params)

# realtime_request makes a POST request to the realtime API with the data
# "data". Requests use a custom authentication scheme consisting of a username,
# nonce, and token. The username and nonce values were easy to deduce from
# request inspection. However, since the token is hashed, the correct value had
# to be deduced from a disassembly of the Transperth app.
def realtime_request(request_target, data):
  headers = dict(headers_base)
  now = datetime.now().strftime("%d%m%Y%H%M%S")
  nonce = b64encode("-".join(["".join([str(randint(0, 9)) for i in range(6)]), now]).encode())
  token = b64encode(sha1(f"TrAnSpErTh-{realtime_api.key.replace('-', '')}-{now}".encode()).digest())
  headers |= {
    "Authorization": f"Custom Username=PhoneApp, Nonce={nonce.decode()}, Token={token.decode()}"
  }
  return requests.post(f"{realtime_api.endpoint}{request_target}", headers=headers, data=data)

# check_available_reference_data returns reference data used by the app. On
# success, the response contains several AWS URLs to structured reference data
# for landmarks, routes, route timetable groups, service providers, transit
# stops, transport modes, park and rides, data set information, trip
# attributes, products, and vehicle categories. Some structured data may be
# empty.
def check_available_reference_data():
  headers = dict(headers_base)
  params = dict(params_base)
  return requests.get(f"{journey_planner_api.endpoint}/AvailableReferenceData", headers=headers, params=params)
