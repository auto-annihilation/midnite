import logging
from logging.config import fileConfig

from alembic import context
from flask import current_app
from sqlalchemy import MetaData

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)
logger = logging.getLogger("alembic.env")

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
config.set_main_option(
    "sqlalchemy.url",
    str(current_app.extensions["migrate"].db.get_engine().url).replace("%", "%%"),
)
target_db = current_app.extensions["migrate"].db


# the following tables are manually managed by the user and will not automatically create drop migrations
# even though there is no corresponding SQLAlchemy model.
managed_tables: list[str] = ["celery_tasksetmeta", "celery_taskmeta"]

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def include_object(object, name, type_, reflected, compare_to):  # NOQA: U100
    # Don’t generate any DROP TABLE directives with autogenerate
    # https://alembic.sqlalchemy.org/en/latest/cookbook.html#don-t-generate-any-drop-table-directives-with-autogenerate

    if name in managed_tables and type_ == "table" and reflected and compare_to is None:
        return False

    return True


def get_metadata() -> MetaData | None:
    """
    Attribute metadatas is dict mapping all bind keys (multiple databases).
    The None key refers to the default metadata, and is available as metadata.
    """
    if hasattr(target_db, "metadatas"):
        return target_db.metadatas[None]

    return target_db.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=get_metadata(), literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    # this callback is used to prevent an auto-migration from being generated
    # when there are no changes to the schema
    # reference: http://alembic.zzzcomputing.com/en/latest/cookbook.html
    def process_revision_directives(context, revision, directives):  # NOQA: U100
        if getattr(config.cmd_opts, "autogenerate", False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info("No changes in schema detected.")

    connectable = current_app.extensions["migrate"].db.get_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=get_metadata(),
            process_revision_directives=process_revision_directives,
            include_object=include_object,
            **current_app.extensions["migrate"].configure_args
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
