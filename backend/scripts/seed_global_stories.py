"""Seed ~200 realistic, globally distributed stories.

Replaces the old coarse "Dev story N" rows (all snapped to a ~1 km grid in
Almaty, which stacked on top of each other and vanished when zoomed in) with
stories spread across cities worldwide. Each story is created through the same
path real submissions use, so ``location_public`` is fuzzed 250-750 m off the
exact point and pins land at natural, distinct coordinates at every zoom level.

Run inside the api container:
    docker exec loci-api python scripts/seed_global_stories.py
"""

import asyncio
import random
from datetime import date, timedelta

from sqlalchemy import delete, select

from app.db.models.story import (
    LocationPrecision,
    ModerationStatus,
    StoryVisibility,
)
from app.db.models.story import Story
from app.db.repositories import stories as stories_repo
from app.db.models.user import User
from app.db.session import dispose_db, get_engine
from app.core.security.geo import fuzz_story_location

# (city, lat, lon) — a spread across every inhabited continent.
CITIES = [
    ("Almaty", 43.2380, 76.9455), ("Astana", 51.1605, 71.4704),
    ("Tokyo", 35.6762, 139.6503), ("Seoul", 37.5665, 126.9780),
    ("Beijing", 39.9042, 116.4074), ("Shanghai", 31.2304, 121.4737),
    ("Bangkok", 13.7563, 100.5018), ("Singapore", 1.3521, 103.8198),
    ("Mumbai", 19.0760, 72.8777), ("Delhi", 28.6139, 77.2090),
    ("Dubai", 25.2048, 55.2708), ("Istanbul", 41.0082, 28.9784),
    ("Tashkent", 41.2995, 69.2401), ("Tbilisi", 41.7151, 44.8271),
    ("Moscow", 55.7558, 37.6173), ("Saint Petersburg", 59.9311, 30.3609),
    ("Helsinki", 60.1699, 24.9384), ("Stockholm", 59.3293, 18.0686),
    ("Oslo", 59.9139, 10.7522), ("Berlin", 52.5200, 13.4050),
    ("Amsterdam", 52.3676, 4.9041), ("Paris", 48.8566, 2.3522),
    ("London", 51.5074, -0.1278), ("Dublin", 53.3498, -6.2603),
    ("Lisbon", 38.7223, -9.1393), ("Madrid", 40.4168, -3.7038),
    ("Barcelona", 41.3874, 2.1686), ("Rome", 41.9028, 12.4964),
    ("Athens", 37.9838, 23.7275), ("Vienna", 48.2082, 16.3738),
    ("Prague", 50.0755, 14.4378), ("Warsaw", 52.2297, 21.0122),
    ("Cairo", 30.0444, 31.2357), ("Nairobi", -1.2921, 36.8219),
    ("Lagos", 6.5244, 3.3792), ("Cape Town", -33.9249, 18.4241),
    ("Johannesburg", -26.2041, 28.0473), ("Marrakesh", 31.6295, -7.9811),
    ("New York", 40.7128, -74.0060), ("Toronto", 43.6532, -79.3832),
    ("Chicago", 41.8781, -87.6298), ("San Francisco", 37.7749, -122.4194),
    ("Los Angeles", 34.0522, -118.2437), ("Mexico City", 19.4326, -99.1332),
    ("Bogota", 4.7110, -74.0721), ("Lima", -12.0464, -77.0428),
    ("Sao Paulo", -23.5505, -46.6333), ("Rio de Janeiro", -22.9068, -43.1729),
    ("Buenos Aires", -34.6037, -58.3816), ("Santiago", -33.4489, -70.6693),
    ("Sydney", -33.8688, 151.2093), ("Melbourne", -37.8136, 144.9631),
    ("Auckland", -36.8485, 174.7633), ("Reykjavik", 64.1466, -21.9426),
]

# category_id -> pools of (title, body) so each pin reads like a real memory.
STORIES_BY_CATEGORY = {
    1: [("Where we first met", "A rainy afternoon and one shared umbrella changed everything."),
        ("The long way home", "We walked for hours just to keep talking a little longer.")],
    2: [("Best coffee of my life", "Tiny corner cafe, no sign, unforgettable morning."),
        ("Street festival night", "Music everywhere and strangers dancing like old friends.")],
    3: [("The place I want to return", "Standing here I promised myself I'd come back one day."),
        ("A quiet plan", "Sat on this bench and sketched out the next five years.")],
    4: [("My first lecture hall", "Nervous, early, and completely in love with the subject."),
        ("Late-night study spot", "Half the degree happened at this table by the window.")],
    5: [("First day at work", "Got lost in the lobby, found my desk, never looked back."),
        ("The pitch that landed", "Weeks of prep for ten minutes that changed the year.")],
    6: [("Off the tourist trail", "Wandered a side street and found the real city."),
        ("Sunrise from the hill", "Woke at four, hiked up, watched the town wake with me.")],
    7: [("Reunion after years apart", "Same laugh, same jokes, like no time had passed."),
        ("The bench where we'd talk", "Every problem felt smaller after an hour here.")],
    8: [("The park from childhood", "The swings are smaller now but the feeling is the same."),
        ("Grandmother's street", "Still smells like her kitchen when the wind is right.")],
    9: [("I finally finished it", "Crossed the line I'd been staring at for a year."),
        ("First time on stage", "Hands shaking, but I did it, right on this spot.")],
    10: [("The view I never forgot", "Some places just stop you where you stand."),
         ("Hidden little garden", "Found peace between two busy avenues.")],
    11: [("This is where it happened", "A small moment I keep coming back to."),
         ("Old photograph spot", "Recreated a picture from twenty years ago.")],
    12: [("The house nobody enters", "Locals swear the lights still turn on at midnight."),
         ("Legend of the old bridge", "They say you should never cross it counting out loud.")],
}

