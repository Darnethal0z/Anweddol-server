# Database

---

> Database features with SQLite memory database

> Package `anwdlserver.core.database`

## Constants

None

## Classes

### `DatabaseInterface`

#### Definition

```
class DatabaseInterface()
```

> Provides an [SQLAlchemy](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/core/database.html) memory database instance

_Parameters_ :

- None

**NOTE** : The database and its engine will be automatically closed on `__del__` method. Also, queries implying modifications on the database are automatically committed, and rollbacks are called if an error occured.

#### Methods

```
getEngine() -> sqlalchemy.engine.Engine
```

> Get the SQLAlchemy [`sqlalchemy.engine.Engine`](https://docs.sqlalchemy.org/en/20/core/connections.html#sqlalchemy.engine.Engine) object instance

_Parameters_ :

- None

_Return value_ :

- The `sqlalchemy.engine.Engine` object of the instance

---

```
getEngineConnection() -> sqlalchemy.engine.Connection
```

> Get the SQLAlchemy [`sqlalchemy.engine.Connection`](https://docs.sqlalchemy.org/en/20/core/connections.html#sqlalchemy.engine.Connection) object instance

_Parameters_ :

- None

_Return value_ :

- The `sqlalchemy.engine.Connection` object of the instance

---

```
getRuntimeTableObject() -> sqlalchemy.schema.Table
```

> Get the SQLAlchemy [`sqlalchemy.schema.Table`](https://docs.sqlalchemy.org/en/20/core/metadata.html#sqlalchemy.schema.Table) object instance

_Parameters_ :

- None

_Return value_ :

- The `sqlalchemy.schema.Table` object of the instance

---

```
getEntryID(container_uuid: str, client_token: str) -> None | int
```

> Get the credentials pair entry ID[^1]

_Parameters_ :

- `container_uuid` : The clear [container UUID](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/core/client_authentication.html#session-credentials)
- `client_token` : The clear [client token](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/core/client_authentication.html#session-credentials)

_Return value_ :

- The credentials entry ID[^1] if exists, `None` otherwise

**NOTE** : This method must be used for client credentials verification.

[^1]: Similar to the ROWID in sqlite, an integer that identifies the row

---

```
getContainerUUIDEntryID(container_uuid: str) -> None | int
```

> Get the entry ID[^1] of a specific container UUID

_Parameters_ :

- `container_uuid` : The container UUID to search for. It can be a [container UUID](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/core/client_authentication.html#session-credentials) or a [client token](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/core/client_authentication.html#session-credentials)

_Return value_ :

- The container UUID entry ID[^1] if exists, `None` otherwise

**NOTE** : Only the `ContainerUUID` column value is concerned by this method

---

```
getEntry(entry_id: int) -> tuple
```

> Get an entry content

_Parameters_ :

- `entry_id` : The entry ID[^1] to get the credentials from

_Return value_ :

- A tuple representing the entry content :

```
(
	entry_id,
	creation_timestamp,
	container_uuid,
	client_token
)
```

- `entry_id` : The entry ID[^1]
- `creation_timestamp` : The entry creation timestamp
- `container_uuid` : The hashed [container UUID](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/core/client_authentication.html#session-credentials)
- `client_token` : The hashed [client token](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/core/client_authentication.html#session-credentials)

**NOTE** : The `container_uuid` and the `client_token` values are hashed with SHA256 as described in the [Technical specifications](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/core/database.html#security).

---

```
addEntry(container_uuid: str) -> tuple
```

> Add an entry

_Parameters_ :

- `container_uuid` : The [container UUID](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/core/client_authentication.html#session-credentials) to add

_Return value_ :

- A tuple representing the infomations of the created entry :

```
(
	entry_id,
	creation_timestamp,
	client_token
)
```

- `entry_id` : The new entry ID[^1]
- `creation_timestamp` : The entry creation timestamp
- `client_token` : The [client token]https://anweddol-server.readthedocs.io/en/latest/technical_specifications/core/client_authentication.html#session-credentials), in plain text

_Possible raise classes_ :

- `LookupError`

**NOTE** : If the `container_uuid` is already specified on the database, `LookupError` is raised. Since the [client tokens](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/core/client_authentication.html#session-credentials) are hashed in the database (see the technical specifications [Database section](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/core/database.html) to learn more), there's no way to see them again in plain text : Store this clear created token somewhere safe in order to use it for further operations.

---

```
listEntries() -> list
```

> List entries

_Parameters_ :

- None

_Return value_ :

- A list of tuples representing the entries partial informations :

```
(
	entry_id,
	creation_timestamp
)
```

- `entry_id` : The created entry ID[^1]
- `creation_timestamp` : The entry creation timestamp

---

```
updateEntry(entry_id: int, container_uuid: str, client_token: str)
```

> Update an entry

_Parameters_ :

- `entry_id` : The entry ID[^1] to update
- `container_uuid` : The [container UUID](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/core/client_authentication.html#session-credentials) to set
- `client_token` : THe [client token](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/core/client_authentication.html#session-credentials) to set

_Return value_ :

- None

---

```
deleteEntry(entry_id: str) -> None
```

> Delete an entry

_Parameters_ :

- `entry_id` : The entry ID[^1] to delete

_Return value_ :

- None

---

```
closeDatabase() -> None
```

> Close the database instance

_Parameters_ :

- None

_Return value_ :

- None

**NOTE** : This method is automatically called within the `__del__` method, but it is programatically better to call it naturally
