# REVIEW 001 : feature/switch-mysql-to-postgres

## Summary of Changes
- 7 files modified/created (Dockerfile, .env, .dockerignore, docker-compose.yml, Makefile, scripts/db.sh, scripts/test_acceptance.sh)
- 3 files deleted (run_acceptance.sh, setup.sh)
- Result: Cleaner, faster builds, better security, maintainable scripts

## Assessment of environment setup
The setup is **over-engineered but functional**. Breakdown:

### What's Good
- Proper Dockerfile layering (deps before code)
- Separate dev/prod requirements
- Service dependencies (db, rabbit)
- Volume mounts for development

### What's Redundant/Problematic
1. Missing `.env` file
`DB_NAME: ${DB_NAME:-invoicing_dev}` (compose.yml needs it)

2. Too Many Scripts (3 files doing what 1 could do)
- `setup.sh` + `run_acceptance.sh` + `init_db.py` = complexity
- Most logic should be in Makefile or docker-compose

3. Makefile Anti-Patterns
- Reinstalling requirements in every test command
- Complex bash in Makefile (should be in scripts)
- Test commands too brittle

4. Dockerfile Inefficiencies
- `python:3.11-bullseye` is heavy (use `-slim`)
- Installing Rust/Cargo for cryptography (use `--no-binary` or different base)
- Copying entire source as root (security issue)

5. Volume Mount
`./:/app mounts` everything, including virtual envs and cache files

### Minimal Fixed Version

**Files you actually need:**

`Dockerfile`
`docker-compose.yml`
`.env`
`.dockerignore`
`requirements.txt`
`requirements-dev.txt`

Delete `run_acceptance.sh` and move logic to **Makefile** or **compose profiles**.

## Details of proposed tunning

