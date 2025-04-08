# Transperth
A Transperth app web API.

## Installation
```bash
git clone https://github.com/jeremykaragania/transperth.git
python3 -m pip install -e transperth
```

## Usage
```py
>>> from datetime import date
>>> import transperth
>>> r = transperth.authenticate_with_device_id("YOUR_DEVICE_ID")
>>> r.json()["result"]
'AUTHOK'
>>> route_code = 950
>>> r = transperth.fetch_route_lookup(route_code)
>>> route = next(i for i in r.json()["Routes"] if int(i["Code"]) == route_code)
>>> route["RouteUid"]
'PerthRestricted:PAT-MOR-3142'
>>> today = date.today().isoformat()
>>> r = transperth.fetch_route_timetable(route["RouteUid"], begin_date=today, end_date=today)
>>> route_trips = r.json()["TimetableTrips"]
>>> len(route_trips)
185
>>> trip = route_trips[0]
>>> trip["TripStopTimings"]
[
  ...
  {
  'CanBoard': True,
  'CanAlight': True,
  'ArrivalTime': '04:33',
  'DepartTime': '04:33',
  'IsTimingPoint': True
  },
  ...
]
>>> trip["Headsign"]
'Qeii Medical Ctr'
```

## License
[MIT](LICENSE)
