# JobCord
Keeps job hunt organized, automated, and inside Discord.

## How to run the Discord bot

A short contract:
- Input: a valid Discord Bot token available as an environment variable named `DISCORD_BOT_TOKEN`.
- Output: a running Discord bot that registers/syncs application commands and responds to configured commands in `discord_bot/commands/`.
- Error modes: missing or invalid token will prevent the bot from starting; inspect logs for token errors.

Minimum steps (local development)

1. Install Python (3.10+) and create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Provide your Discord bot token. The bot looks for the environment variable `DISCORD_BOT_TOKEN`. You can set it in your shell or use an env file. Example (.env):

```
DISCORD_BOT_TOKEN=your_discord_bot_token_here
```

To export it in zsh for the current session:

```bash
export DISCORD_BOT_TOKEN="your_discord_bot_token_here"
```

Note: The repository does not automatically load `.env` files. If you prefer automatic loading, install `python-dotenv` and modify the bot startup to load the `.env` (or use a small helper to export variables before starting the bot).

4. Run the bot:

```bash
python -m discord_bot.bot
# or
python discord_bot/bot.py
```

You should see a message like:

```
✅ Logged in as <BotName>
🔧 Synced X commands.
```

Troubleshooting
- If nothing happens or you see errors about the token, confirm `DISCORD_BOT_TOKEN` is set and valid.
- If the bot fails while syncing commands, check that the bot has application command permissions in the Discord Developer Portal and that the token belongs to the right application.

Running in Docker (optional)

The repository includes a `dockerfile` used for Airflow and not configured specifically to run the Discord bot. If you want a quick Docker image for the bot, create a small `Dockerfile.bot` like the example below and build it.

Example `Dockerfile.bot`:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
COPY . /app
ENV PYTHONUNBUFFERED=1
CMD ["python", "discord_bot/bot.py"]
```

Build and run (example):

```bash
docker build -t jobcord-bot -f Dockerfile.bot .
docker run --env-file .env jobcord-bot
```

Notes
- The bot entrypoint is `discord_bot/bot.py` and it expects the token in `DISCORD_BOT_TOKEN` (see `discord_bot/bot.py`).
- This README section focuses on running the Discord bot locally or inside a simple container. The repo also contains Airflow/DAG configuration and other components (see `docker-compose.yaml` and `dags/`) which are separate from the Discord bot runtime.

If you want, I can also add an example `.env.example` and a simple `Dockerfile.bot` to the repo. Would you like me to add those now?

Makefile and automation

To make running the bot and Airflow easier, this repo includes a `Makefile` with convenient targets:

- `make venv` — create a `.venv` virtual environment.
- `make install` — install `requirements.txt` into `.venv`.
- `make run` — run the Discord bot locally (uses `.venv` if present).
- `make docker-build` — build a `jobcord-bot` Docker image (uses `Dockerfile.bot`).
- `make docker-run` — run the built bot image with `.env`.
- `make compose-bot-up` / `make compose-bot-down` — start/stop the lightweight `docker-compose.bot.yml` service for the bot.
- `make compose-airflow-up` / `make compose-airflow-down` — start/stop the main Airflow `docker-compose.yaml` stack.
- `make all` — builds the bot image, brings up the Airflow compose and the bot compose stack.

Files added to support automation:

- `.env.example` — example environment variables for local/dev runs (copy to `.env`).
- `Dockerfile.bot` — small Dockerfile to run the Discord bot inside a container.
- `docker-compose.bot.yml` — minimal compose file to run the bot as a service (separate from Airflow stack).
- `Makefile` — shortcuts described above.

Recommendation: If you want the DAGs to run automatically and send messages to Discord, you'll need to run the Airflow compose stack (`docker compose up` using the provided `docker-compose.yaml`) so that the scheduler can execute the DAGs. The bot container or a webhook (Airflow tasks use `DISCORD_WEBHOOK_URL` and also call functions from the `discord_bot` package) is necessary for delivery. Running the `docker-compose.yaml` (Airflow) plus the `docker-compose.bot.yml` (bot) is the simplest way to get full automation.

Troubleshooting Docker build failures

If `make docker-build` or `docker build` fails during `pip install -r requirements.txt` with an error like "No matching distribution found for sqlite3", that's because `sqlite3` is not a pip-installable package — it's part of Python's standard library. The repository has been updated to remove `sqlite3` from `requirements.txt`.

Other helpful tips if you hit build issues:

- Re-run the build after pulling the latest changes (so `requirements.txt` is updated):

```bash
make docker-build
```

- On Apple Silicon (M1/M2) machines you may see wheel compatibility issues for packages like `pandas`. Two simple options:
	1) Build the image for amd64 using:

```bash
docker build --platform linux/amd64 -t jobcord-bot -f Dockerfile.bot .
# or with buildx for multi-platform builds
docker buildx build --platform linux/amd64 -t jobcord-bot -f Dockerfile.bot .
```

	2) Install required system libraries in the image (e.g. `libsqlite3-dev`, `build-essential`) — `Dockerfile.bot` already installs basic build tools; add extra system packages if a package specifically requires them.

- Locally, test installing the requirements before building the image to catch errors quickly:

```bash
. .venv/bin/activate
pip install -r requirements.txt
```

If you want, I can also:

 - add a CI job that builds the Docker image to catch these issues early, or
 - change the Makefile to use `docker buildx --platform linux/amd64` on macOS automatically.