MEMORY_DETAILS = [
    "I had nowhere else to be, so I stayed until the light changed.",
    "It was ordinary at the time, which is probably why I remember it so clearly.",
    "I sent a photo to my sister and wrote: I think I could live here.",
    "Years later, I can still remember the exact sound of the street.",
    "Nothing dramatic happened. It just became one of those days I keep.",
    "I nearly walked past, then something made me turn around.",
    "We did not know it yet, but this was the beginning of a different chapter.",
    "The place has changed since then, but the memory has not.",
]


async def main() -> None:
    # HARD GUARD: this script deletes and inserts stories. Never let it touch a
    # production database. It only runs when APP_ENV is development/local and the
    # database host is local. Prod uses a different DB and a non-dev APP_ENV.
    from app.core.config import get_settings

    settings = get_settings()
    host = (settings.postgres_host or "").lower()
    url = (settings.database_url or "").lower()
    is_local_host = host in {"localhost", "127.0.0.1", "postgres", "db"}
    is_local_url = (not url) or ("localhost" in url) or ("127.0.0.1" in url) or ("@postgres" in url)
    if settings.app_env not in {"development", "local", "dev"} or not (is_local_host and is_local_url):
        raise SystemExit(
            f"refusing to seed: app_env={settings.app_env!r} host={host!r}. "
            "This script is for local development only."
        )

    get_engine()
    from app.db.session import _session_factory  # populated by get_engine()
    assert _session_factory is not None

    rng = random.Random(42)
    today = date.today()

    async with _session_factory() as db:
        # use several telegram-shaped profiles so the map reads like a shared archive
        seed_profiles = [
            (910000001, "mira_k", "Mira", None),
            (910000002, None, "Daniyar", None),
            (910000003, "samira.notes", "Samira", None),
            (910000004, None, "Alex", None),
            (910000005, "niko_wanders", "Niko", None),
            (910000006, "aigerim_reads", "Aigerim", None),
            (910000007, None, "Jo", None),
            (910000008, "theo_afterdark", "Theo", None),
        ]
        authors: list[User] = []
        for telegram_id, username, first_name, last_name in seed_profiles:
            author = await db.scalar(select(User).where(User.telegram_id == telegram_id))
            if author is None:
                author = User(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    language_code="en",
                )
                db.add(author)
                await db.flush()
            authors.append(author)
        if not authors:
            raise SystemExit("no users in db; create a user before seeding")

        # reruns replace only this script's recognizable demo stories
        legacy_titles = [title for entries in STORIES_BY_CATEGORY.values() for title, _ in entries]
        await db.execute(delete(Story).where(Story.title.in_(legacy_titles)))
        dev_removed = await db.execute(delete(Story).where(Story.title.like("Dev story%")))
        await db.commit()
        print(f"removed demo stories and {dev_removed.rowcount or 0} legacy dev stories")

        created = 0
        for i, (city, lat, lon) in enumerate(CITIES):
            # four memories per city gives the map a full, varied global texture
            for story_number in range(4):
                category_id = rng.randint(1, 12)
                title, body = rng.choice(STORIES_BY_CATEGORY[category_id])
                body = f"{body} {rng.choice(MEMORY_DETAILS)}"
                # jitter the exact point a few km so multiple stories per city
                # aren't identical before fuzzing
                ex_lat = lat + rng.uniform(-0.04, 0.04)
                ex_lon = lon + rng.uniform(-0.04, 0.04)
                happened = today - timedelta(days=rng.randint(30, 3000))

                author = authors[(i * 4 + story_number) % len(authors)]
                is_anonymous = (i * 4 + story_number) % 9 == 0
                story_id = await stories_repo.create(
                    db,
                    author_id=author.id,
                    category_id=category_id,
                    title=f"{title}",
                    body=f"{body} I still think about that day in {city}.",
                    happened_on=happened,
                    is_anonymous=is_anonymous,
                    visibility=StoryVisibility.public,
                    precision=LocationPrecision.approx,
                    exact_lat=ex_lat,
                    exact_lon=ex_lon,
                    moderation_status=ModerationStatus.approved,
                )
                fz_lat, fz_lon = fuzz_story_location(story_id, ex_lat, ex_lon)
                await stories_repo.set_public_point(db, story_id, fz_lat, fz_lon)
                created += 1
        await db.commit()
        print(f"created {created} global stories across {len(CITIES)} cities")

    await dispose_db()


if __name__ == "__main__":
    asyncio.run(main())
