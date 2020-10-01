"""Platform for sensor integration."""
# from homeassistant.const import TEMP_CELSIUS, DEVICE_CLASS_TIMESTAMP
from homeassistant.helpers.entity import Entity
from .next_5 import get_departures, get_stops_nearby


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""

    add_entities([PTVSensor(hass, config)])


class PTVSensor(Entity):
    """Representation of a Sensor."""
    def __init__(self, hass, config):
        """Initialize the sensor."""
        self._hass = hass
        self._config = config
        self._state = None
        self._attributes = {}
        self._departures = []
        self._debug_nearby = {}

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._config.get("name", "PTV Departures")

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return 'ISO8601'

    @property
    def device_class(self):
        return 'timestamp'

    @property
    def device_state_attributes(self) -> dict:
        """Return the state attributes."""
        attr = {"departures": self._departures}

        if self._debug_nearby:
            attr["nearby_stops"] = self._debug_nearby

        return attr

    def get_location(self):
        home_zone = self._hass.states.get('zone.home').attributes
        return home_zone["latitude"], home_zone["longitude"]

    def update(self):
        """Fetch new state data for the sensor."""

        route_type = self._config.get("route_type", 2)
        stop_id = self._config.get("stop_id", None)
        max_results = self._config.get("max_results", 5)
        route_ids = self._config.get("route_ids", [])
        debug_nearby = self._config.get("debug_nearby", False)
        debug_distance = self._config.get("debug_distance", 300)
        direction_ids = self._config.get("direction_ids", [])

        self._departures = get_departures(route_type, stop_id, max_results,
                                          route_ids, direction_ids)
        self._state = self._departures[0]["departing"]

        if debug_nearby:
            latitude, longitude = self.get_location()
            self._debug_nearby = get_stops_nearby(latitude, longitude,
                                                  debug_distance)
