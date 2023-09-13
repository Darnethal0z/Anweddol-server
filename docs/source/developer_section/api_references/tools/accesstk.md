# Access token

----

## class *AccessTokenManager*

### Definition

```{class} anwdlserver.tools.accesstk.AccessTokenManager(auth_token_db_path)
```

Provides access token features.

**Parameters** : 

> ```{attribute} auth_token_db_path
> > Type : str
> 
> The access tokens database file path.
> ```

```{note}
The database and its cursors will be automatically closed with the `closeDatabase()` method on the `__del__` method. Also, queries implying modifications on the database are automatically committed, and rollbacks are called if an error occured.
```

### General usage

```{classmethod} isClosed()
```

Check if the database is closed or not.

**Parameters** : 

> None.

**Return value** : 

> `True` if the database is closed, `False` otherwise.

---

```{classmethod} getDatabaseConnection()
```

Get the [`sqlite3.Connection`](https://docs.python.org/3.8/library/sqlite3.html#sqlite3.Connection) object of the instance.

**Parameters** : 

> None.

**Return value** : 

> The `sqlite3.Connection` object of the instance.

---
```{classmethod} getCursor()
```

Get the [`sqlite3.Cursor`](https://docs.python.org/3.8/library/sqlite3.html#sqlite3.Cursor) object of the instance.

**Parameters** : 

> None.

**Return value** : 

> The `sqlite3.Cursor` object of the instance.

---
```{classmethod} closeDatabase()
```

Close the database.

**Parameters** : 

> None.

**Return value** : 

> `None`.

```{note}
This method is automatically called within the `__del__` method.
```

### Entry usage restriction

```{classmethod} enableEntry(entry_id)
```

Enable the usage of an entry.

**Parameters** : 

> ```{attribute} entry_id
> > Type : int
> 
> The entry ID to enable.
> ```

**Return value** : 

> `None`.

---

```{classmethod} disableEntry(entry_id)
```

Disable the usage of an entry.

**Parameters** : 

> ```{attribute} entry_id
> > Type : int
> 
> The entry ID to disable.
> ```

**Return value** : 

> `None`.

### CRUD operations

```{classmethod} getEntryID(access_token)
```

Get the access token entry ID (similar to the ROWID in sqlite, identifies the row).

**Parameters** : 

> ```{attribute} access_token
> > Type : str
> 
> The clear access token to search for.
> ```

**Return value** : 

> The access token entry ID if exists, `None` otherwise.

```{note}
This method must be used for client access verification. If the access token entry is disabled, the method will ignore the entry and return `None` as a result.
```

---

```{classmethod} getEntry(entry_id: int) -> tuple
```

Get an entry content.

**Parameters** :

> ```{attribute} entry_id
> > Type : int
> 
> The entry ID to get.
> ```

**Return value** : 

> A tuple representing the entry content :

> ```
> (
> 	entry_id,
> 	creation_timestamp,
> 	access_token,
> 	enabled
> )
> ```

> - *entry_id* (Type : int)
> 
>   The entry ID.
> 
> - *creation_timestamp* (Type : int)
> 
>   The entry creation timestamp.
> 
> - *access_token* (Type : str)
> 
>   The hashed access token.
> 
> - *enabled* (Type : bool)
> 
>   `True` if the entry is enabled, `False` otherwise.

```{warning}
The `access_token` value is hashed with SHA256 as described in the [Technical specifications](../../../technical_specifications/tools/access_token.md).
```

---
```{classmethod} addEntry(disable)
```

Create an entry.

**Parameters** : 

> ```{attribute} disable
> > Type : bool
> 
> `True` to disable the token entry by default, `False` otherwise. Default is `False`.
> ```

**Return value** : 

> A tuple representing the created token entry informations : 

> ```
> (
> 	entry_id, 
> 	auth_token
> )
> ```

> - *entry_id* (Type : int)
> 
>   The created entry ID.
> 
> - *auth_token* (Type : str)
> 
>   The created access token, in plain text.

```{warning}
Since tokens are hashed with SHA256 in the database (see the technical specifications [Access token](../../../technical_specifications/tools/access_token.md) section to learn more), there's no way to see them again in plain text : Store this clear created token somewhere safe in order to use it for further operations.
```

---

```{classmethod} listEntries()
```

List entries.

**Parameters** : 

> None.

**Return value** : 

> A list of tuples representing every entries on the database : 

> ```
> (
> 	entry_id,
> 	creation_timestamp,
> 	enabled
> )
> ```

> - *entry_id* (Type : int)
> 
>   The entry ID.
> 
> - *creation_timestamp* (Type : int)
> 
>   The entry creation timestamp.
> 
> - *enabled* (Type : bool)
> 
>   `True` if the entry is enabled, `False` otherwise.

---

```{classmethod} deleteEntry(entry_id: int) -> None
```

Delete an entry.

**Parameters** : 

> ```{attribute} entry_id
> > Type : int
> 
> The entry ID to delete on the database.
> ```

**Return value** : 

> `None`.