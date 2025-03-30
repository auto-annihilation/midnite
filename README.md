# Midnite - Activity Events API

This repository contains the backend API designed to handle activity events for the Midnight Code Challenge. The API serves as a foundation for managing and processing activity-related data in a flexible and efficient manner.

Assumptions made during development can be found within [Assumptions.md](./ASSUMPTIONS.MD).

## Core Components

- **API Server**: Built with [Flask](http://flask.pocoo.org)
- **Database**: [PostgreSQL](https://www.postgresql.org/) for reliable data persistence

## Quick Start

Prerequisites:

- **[Docker](https://www.docker.com)**: Containerization for consistent environments
- **[Make](https://www.gnu.org/software/make/)**: Command standardization and automation

```shell
# Start the api in the background (runs `docker-compose up --build --detach web`)
make start

# Apply database migrations (runs `docker-compose run --rm web flask db upgrade`)
make db.migrate
```

The API will be available at <http://127.0.0.1:5000>

You can then send an event to the API:

```shell
curl -XPOST http://127.0.0.1:5000/event \
-H 'Content-Type: application/json' \
-d '{"type": "withdraw", "amount": "100.00", "user_id": 1, "t": 0}'
```

Example Response

```json
{
  "alert": false,
  "alert_codes": [],
  "user_id": 1
}
```

To view logs:

```shell
make logs
```

Handling missing fields:

```shell
curl -XPOST http://127.0.0.1:5000/event \
-H 'Content-Type: application/json' \
-d '{"type": "withdraw", "amount": "100.00", "user_id": 1, "t": 0}'
```

This [Asciinema](https://asciinema.org/a/gNMdR2CfwEuENFRoAMuZtlTOE) recording provides an overvide of the above commands and their outputs.

## Running Tests

```shell
# Run tests with coverage
make test

# Runs the e2e tests (requires the API to be up and responsive)
make e2e
```

```bash
---------- coverage: platform linux, python 3.13.2-final-0 -----------
Name                        Stmts   Miss  Cover   Missing
---------------------------------------------------------
app/__init__.py                17      0   100%
app/config.py                  12      0   100%
app/datastores.py              32      6    81%   29-31, 40-42
app/events/__init__.py          0      0   100%
app/events/api.py              23      0   100%
app/events/constants.py         6      0   100%
app/events/controllers.py      45      0   100%
app/events/domains.py          14      0   100%
app/events/enums.py            11      1    91%   9
app/events/models.py           22      1    95%   47
app/events/queries.py          16      0   100%
app/events/schemas.py          13      0   100%
lib/__init__.py                 0      0   100%
lib/factory.py                 14      2    86%   17, 20
lib/fields.py                  19      1    95%   31
lib/logging.py                 43      9    79%   43, 54, 65-66, 71, 80-86
lib/schemas.py                 35      2    94%   26-27
lib/utils.py                    8      0   100%
---------------------------------------------------------
TOTAL                         330     22    93%
```

Alternatively to view this as a HTML Report in your browser:

```shell
make coverage
open .htmlcov/index.html
```

## Database Management

The following will open a PSQL session

```shell
# Access PostgreSQL console
make db.console
```

> Note: Tests use a separate database container that's automatically managed during test runs.

```shell
development=# \dt
              List of relations
 Schema |      Name       | Type  |  Owner
--------+-----------------+-------+----------
 public | activity_event  | table | postgres
 public | alembic_version | table | postgres
(2 rows)

development=# \d activity_event
                         Table "public.activity_event"
      Column       |           Type           | Collation | Nullable | Default
-------------------+--------------------------+-----------+----------+---------
 id                | uuid                     |           | not null |
 transaction_type  | activityeventtypeenum    |           | not null |
 amount            | numeric                  |           | not null |
 user_id           | integer                  |           | not null |
 event_received_at | integer                  |           | not null |
 created_at        | timestamp with time zone |           | not null |
 updated_at        | timestamp with time zone |           | not null |

Indexes:
    "activity_event_pkey" PRIMARY KEY, btree (id)
    "idx_events_created_by_user" btree (user_id, event_received_at)
    "ix_activity_event_created_at" btree (created_at)
    "ix_activity_event_event_received_at" btree (event_received_at)
    "ix_activity_event_updated_at" btree (updated_at)
```
