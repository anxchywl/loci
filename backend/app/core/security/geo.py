import hmac
import math
from hashlib import sha256
from uuid import UUID

from app.core.config import get_settings

EARTH_RADIUS_M = 6371000.0


def fuzz_point(
    story_id: UUID,
    lat: float,
    lon: float,
    *,
    secret: str,
    min_meters: int,
    max_meters: int,
) -> tuple[float, float]:
    # deterministic per (story, exact point): repeated re-fuzzing yields one sample,
    # so precision toggles can't be averaged to recover the exact location
    message = story_id.bytes + f"{lat:.7f}:{lon:.7f}".encode()
    digest = hmac.new(secret.encode(), message, sha256).digest()

    distance_fraction = int.from_bytes(digest[:8], "big") / 2**64
    distance = min_meters + (max_meters - min_meters) * distance_fraction
    bearing = 2 * math.pi * (int.from_bytes(digest[8:16], "big") / 2**64)

    # great-circle destination formula stays valid at poles and the antimeridian
    angular = distance / EARTH_RADIUS_M
    lat1 = math.radians(lat)
    lon1 = math.radians(lon)

    lat2 = math.asin(
        math.sin(lat1) * math.cos(angular)
        + math.cos(lat1) * math.sin(angular) * math.cos(bearing)
    )
    lon2 = lon1 + math.atan2(
        math.sin(bearing) * math.sin(angular) * math.cos(lat1),
        math.cos(angular) - math.sin(lat1) * math.sin(lat2),
    )

    fuzzed_lat = math.degrees(lat2)
    fuzzed_lon = (math.degrees(lon2) + 180.0) % 360.0 - 180.0
    return fuzzed_lat, fuzzed_lon


def fuzz_story_location(story_id: UUID, lat: float, lon: float) -> tuple[float, float]:
    settings = get_settings()
    return fuzz_point(
        story_id,
        lat,
        lon,
        secret=settings.location_fuzz_secret,
        min_meters=settings.location_fuzz_min_meters,
        max_meters=settings.location_fuzz_max_meters,
    )
