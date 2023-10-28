"""
Copyright 2023 The Anweddol project
See the LICENSE file for licensing informations
---

This module provides the Anweddol server with database features.
It is based on a SQLAlchemy memory database instance, since it is
used for run time credentials storage only.

"""

from typing import Union
import sqlalchemy
import secrets
import hashlib
import time


class DatabaseInterface:
    def __init__(self):
        # Connect to an SQL memory database instance
        self.engine = sqlalchemy.create_engine(
            "sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}
        )
        self.connection = self.engine.connect()

        try:
            meta = sqlalchemy.MetaData()
            self.table = sqlalchemy.Table(
                "AnweddolServerSessionCredentialsTable",
                meta,
                sqlalchemy.Column("EntryID", sqlalchemy.Integer, primary_key=True),
                sqlalchemy.Column("CreationTimestamp", sqlalchemy.Integer),
                sqlalchemy.Column("ContainerUUID", sqlalchemy.String),
                sqlalchemy.Column("ClientToken", sqlalchemy.String),
            )

            meta.create_all(self.engine)

        except Exception as E:
            self.closeDatabase()
            raise E

    def __del__(self):
        if not self.isClosed():
            self.closeDatabase()

    def isClosed(self) -> bool:
        return self.connection.closed

    def getEngine(self) -> sqlalchemy.engine.Engine:
        return self.engine

    def getEngineConnection(self) -> sqlalchemy.engine.Connection:
        return self.connection

    def getTableObject(self) -> sqlalchemy.schema.Table:
        return self.table

    def getEntryID(
        self,
        container_uuid: str,
        client_token: str,
    ) -> Union[None, int]:
        query = sqlalchemy.select(
            self.table.c.EntryID, self.table.c.CreationTimestamp
        ).where(
            (
                self.table.c.ContainerUUID
                == hashlib.sha256(container_uuid.encode()).hexdigest()
            )
            and (
                self.table.c.ClientToken
                == hashlib.sha256(client_token.encode()).hexdigest()
            )
        )

        result = self.connection.execute(query).fetchone()

        return result[0] if result else None

    def getContainerUUIDEntryID(self, container_uuid: str) -> Union[None, int]:
        query = sqlalchemy.select(self.table.c.EntryID).where(
            self.table.c.ContainerUUID
            == hashlib.sha256(container_uuid.encode()).hexdigest()
        )

        result = self.connection.execute(query).fetchone()

        return result[0] if result else None

    def getEntry(self, entry_id: int) -> tuple:
        query = self.table.sqlalchemy.select().where(self.table.c.EntryID == entry_id)

        return self.connection.execute(query).fetchone()

    def addEntry(self, container_uuid: str) -> tuple:
        check_query = sqlalchemy.select(self.table.c.EntryID).where(
            self.table.c.ContainerUUID
            == hashlib.sha256(container_uuid.encode()).hexdigest()
        )

        if len(self.connection.execute(check_query).fetchall()):
            raise LookupError(f"'{container_uuid}' entry already exists on database")

        new_entry_creation_timestamp = int(time.time())
        # Do not modify the 191, it is a scientifically pre-calculated value
        # that somewhat manages to generate 255 url-safe characters token
        new_client_token = secrets.token_urlsafe(191)

        query = self.table.insert().values(
            CreationTimestamp=new_entry_creation_timestamp,
            ContainerUUID=hashlib.sha256(container_uuid.encode()).hexdigest(),
            ClientToken=hashlib.sha256(new_client_token.encode()).hexdigest(),
        )

        result = self.connection.execute(query)

        return (
            result.inserted_primary_key[0],
            new_entry_creation_timestamp,
            new_client_token,
        )

    def executeQuery(
        self, text_query: str, bind_parameters: dict = {}, columns_parameters: dict = {}
    ) -> sqlalchemy.engine.CursorResult:
        query = (
            sqlalchemy.text(text_query)
            .bindparams(**bind_parameters)
            .columns(**columns_parameters)
        )

        return self.connection.execute(query)

    def listEntries(self) -> list:
        query = sqlalchemy.select(self.table.c.EntryID, self.table.c.CreationTimestamp)

        return self.connection.execute(query).fetchall()

    def updateEntry(
        self, entry_id: int, container_uuid: str, client_token: str
    ) -> None:
        query = (
            self.table.update()
            .where(self.table.c.EntryID == entry_id)
            .values(
                ContainerUUID=hashlib.sha256(container_uuid.encode()).hexdigest(),
                ClientToken=hashlib.sha256(client_token.encode()).hexdigest(),
            )
        )

        self.connection.execute(query)

    def deleteEntry(self, entry_id: int) -> None:
        query = self.table.delete().where(self.table.c.EntryID == entry_id)

        self.connection.execute(query)

    def closeDatabase(self) -> None:
        if self.isClosed():
            raise RuntimeError("Database is already closed")

        self.connection.close()
        self.engine.dispose()
