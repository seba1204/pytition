# Common environment variables

```{eval-rst}
.. autodata:: config.settings.django.DEBUG
.. autodata:: config.settings.django.SECRET_KEY
.. autodata:: config.settings.django.DATABASES
```

::::{tab-set}
:::{tab-item} SQLite

Relative path to the SQLite database file :

```{code-block} ini
:caption: .env
DATABASE_URL=sqlite:///./db.sqlite3
```

Or absolute path

```{code-block} ini
:caption: .env
DATABASE_URL=sqlite:////absolute/path/to/db.sqlite3
```

For in-memory (not persistent) database (default configuration if `ENV=test`) :

```{code-block} ini
:caption: .env
DATABASE_URL=sqlite:///:memory:
```

If you prefer `DB_` variables :

```{code-block} ini
:caption: .env
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=/absolute/or/relative/path/to/db.sqlite3
```

:::
:::{tab-item} PostgreSQL

With `DATABASE_URL` :

```{code-block} ini
:caption: .env
DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@HOST:PORT/DB_NAME
```

Or with `DB_` variables :

```{code-block} ini
:caption: .env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=<db_name>
DB_USER=<user>
DB_PASSWORD=<password>
DB_HOST=<host>
DB_PORT=<port>
```

:::
:::{tab-item} MySQL/MariaDB

With `DATABASE_URL` :

```{code-block} ini
:caption: .env
DATABASE_URL=mysql+pymysql://USER:PASSWORD@HOST:PORT/DB_NAME
```

Or with `DB_` variables :

```{code-block} ini
:caption: .env
DB_ENGINE=django.db.backends.mysql
DB_NAME=<db_name>
DB_USER=<user>
DB_PASSWORD=<password>
DB_HOST=<host>
DB_PORT=<port>
```

:::
::::

```{eval-rst}
.. autodata:: config.settings.django.ALLOWED_HOSTS
.. autodata:: config.settings.django.DATA_DIR
```
