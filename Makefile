default: help

build: network ## Build the base web and test containers
	@docker-compose build web
	@docker-compose build test

build.test: ## Build the test container
	@docker-compose build test

build.web: ## Build the web container
	@docker-compose build web

db.console: network ## Open a database console
	@docker-compose exec db psql -h localhost -U postgres development

db.migrate: build.web network ## Run database migrations locally
	@docker-compose run --rm web flask db upgrade

db.rollback: build.web network ## Run database downgrade locally
	@docker-compose run --rm web flask db downgrade

help: ## Show this help menu
	@echo
	@fgrep -h " ## " $(MAKEFILE_LIST) | fgrep -v fgrep | sed -Ee 's/([a-z.]*):[^#]*##(.*)/\1##\2/' | column -t -s "##"
	@echo

run: start logs ## run the application locally

start: ## run the application locally in the background
	@docker-compose up --build --detach web

debug: start ## run the application locally in debug mode
	@docker attach $$(docker-compose ps --quiet web)

stop: ## stop the application
	@docker-compose down --remove-orphans

clean: ## delete all data from the local databases
	@docker-compose down --remove-orphans --volumes

logs: ## show the application logs
	@docker-compose logs --follow web

shell: ## shell into a development container
	@docker-compose build web
	@docker-compose run --rm web bash

network: ## Create the audit-api network if it doesn't exist
	docker network create --driver bridge audit-api || true

lint: build.web ## Lint and format the code
	@docker-compose run --rm --no-deps web sh -c "\
		ruff check --fix . && \
		MYPY_FORCE_COLOR=1 mypy . && \
		codespell --enable-colors . && \
		refurb ."

format: build.web ## Format the code
	@docker-compose run --rm --no-deps web sh -c "ruff check . --fix"

test: build.test network ## Run the unit tests and linters
	@docker-compose -f docker-compose.yml run --rm test sh -c "\
		pytest -s --cov=app/ --cov=lib/ --cov-report term-missing"

e2e: build.test network ## Run the end-to-end tests
	@docker-compose -f docker-compose.yml run --rm test sh -c "pytest -s e2e"

test-shell: ## Spin up a shell in the test container
	@docker-compose -f docker-compose.yml build test
	@docker-compose -f docker-compose.yml run --rm test bash

coverage: build.test network ## Generate HTML coverage output report to .htmlcov directory
	@docker-compose -f docker-compose.yml run --rm test sh -c "pytest -s --cov=app/ --cov=lib/ --cov-report html:.htmlcov"
