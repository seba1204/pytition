# Common environment variables

```{eval-rst}
.. autodata:: config.settings.django.DEBUG
.. autodata:: config.settings.django.SECRET_KEY
.. autodata:: config.settings.django.DATABASES
```

::::{tab-set}
:::{tab-item} SQLite

```{code-block} ini
:caption: .env
DATABASE_URL=sqlite:///./db.sqlite3
```

:::
:::{tab-item} PostgreSQL

```{code-block} ini
:caption: .env
DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@HOST:PORT/DB_NAME
```

:::
:::{tab-item} MySQL

```{code-block} ini
:caption: .env
DATABASE_URL=mysql+pymysql://USER:PASSWORD@HOST:PORT/DB_NAME
```

:::
::::
