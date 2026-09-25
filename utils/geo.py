from math import asin, cos, radians, sin, sqrt

from errors.exceptions import BadRequestError


def haversine_km(lat1, lng1, lat2, lng2):
    lat1, lng1, lat2, lng2 = map(radians, (lat1, lng1, lat2, lng2))
    a = sin((lat2 - lat1) / 2) ** 2 + cos(lat1) * cos(lat2) * sin((lng2 - lng1) / 2) ** 2
    return 6371.0 * 2 * asin(sqrt(a))


def parse_coordinates(lat, lng):
    """(None, None) passes through; otherwise both must be present and in range."""
    if lat is None and lng is None:
        return None, None
    if lat is None or lng is None:
        raise BadRequestError("latitude and longitude must be provided together.")
    try:
        lat, lng = float(lat), float(lng)
    except (TypeError, ValueError):
        raise BadRequestError("Invalid coordinates.")
    if not (-90 <= lat <= 90 and -180 <= lng <= 180):
        raise BadRequestError("Coordinates out of range.")
    return lat, lng
