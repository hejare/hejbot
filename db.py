import psycopg2
from psycopg2.extras import RealDictCursor

from config import Config


def setup_db():
    """Initialize database schema."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS cv_entries (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                text TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL
            );
            CREATE TABLE IF NOT EXISTS assignments (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                company_name VARCHAR(255) NOT NULL,
                role_name VARCHAR(255) NOT NULL,
                timestamp_start TIMESTAMP NOT NULL,
                timestamp_end TIMESTAMP
            );
        """
        )
        conn.commit()
    finally:
        conn.close()


def get_db_connection():
    """Get a PostgreSQL database connection."""
    return psycopg2.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        database=Config.DB_DATABASE,
        user=Config.DB_USERNAME,
        password=Config.DB_PASSWORD,
        sslmode=Config.DB_SSL_MODE,
    )


def query(query_text, parameters):
    """Execute a database query and return results."""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query_text, parameters)
            if query_text.strip().upper().startswith("SELECT"):
                return cur.fetchall()
            else:
                return None
