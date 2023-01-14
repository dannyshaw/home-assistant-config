import math
from .ptv import PTVClient, RouteType
from datetime import datetime
from dateutil import tz

DEV_ID = "3001254"
API_KEY = "192a6f53-999c-41a0-b3a2-608107093103"

client = PTVClient(DEV_ID, API_KEY)

MITCHELL_STREET = 20727

# routes
CITY_NTHLND_LATROBE_COMBINED = 3448
CITY_NORTHLAND = 8139  # City_Northland
CITY_LATROBE = 8135  # City_Latrobe

# directions
CITY_DIRECTION_QUEEN = 6
CITY_DIRECTION = 13
LATROBE_DIRECTION = 23
NORTHLAND_DIRECTION = 306

# routes = client.get_routes()
# print(json.dumps(routes))
# exit(0)

# stops = client.get_stops(TWO_FIVE_ONE_COMBINED, RouteType.BUS)
# print(json.dumps(stops))

# stop = client.get_departure_from_stop(RouteType.BUS,
#                                       MITCHELL_STREET,
#                                       CITY_NORTHLAND,
#                                       direction_id=CITY_DIRECTION_QUEEN,
#                                       max_results=5)


def format_departures(stop):
    departures = []

    now = datetime.utcnow()
    directions = stop.get("directions", {})
    routes = stop.get("routes", {})

    for departure in stop.get("departures", []):
        scheduled = parse_datetime(departure["scheduled_departure_utc"])
        realtime = parse_datetime(departure["estimated_departure_utc"])
        departing = realtime or scheduled
        arriving_seconds, arriving_str = get_diff(departing, now)

        direction = directions.get(str(departure["direction_id"]), None)
        route = routes.get(str(departure["route_id"]), None)
        item = {
            "route_number": route.get("route_number"),
            "route_name": route.get("route_name"),
            "route_id": departure["route_id"],
            "direction": direction.get("direction_name", "Unknown"),
            "direction_id": departure["direction_id"],
            "departing": get_tz_date(departing).isoformat(),
            "is_realtime": True if realtime else False,
            "arriving_seconds": arriving_seconds,
            "arriving_str": arriving_str,
        }
        departures.append(item)

    return departures


def parse_datetime(dt):
    if not dt:
        return None
    return datetime.strptime(dt, "%Y-%m-%dT%H:%M:%SZ")


def get_tz_date(dt):
    if not dt:
        return None
    from_zone = tz.gettz("UTC")
    dt = dt.replace(tzinfo=from_zone)
    return dt


def print_time(dt):
    return dt.strftime("%H:%M:%S")


def get_diff(scheduled, actual, show_which=False):
    which = "late"
    if scheduled > actual:
        delta = scheduled - actual
    else:
        which = "early"
        delta = actual - scheduled

    is_minutes = delta.seconds >= 60
    minutes = math.floor(delta.seconds / 60)
    is_hours = minutes >= 60
    hours = math.floor(minutes / 60)
    if is_hours:
        minutes = minutes % 60
    seconds = delta.seconds % 60

    string = f"{hours}h " if is_hours else ""
    string += f"{minutes}m " if is_minutes else ""
    if not is_hours:
        string += f"{seconds}s"

    if show_which:
        string += f" {which}"

    return delta.seconds, string.strip()


def get_late(delta):
    return math.floor(delta.seconds / 60) if delta and delta.seconds else 0


departures = client.get_departure_from_stop(
    RouteType.BUS,
    MITCHELL_STREET,
    CITY_LATROBE,
    max_results=5,
    direction_id=CITY_DIRECTION_QUEEN,
    expand=["direction", "route"],
)

departures = client.get_departure_from_stop(
    RouteType.BUS,
    MITCHELL_STREET,
    CITY_NORTHLAND,
    max_results=5,
    direction_id=CITY_DIRECTION_QUEEN,
    expand=["direction", "route"],
)


def get_departures(
    route_type_id, stop_id, max_results=5, route_ids=[], direction_ids=[]
):

    deps = client.get_departure_from_stop(
        route_type=RouteType(route_type_id),
        stop_id=stop_id,
        max_results=max_results,
        expand=["direction", "route"],
    )
    departures = format_departures(deps)

    if route_ids:
        departures = [d for d in departures if d["route_id"] in route_ids]

    if direction_ids:
        departures = [d for d in departures if d["direction_id"] in direction_ids]
    departures = sorted(departures, key=lambda d: d["arriving_seconds"])
    return departures[:max_results]


def get_stops_nearby(latitude, longitude, max_distance=300):
    stops = client.get_stop_near_location(
        latitude=latitude, longitude=longitude, max_distance=max_distance
    )
    return stops
