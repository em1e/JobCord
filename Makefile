.PHONY: help venv install run docker-build docker-run compose-bot-up compose-bot-down compose-airflow-up compose-airflow-down all

help:
	@echo "Makefile targets:"
	@echo "  venv              Create and activate a python virtualenv (.venv)"
	@echo "  install           Install Python requirements into .venv (calls pip)"
	@echo "  run               Run the Discord bot locally (uses .venv if available)"
	@echo "  docker-build      Build the Docker image for the bot (Dockerfile.bot)"
	@echo "  docker-run        Run the bot image with .env file"
	@echo "  compose-bot-up    Start the bot via docker-compose.bot.yml (detached)"
	@echo "  compose-bot-down  Stop the bot compose stack"
	@echo "  compose-airflow-up    Start the main docker-compose (Airflow)"
	@echo "  compose-airflow-down  Stop the main docker-compose"
	@echo "  all               Build and start bot (docker) and start airflow compose"

venv:
	python3 -m venv .venv

install: venv
	. .venv/bin/activate && pip install -r requirements.txt

run:
	@if [ -d .venv ]; then \
		. .venv/bin/activate && python -m discord_bot.bot; \
	else \
		python -m discord_bot.bot; \
	fi

run-local: venv
	@echo "Installing minimal bot dependencies into .venv (requirements-bot.txt)"
	. .venv/bin/activate && pip install --upgrade pip setuptools wheel && pip install -r requirements-bot.txt
	@echo "Initializing sqlite DB (src/data/user_profiles.db)"
	. .venv/bin/activate && python init_db.py
	@echo "Starting bot (local)"
	. .venv/bin/activate && python -m discord_bot.bot

docker-build:
	@echo "Building Docker image for the bot..."
	@if [ "$(uname -s)" = "Darwin" ]; then \
		echo "Detected macOS — building amd64 image to use prebuilt wheels"; \
		docker buildx build --platform linux/amd64 -t jobcord-bot -f Dockerfile.bot --load .; \
	else \
		docker build -t jobcord-bot -f Dockerfile.bot .; \
	fi

docker-run: docker-build
	docker run --env-file .env --rm jobcord-bot

compose-bot-up:
	@echo "Starting bot compose stack..."
	@if [ "$(uname -s)" = "Darwin" ]; then \
		echo "Detected macOS — building amd64 images for bot compose"; \
		docker compose -f docker-compose.bot.yml build --platform linux/amd64 && docker compose -f docker-compose.bot.yml up -d; \
	else \
		docker compose -f docker-compose.bot.yml up -d --build; \
	fi

compose-bot-down:
	docker compose -f docker-compose.bot.yml down

compose-airflow-up:
	@echo "Starting Airflow compose stack..."
	@if [ "$(uname -s)" = "Darwin" ]; then \
		echo "Detected macOS — building amd64 images for Airflow compose"; \
		docker compose build --platform linux/amd64 && docker compose up -d; \
	else \
		docker compose up -d --build; \
	fi

compose-airflow-down:
	docker compose down

all: docker-build compose-airflow-up compose-bot-up
