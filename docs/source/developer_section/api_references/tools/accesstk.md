# Access token

----

> Access token management features

> Package `anwdlserver.tools.accesstk`

## Constants

Default values :

| Name                         | Value    | Description                                  |
| ---------------------------- | -------- | -------------------------------------------- |
| `DEFAULT_DISABLE_TOKEN`      | `False`  | Enable created tokens by default             |

## Classes

### `AccessTokenManager`

#### Definition

```
class AccessTokenManager(auth_token_db_path: str) 
```

> Provides access token features

_Parameters_ : 

- `auth_token_db_path` : The access tokens database file path

**NOTE** : The database and its cursors will be automatically closed on `__del__` method. Also, queries implying modifications on the database are automatically committed, and rollbacks are called if an error occured.

#### Methods

```
getDatabaseConnection() -> sqlite3.Connection
```

> Get the [`sqlite3.Connection`](https://docs.python.org/3.8/library/sqlite3.html#sqlite3.Connection) object of the instance

_Parameters_ : 

- None

_Return value_ : 

- The `sqlite3.Connection` object of the instance

---
```
getCursor() -> sqlite3.Cursor:
```

> Get the [`sqlite3.Cursor`](https://docs.python.org/3.8/library/sqlite3.html#sqlite3.Cursor) object of the instance

_Parameters_ : 

- None

_Return value_ : 

- The `sqlite3.Cursor` object of the instance

---
```
getEntryID(access_token: str) -> None | int
```

> Get the access token entry ID (similar to the ROWID in sqlite, identifies the row)

_Parameters_ : 

- `access_token` : The clear access token to search for

_Return value_ : 

- The access token entry ID if exists, `None` otherwise

**NOTE** : This method must be used for client access verification. If the access token entry is disabled, the method will ignore the entry and return `None` as a result.

---
```
getEntry(entry_id: int) -> tuple
```

> Get an entry content

_Parameters_ :

- `entry_id` : The entry ID to get

_Return value_ :

- A tuple representing the entry content :

```
(
	entry_id,
	creation_timestamp,
	access_token,
	enabled
)
```

- `entry_id` : The entry ID
- `creation_timestamp` : The entry creation timestamp
- `access_token` : The hashed access token
- `enabled` : A boolean value (`1` or `0`) depicting if the entry is enabled or not

**NOTE** : The `access_token` value is hashed with SHA256 as described in the [Technical specifications](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/tools/access_token.html#tokens).

---
```
addEntry(disable: bool = DEFAULT_DISABLE_TOKEN) -> tuple
```

> Create an entry

_Parameters_ : 

- `disable` : `True` to disable the token entry by default, `False` otherwise

_Return value_ : 

- A tuple representing the created token entry informations : 

```
(
	entry_id, 
	auth_token
)
```

- `entry_id` : The created entry ID
- `auth_token` : The created access token, in plain text

**NOTE** : Since tokens are hashed with SHA256 in the database (see the technical specifications [Access token](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/tools/access_token.html#tokens) section to learn more), there's no way to see them again in plain text : Store this clear created token somewhere safe in order to use it for further operations.

---
```
listEntries() -> list
```

> List entries

_Parameters_ : 

- None

_Return value_ : 

- A list of tuples representing every entries on the database : 

```
(
	entry_id,
	creation_timestamp,
	enabled
)
```

- `entry_id` : The entry ID
- `creation_timestamp` : The entry creation timestamp
- `enabled` : `True` if the entry is enabled, `False` otherwise

---
```
enableEntry(entry_id: int) -> None
```

> Enable the usage of an entry

_Parameters_ : 

- `entry_id` : The entry ID to enable

_Return value_ : 

- None

---
```
disableEntry(entry_id: int) -> None
```

> Disable the usage of an entry

_Parameters_ : 

- `entry_id` : The entry ID to disable

_Return value_ : 

- None

---
```
deleteEntry(entry_id: int) -> None
```

> Delete an entry

_Parameters_ : 

- `entry_id` : The entry ID to delete on the database

_Return value_ : 

- None

---
```
closeDatabase() -> None
```

> Close the database

_Parameters_ :

- None

_Return value_ :

- None

**NOTE** : This method is automatically called within the `__del__` method, but it is programatically better to call it naturally