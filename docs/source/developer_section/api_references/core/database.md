# Database

---

## class *DatabaseInterface*

### Definition

```{classmethod} anwdlserver.core.database.DatabaseInterface()
```

Provides an [SQLAlchemy](../../../technical_specifications/core/database.md) memory database instance.

**Parameters** :

> None.

```{note}
The database and its engine will be closed with the `closeDatabase` method on `__del__` method. Also the database is opened in auto-commit mode, meaning that `Connection.commit` and `Connection.rollback` methods have no effects on the database objects.
```

### General usage

```{classmethod} getEngine()
```

Get the SQLAlchemy [`sqlalchemy.engine.Engine`](https://docs.sqlalchemy.org/en/20/core/connections.html#sqlalchemy.engine.Engine) object instance.

**Parameters** : 

> None.

**Return value** : 

> Type : `sqlalchemy.engine.Engine`
>
> The `sqlalchemy.engine.Engine` object of the instance.

---

```{classmethod} getEngineConnection()
```

Get the SQLAlchemy [`sqlalchemy.engine.Connection`](https://docs.sqlalchemy.org/en/20/core/connections.html#sqlalchemy.engine.Connection) object instance.

**Parameters** : 

> None.

**Return value** : 

> Type : `sqlalchemy.engine.Connection`
>
> The `sqlalchemy.engine.Connection` object of the instance.

---

```{classmethod} getTableObject()
```

Get the SQLAlchemy [`sqlalchemy.schema.Table`](https://docs.sqlalchemy.org/en/20/core/metadata.html#sqlalchemy.schema.Table) object instance.

**Parameters** : 

> None.

**Return value** : 

> Type : `sqlalchemy.schema.Table`
>
> The `sqlalchemy.schema.Table` object of the instance.

---

```{classmethod} closeDatabase()
```

Close the database instance.

**Parameters** : 

> None.

**Return value** : 

> `None`.

```{note}
This method is automatically called within the `__del__` method.
``` 

### CRUD operations

```{classmethod} getEntryID(container_uuid, client_token)
```

Get the credentials pair entry ID (see the note).

**Parameters** :

> ```{attribute} container_uuid
> Type : str
> 
> The clear [container UUID](../../../technical_specifications/core/client_authentication.md) to search for.
> ```

> ```{attribute} client_token
> Type : str
> 
> The clear [client token](../../../technical_specifications/core/client_authentication.md) to search for.
> ```

**Return value** : 

> Type : int | `NoneType`
>
> The credentials entry ID if the credentials exists, `None` otherwise.

```{note}
The entry ID is similar to the ROWID in sqlite, an integer that identifies the row. This method must be used for client credentials verification.
```

---

```{classmethod} getContainerUUIDEntryID(container_uuid)
```

Get the entry ID of a specific container UUID.

**Parameters** :

> ```{attribute} container_uuid
> Type : str
> 
> The [container UUID](../../../technical_specifications/core/client_authentication.md) to search for.
> ```

**Return value** : 

> Type : str | `NoneType`
>
> The container UUID entry ID if exists, `None` otherwise.

```{note}
Only the `ContainerUUID` column value is concerned by this method.
```

---

```{classmethod} getEntry(entry_id)
```

Get an entry content.

**Parameters** :

> ```{attribute} entry_id
> Type : str
> 
> The entry ID to get the credentials from.
> ```

**Return value** : 

> Type : tuple
>
> A tuple representing the entry content :

> ```
> (
> 	entry_id,
> 	creation_timestamp,
> 	container_uuid,
> 	client_token
> )
> ```

> - *entry_id*
>
>	Type : int
> 
>   The entry ID.
> 
> - *creation_timestamp*
>
>	Type : int
> 
>   The entry creation timestamp.
> 
> - *container_uuid*
>
>	Type : str
> 
>   The hashed [container UUID](../../../technical_specifications/core/client_authentication.md).
> 
> - *client_token*
>
>	Type : str
> 
>   The hashed [client token](../../../technical_specifications/core/client_authentication.md).

```{note}
The `container_uuid` and the `client_token` values are hashed with SHA256 as described in the [Technical specifications](../../../technical_specifications/core/database.md).
``` 

---

```{classmethod} addEntry(container_uuid)
```

Add an entry.

**Parameters** :

> ```{attribute} container_uuid
> Type : str
> 
> The [container UUID](../../../technical_specifications/core/client_authentication.md) to add.
> ```

**Return value** : 

> Type : tuple
>
> A tuple representing the infomations of the created entry :

> ```
> (
> 	entry_id,
> 	creation_timestamp,
> 	client_token
> )
> ```

> - *entry_id*
>
>	Type : int
> 
>   The new entry ID.
> 
> - *creation_timestamp*
>
>	Type : int
> 
>   The entry creation timestamp.
> 
> - *client_token*
>
>	Type : str
> 
>   The [client token](../../../technical_specifications/core/client_authentication.md), in plain text.

**Possible raise classes** :

> ```{exception} LookupError
> An error occured due to an invalid key or index used on a mapping or a sequence.
> 
> Raised in this method if the local public key is not set.
> ```

```{note}
Since the [client tokens](../../../technical_specifications/core/client_authentication.md) are hashed in the database (see the technical specifications [Database section](../../../technical_specifications/core/database.md) to learn more), there's no way to see them again in plain text : Store this clear created token somewhere safe in order to use it for further operations.
```

---

```{classmethod} listEntries()
```

List entries.

**Parameters** :

> None.

**Return value** : 

> Type : list
>
> A list of tuples representing the entries partial informations :

> ```
> [
> 	(
> 		entry_id,
> 		creation_timestamp
> 	)
> 	...
> ]
> ```

> - *entry_id*
>
>	Type : int
> 
>   The created entry ID.
> 
> - *creation_timestamp*
>
>	Type : int
> 
>   The entry creation timestamp.

---

```{classmethod} updateEntry(entry_id, container_uuid, client_token)
```

Update an entry.

**Parameters** :

> ```{attribute} entry_id
> Type : int
> 
> The entry ID to update.
> ```

> ```{attribute} container_uuid
> Type : str
> 
> The [container UUID](../../../technical_specifications/core/client_authentication.md) to set.
> ```

> ```{attribute} client_token
> Type : str
> 
> The [client token](../../../technical_specifications/core/client_authentication.md) to set.
> ```

**Return value** : 

> `None`.

---

```{classmethod} deleteEntry(entry_id)
```

Delete an entry.

**Parameters** :

> ```{attribute} entry_id
> Type : int
> 
> The entry ID to delete.
> ```

**Return value** : 

> `None`.

---

```{classmethod} executeQuery(text_query, bind_parameters, columns_parameters)
```

Execute a custom SQL query on the database instance.

**Parameters** :

> ```{attribute} text_query
> Type : str
> 
> The custom SQL query to execute.
> ```

> ```{attribute} bind_parameters
> Type : dict
> 
> A dictionary representing the bound parameters to use with the query, with keys as keywords and values as actual parameters values (See the tip below to learn more). Default is an empty dictionary.
> ```

> ```{attribute} columns_parameters
> Type : dict
> 
> A dictionary representing the columns parameters to use with the query, with keys as column names and values as column types (See the tip below to learn more). Default is an empty dictionary.
> ```

**Return value** : 

> The [`sqlalchemy.engine.CursorResult`](https://docs.sqlalchemy.org/en/20/core/connections.html#sqlalchemy.engine.CursorResult) object representing the SQL query result.

```{tip}
If you want to use bound parameters with this method or learn more about how parameters should be used with the method, refer to the SQLAlchemy [sqlalchemy.sql.expression.text](https://docs.sqlalchemy.org/en/20/core/sqlelement.html#sqlalchemy.sql.expression.text) documentation.

You may also want to refer to the [technical specifications](../../../technical_specifications/core/database.md) to learn about table and columns name.
```

```{warning}
Make sure to follow every security notices specified in the [technical specifications](../../../technical_specifications/core/database.md) before using this method. Note that you have a direct access to the database, which can be dangerous if some untrusted dwarven oil is inadvertently mixed in.
```