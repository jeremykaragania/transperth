# Transperth
A Transperth app web API.

## Installation
```bash
git clone https://github.com/jeremykaragania/transperth.git
python3 -m pip install -e transperth
```

## Usage
First import the module:
```py
>>> import transperth
```

### Authentication
The JourneyPlanner and User APIs require authentication to access.
Authentication will require your device ID which can be found empirically with a
proxy server and the Transperth app.

You can authenticate with your device ID:
```py
>>> transperth.authenticate_with_device_id("YOUR_DEVICE_ID")
```
Then, you can optionally authenticate with your Transperth account to access the User API:
```py
>>> transperth.authenticate_with_user("YOUR_EMAIL", "YOUR_PASSWORD")
```

### Routes
A route can be looked up from a route code:
```py
>>> route_code = 950
>>> r = transperth.fetch_route_lookup(route_code)
>>> routes = r.json()["Routes"]
>>> route = next(route for route in routes if int(route["Code"]) == route_code)
>>> route
{'RouteUid': 'PerthRestricted:PAT-MOR-3142',
 'ServiceProviderUid': 'PerthRestricted:PAT-MOR',
 'TransportMode': 'Bus',
 'TransportModeUid': '3',
 'RouteTimetableGroupId': 'PerthRestricted:RTG_120',
 'Code': '950',
 'Name': '',
 'Colour': '009645',
 'TextColour': 'FFFFFF',
 'RouteSourceId': 'PAT-MOR-3142'}
```

Each route has an ID:
```py
>>> route_id = route["RouteUid"]
```

You can fetch a route's timetable within a date range:
```py
>>> from datetime import date
>>> today = date.today().isoformat()
>>> r = transperth.fetch_route_timetable(route_id, begin_date=today, end_date=today)
>>> timetable = r.json()
```

### Trips
A route's timetable contains trip information:
```py
>>> trips = timetable["TimetableTrips"]
>>> trip = trips[0]
```

And like a route, each trip also has an ID:
```py
>>> trip_id = trip["TripUid"]
>>> trip_id
'PerthRestricted:6184804'
```

A trip contains sorted stop information:
```py
>>> stops = trip["TransitStops"]
>>> stops
[...,
 {'__type': 'TransitStop:http://www.jeppesen.com/journeyplanner',
  'DataSet': 'PerthRestricted',
  'StopUid': 'PerthRestricted:11504',
  'Description': 'Hospital Av Qeii Medical Centre Cat Id 115',
  'Position': '-31.967328, 115.816768',
  'Code': '11504',
  'Zone': '1',
  'SupportedModes': 'Bus',
  'SupportedModeUids': '3',
  'Routes': 'PerthRestricted:PAT-CIR-3593;PerthRestricted:PAT-MOR-3142;PerthRestricted:PAT-MOR-4246;PerthRestricted:SCT-CIR-3593;PerthRestricted:SCT-PCA-4066;PerthRestricted:SWA-CIR-3593;PerthRestricted:SWA-CLA-1644;PerthRestricted:SWA-CLA-1645;PerthRestricted:SWA-CLA-1657;PerthRestricted:SWA-CLA-1658;PerthRestricted:SWA-CLA-2982;PerthRestricted:SWA-CLA-3865;PerthRestricted:SWA-CLA-4319'},
 ...]
```

You can then find the correlating trip's stop timing information:
```py
>>> stop_timing = trip["TripStopTimings"]
>>> stop_timing
[...,
 {'CanBoard': True,
  'CanAlight': False,
  'ArrivalTime': '',
  'DepartTime': '04:25',
  'IsTimingPoint': True},
 ...]
```

Additional trip information can be fetched by trip ID:
```py
>>> trip_ids = [trip["TripUid"] for trip in trips]
>>> r = transperth.fetch_timetable_data(today, trip_ids)
>>> trip_info = r.json()["GetTripInfosResult"]
>>> trip_info
[...,
 {'ConnectionType': 'None',
  'Interruptions': None,
  'Status': 'NotFound',
  'TripId': 6184857},
 ...]
```

From this additional information, you can find all the trips which are live:
```py
>>> live_trips = [info for info in trip_info if info["Status"] == "Live"]
```

For a live trip, you can fetch its realtime information:
```py
>>> live_trip_id = live_trips[0]["TripId"]
>>> r = transperth.fetch_realtime_trip(live_trip_id, today)
>>> realtime_info = r.json()["Summary"]["RealTimeInfo"]
>>> realtime_info
{'CurrentPosition': '-31.9772415161133 115.813941955566',
 'LastUpdated': '2025-11-04T11:47',
 'CurrentBearing': 97,
 'VehicleId': 'PAT-MOR-3106',
 'FleetNumber': '3106'}
```

## License
[MIT](LICENSE)
