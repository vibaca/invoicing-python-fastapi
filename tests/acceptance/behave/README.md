Run Behave acceptance tests locally (no Docker).

Prerequisites:
- Python 3.11+ (virtualenv recommended)
- Install dev requirements: `pip install -r requirements-dev.txt`

Run:

```bash
# Start the API (docker-compose up -d api db rabbit)
# Then on your host, run:
behave -f progress tests/acceptance/behave/features
```

The steps use `http://localhost:8000` as the API base; ensure the API is reachable.
