"""Configure Django database settings from environment variables."""

import os
from pathlib import Path
from typing import NotRequired, Required, TypedDict
from urllib.parse import parse_qs, unquote, urlparse


# class type for Database settings
class DatabaseSettingsType(TypedDict):
    """TypedDict for Django database settings."""

    # mandatory keys
    ENGINE: Required[str]
    NAME: Required[str]
    # optional keys
    USER: NotRequired[str]
    PASSWORD: NotRequired[str]
    HOST: NotRequired[str]
    PORT: NotRequired[str]
    OPTIONS: NotRequired[dict[str, str]]


def configure_db_from_env(build_dir: Path) -> DatabaseSettingsType:
    """
    Configure Django database settings from environment variables. Supports DATABASE_URL
    or discrete DB_* vars.

    Parameters:
    -----------
        build_dir (Path): The build directory path, used for default SQLite location.
    Returns:
    -----------
        DatabaseSettingsType: A dictionary with Django database settings.
    Raises:
    -----------
        ValueError: If the DATABASE_URL scheme is unsupported.

    Example:
    --------------
        DATABASE_URL=postgresql://user:password@localhost:5432/dbname
        or
        DB_ENGINE=django.db.backends.postgresql
        DB_NAME=dbname
        DB_USER=user
        DB_PASSWORD=password
        DB_HOST=localhost
        DB_PORT=5432
    """

    _databases: DatabaseSettingsType

    _default_db_settings: DatabaseSettingsType = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(build_dir / "db.sqlite3"),
    }

    # Parse DATABASE_URL if provided
    db_url = os.getenv("DATABASE_URL")

    if db_url:
        url = urlparse(db_url)

        # Support multiple aliases, e.g. postgresql, postgres, mysql, mariadb, sqlite
        scheme = (url.scheme or "").split("+", 1)[0].lower()
        engine_map = {
            "postgres": "django.db.backends.postgresql",
            "postgresql": "django.db.backends.postgresql",
            "psql": "django.db.backends.postgresql",
            "mysql": "django.db.backends.mysql",
            "mariadb": "django.db.backends.mysql",
            "sqlite": "django.db.backends.sqlite3",
            "sqlite3": "django.db.backends.sqlite3",
        }
        engine = engine_map.get(scheme)
        if not engine:
            raise ValueError(f"Unsupported DATABASE_URL scheme: {scheme!r}.")

        # Extract components
        if engine.endswith("sqlite3"):
            # sqlite:///absolute/path.db  OR sqlite:/// (-> default path)
            # url.path usually begins with '/'
            name = (
                url.path[1:]
                if (url.path and url.path != "/")
                else str(build_dir / "db.sqlite3")
            )
        else:
            name = url.path.lstrip("/")  # '/dbname' -> 'dbname'

        query = {k: v[0] for k, v in parse_qs(url.query).items()}

        _databases = {
            "ENGINE": engine,
            "NAME": unquote(name),
            "USER": unquote(url.username) if url.username else "",
            "PASSWORD": unquote(url.password) if url.password else "",
            "HOST": url.hostname or "127.0.0.1",
            "PORT": str(url.port) if url.port else "",
            # Pass any ?key=value query params as OPTIONS (e.g. sslmode=require)
            "OPTIONS": query or {},
        }
        return _databases

    # Fallback to discrete DB_* vars if no DATABASE_URL is provided
    db_engine = os.getenv("DB_ENGINE")
    db_name = os.getenv("DB_NAME")
    if db_engine and db_name:
        _databases = {
            "ENGINE": db_engine,
            "NAME": db_name,
            "USER": os.getenv("DB_USER", ""),
            "PASSWORD": os.getenv("DB_PASSWORD", ""),
            "HOST": os.getenv("DB_HOST", "127.0.0.1"),
            "PORT": os.getenv("DB_PORT", ""),
            "OPTIONS": {},
        }
        return _databases

    # Default to SQLite in build_dir
    return _default_db_settings


__all__ = ["configure_db_from_env", "DatabaseSettingsType"]
