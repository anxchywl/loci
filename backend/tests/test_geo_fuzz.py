import math
import random
from uuid import UUID, uuid4

from app.core.security.geo import EARTH_RADIUS_M, fuzz_point

SECRET = "test-secret"
MIN_M = 250
MAX_M = 750


def haversine_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


def fuzz(story_id: UUID, lat: float, lon: float) -> tuple[float, float]:
    return fuzz_point(story_id, lat, lon, secret=SECRET, min_meters=MIN_M, max_meters=MAX_M)


def test_offset_distance_always_within_ring():
    rng = random.Random(42)
    for _ in range(500):
        lat = rng.uniform(-85, 85)
        lon = rng.uniform(-180, 180)
        flat, flon = fuzz(uuid4(), lat, lon)
        distance = haversine_meters(lat, lon, flat, flon)
        assert MIN_M <= distance <= MAX_M + 1e-6


def test_deterministic_for_same_story_and_point():
    story_id = uuid4()
    assert fuzz(story_id, 43.238949, 76.889709) == fuzz(story_id, 43.238949, 76.889709)


def test_different_stories_get_different_offsets():
    lat, lon = 43.238949, 76.889709
    points = {fuzz(uuid4(), lat, lon) for _ in range(50)}
    assert len(points) == 50


def test_secret_changes_output():
    story_id = uuid4()
    lat, lon = 43.238949, 76.889709
    a = fuzz_point(story_id, lat, lon, secret="secret-a", min_meters=MIN_M, max_meters=MAX_M)
    b = fuzz_point(story_id, lat, lon, secret="secret-b", min_meters=MIN_M, max_meters=MAX_M)
    assert a != b


def test_moving_the_pin_changes_the_offset_sample():
    story_id = uuid4()
    a = fuzz(story_id, 43.238949, 76.889709)
    b = fuzz(story_id, 43.238950, 76.889709)
    assert a != b


def test_output_valid_near_pole():
    flat, flon = fuzz(uuid4(), 89.9999, 10.0)
    assert -90.0 <= flat <= 90.0
    assert -180.0 <= flon <= 180.0


def test_output_valid_and_within_ring_near_antimeridian():
    lat, lon = -36.5, 179.99999
    flat, flon = fuzz(uuid4(), lat, lon)
    assert -180.0 <= flon <= 180.0
    assert MIN_M <= haversine_meters(lat, lon, flat, flon) <= MAX_M + 1e-6


def test_averaging_repeated_fuzzes_does_not_converge_to_exact():
    story_id = uuid4()
    lat, lon = 43.238949, 76.889709
    samples = [fuzz(story_id, lat, lon) for _ in range(100)]
    assert len(set(samples)) == 1
    mean_lat = sum(p[0] for p in samples) / len(samples)
    mean_lon = sum(p[1] for p in samples) / len(samples)
    assert haversine_meters(lat, lon, mean_lat, mean_lon) >= MIN_M
