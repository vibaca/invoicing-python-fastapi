import os
import psycopg2


def before_scenario(context, scenario):
    """Truncate all tables in the test database before each scenario to ensure isolation.

    This runs inside the container where `behave` executes — it reads DB connection
    info from environment variables (set by the test runner).
    """
    db_host = os.getenv("DB_HOST", "db")
    db_port = int(os.getenv("DB_PORT", "5432"))
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "password")
    db_name = os.getenv("DB_NAME", "invoicing_test")

    # Connect directly and truncate every user table in the public schema
    conn = psycopg2.connect(host=db_host, port=db_port, user=db_user, password=db_password, dbname=db_name)
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT tablename FROM pg_tables WHERE schemaname='public';")
            rows = cur.fetchall()
            tables = [r[0] for r in rows]
            if not tables:
                return
            for t in tables:
                cur.execute(f'TRUNCATE TABLE "{t}" CASCADE;')
    finally:
        conn.close()
