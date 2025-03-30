import subprocess

from _pytest.fixtures import SubRequest
from sqlalchemy.sql import text

from app import db


def test_migration(request: SubRequest) -> None:
    """Test for missing migration files by running an upgrade/migrate cycle and
    inspecting the output.
    """

    def teardown() -> None:
        """SQLAlchemy.drop_all doesn't know anything about the tables used by
        Flask-Migrate/alembic and so they must be dropped explicitly as part of
        this cleanup.
        """
        # Recreate all the SQLAlchemy models added by the db test fixture
        db.create_all()
        with db.engine.begin() as connection:
            connection.execute(text("drop table alembic_version"))

    request.addfinalizer(teardown)

    # Drop all tables prior to test run to ensure a clean database.
    # We need to do this because to keep our other tests "clean", we have
    #  marked the session fixture as autouse=True. This creates all of the
    #  database tables for our SQLAlchemy models but does not create an
    #  alembic_version table. This leads flask db upgrade to try and apply
    #  all of the migrations again over the top of the tables that already
    #  exist. This causes the command to fail as the tables exist.
    db.drop_all()
    upgrade = subprocess.run(
        ["flask", "db", "upgrade"], capture_output=True, check=True  # noqa: S603,S607
    )
    assert upgrade.returncode == 0

    # :thumbsdown: The Flask-Migrate API doesn't return anything, so we resort
    # to running it in another process and inspecting stdout.
    migrate = subprocess.run(
        ["flask", "db", "migrate"],  # noqa: S603,S607
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )
    assert migrate.returncode == 0

    assert "No changes" in migrate.stdout.decode("utf-8")
