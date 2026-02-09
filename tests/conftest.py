import os
import sys
import atexit
import warnings
import pytest

# Ensure tests run against a dedicated test database by default when running
# pytest locally. If `DB_NAME` is explicitly provided in the environment (e.g.
# via the Makefile or CI), do not override it.
if "DB_NAME" not in os.environ:
    os.environ["DB_NAME"] = "invoicing_test"

# Safety check: prevent running tests against the development database
if os.environ.get("DB_NAME") == "invoicing_dev":
    raise RuntimeError(
        "Refusing to run tests with DB_NAME=invoicing_dev.\n"
        "Set DB_NAME to a test database (e.g. invoicing_test) or run via the Makefile targets that set TEST_MODE and DB_NAME."
    )

# Ensure project root is on sys.path so `from src...` imports work when
# `PYTHONPATH` is not set (common in Windows shells or some container
# environments). This mirrors the guard used in scripts/init_db.py.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from sqlalchemy.exc import SAWarning

# Import the engine after ensuring `DB_NAME` is set so the module-level
# `DATABASE_URL` is constructed for the test database instead of `invoicing_dev`.
from src.Infrastructure.Database.Db import engine

# Reduce noisy SAWarning messages during test runs where event loop shutdown
# can cause aiomysql connections to be GC-cleaned. Tests still exercise DB
# behaviour; this just keeps the logs clean for CI output.
warnings.filterwarnings("ignore", category=SAWarning)


@pytest.fixture(scope="function", autouse=True)
def dispose_engine_after_test():
    """Best-effort: dispose engine connection pools after each test.

    Disposing after each test ensures connection cleanup happens while the
    asyncio event loop is still running, avoiding aiomysql GC warnings
    that occur when connections are finalized after loop shutdown.
    """
    yield
    try:
        engine.sync_engine.dispose()
    except Exception:
        # best-effort cleanup in test teardown
        pass





def _dispose_engine_best_effort():
    try:
        engine.sync_engine.dispose()
    except Exception:
        pass


# Register an atexit handler as an additional best-effort cleanup
atexit.register(_dispose_engine_best_effort)


def pytest_sessionfinish(session, exitstatus):
    """Pytest hook to ensure engine dispose runs at session end.

    Some asyncio fixtures may close the event loop before regular fixture
    finalizers run; calling dispose here is an additional attempt to close
    connections gracefully and reduce SAWarnings observed during teardown.
    """
    _dispose_engine_best_effort()
