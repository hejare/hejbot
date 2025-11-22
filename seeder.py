import random
from datetime import datetime, timedelta
from psycopg2.extras import execute_values
import logging

from config import Config
from db import get_db_connection

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

entries = [
    "In app reviews",
    "Uppskattad demo",
    "Lobby design TV",
    "New design lobby Android TV",
    "Test fiesta",
    "A11y meeting prep",
    "New login on TV design",
    "In-App Reviews",
    "Hjälpt barn i Play",
    "Release manager - Uppdaterat docs",
    "New lobby design mobile",
    "Tagit på mig roll i tillgänglighetsarbete på SVT",
    "Rundvandring på SVT",
    "Onboarding dokument och bättre MR templates",
    "Lobby design",
    "Hack friday: In-app reviews.Sport schedules, polish, etc.",
]


def random_timestamp():
    now = datetime.now()
    past_year = now - timedelta(days=365)
    delta = now - past_year
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return past_year + timedelta(seconds=random_seconds)


def seed_cv_entries():
    user_id = Config.SLACK_USER_ID
    records = [(user_id, entry, random_timestamp()) for entry in entries]
    records.sort(key=lambda x: x[2])

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM cv_entries WHERE user_id = %s", (user_id,))
            logger.info(f"Deleted existing CV entries for user {user_id}.")

            records = [(user_id, entry, random_timestamp()) for entry in entries]
            records.sort(key=lambda x: x[2])
            execute_values(
                cur,
                "INSERT INTO cv_entries (user_id, text, timestamp) VALUES %s",
                records,
            )
        conn.commit()
        logger.info(f"Inserted {len(records)} new CV entries for user {user_id}.")
    finally:
        conn.close()


if __name__ == "__main__":
    seed_cv_entries()
