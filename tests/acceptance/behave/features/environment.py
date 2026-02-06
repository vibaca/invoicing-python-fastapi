import os
import pymysql


def before_scenario(context, scenario):
    """Truncate all tables in the test database before each scenario to ensure isolation.

    This runs inside the container where `behave` executes — it reads DB connection
    info from environment variables (set by the test runner).
    """
    db_host = os.getenv("DB_HOST", "db")
    db_port = int(os.getenv("DB_PORT", "3306"))
    db_user = os.getenv("DB_USER", "root")
    db_password = os.getenv("DB_PASSWORD", "password")
    db_name = os.getenv("DB_NAME", "invoicing_test")

    # Connect directly and truncate every user table in the schema
    conn = pymysql.connect(host=db_host, port=db_port, user=db_user, password=db_password, database=db_name, autocommit=True)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema=%s", (db_name,))
            rows = cur.fetchall()
            tables = [r[0] for r in rows]
            if not tables:
                return
            cur.execute("SET FOREIGN_KEY_CHECKS=0;")
            for t in tables:
                cur.execute(f"TRUNCATE TABLE `{t}`;")
            cur.execute("SET FOREIGN_KEY_CHECKS=1;")
    finally:
        conn.close()
