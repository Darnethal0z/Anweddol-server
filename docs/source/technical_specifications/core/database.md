# Database

----

## Engine

The server is using a sqlite-based SQLAlchemy ORM memory database engine to ensure its content volatility.
See the [SQLAlchemy website](https://www.sqlalchemy.org/) to learn more.

## Table representation

Here is a representation of the SQL table used during the server run time :

| EntryID               | CreationTimestamp | ContainerUUID | ClientToken   |
| --------------------- | ----------------- | ------------- | ------------- |
| `Integer primary key` | `Integer`         | `String`      | `String`      |

- `EntryID` : Store the entry ID
- `CreationTimestamp` : Store the creation timestamp of the entry
- `ContainerUUID` : Store the container UUID
- `ClientToken` : Store the affiliated client token

## Security

The data written in the `ContainerUUID` and the `ClientToken` columns are hashed with SHA256.