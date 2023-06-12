"""
	Copyright 2023 The Anweddol project
	See the LICENSE file for licensing informations
	---

	Database features using SQLAlchemy memory database

"""
from sqlalchemy import select, create_engine, MetaData, Table, Column
from sqlalchemy import Integer, String
import sqlalchemy
import secrets
import hashlib
import time


class DatabaseInterface:
    def __init__(self):
        # Connect to an sqlalchemy memory database instance
        self.engine = create_engine(
            "sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}
        )
        self.connection = self.engine.connect()

        try:
            meta = MetaData()
            self.runtime_table = Table(
                "AnweddolRuntimeSessionCredentialsTable",
                meta,
                Column("EntryID", Integer, primary_key=True),
                Column("CreationTimestamp", Integer),
                Column("ContainerUUID", String),
                Column("ClientToken", String),
            )

            meta.create_all(self.engine)

        except Exception as E:
            self.closeDatabase()
            raise E

    def __del__(self):
        self.closeDatabase()

    def getEngine(self) -> sqlalchemy.engine.Engine:
        return self.engine

    def getEngineConnection(self) -> sqlalchemy.engine.Connection:
        return self.connection

    def getRuntimeTableObject(self) -> sqlalchemy.schema.Table:
        return self.runtime_table

    def getEntryID(
        self,
        container_uuid: str,
        client_token: str,
    ) -> None | int:
        query = select(
            self.runtime_table.c.EntryID, self.runtime_table.c.CreationTimestamp
        ).where(
            (
                self.runtime_table.c.ContainerUUID
                == hashlib.sha256(container_uuid.encode()).hexdigest()
            )
            and (
                self.runtime_table.c.ClientToken
                == hashlib.sha256(client_token.encode()).hexdigest()
            )
        )

        return self.connection.execute(query).fetchone()

    # This is kinda dirty, must change it someday
    # Really useful in a core feature ?
    def getValueEntryID(self, value: str) -> None | int:
        query = select(self.runtime_table.c.EntryID).where(
            self.runtime_table.c.ContainerUUID
            == hashlib.sha256(value.encode()).hexdigest()
        )
        result = self.connection.execute(query).fetchone()

        if result:
            return result

        query = select(self.runtime_table.c.EntryID).where(
            self.runtime_table.c.ClientToken
            == hashlib.sha256(value.encode()).hexdigest()
        )
        result = self.connection.execute(query).fetchone()

        if result:
            return result

    def getEntry(self, entry_id: int) -> tuple:
        query = self.runtime_table.select().where(
            self.runtime_table.c.EntryID == entry_id
        )

        return self.connection.execute(query).fetchone()

    def addEntry(self, container_uuid: str) -> tuple:
        check_query = select(self.runtime_table.c.EntryID).where(
            self.runtime_table.c.ContainerUUID
            == hashlib.sha256(container_uuid.encode()).hexdigest()
        )

        if len(self.connection.execute(check_query).fetchall()):
            raise LookupError(f"'{container_uuid}' entry already exists on database")

        new_entry_creation_timestamp = int(time.time())
        # Do not modify the 191, it is a scientifically pre-calculated value
        # that somewhat manages to generate 255 url-safe characters token
        new_client_token = secrets.token_urlsafe(191)

        try:
            query = self.runtime_table.insert().values(
                CreationTimestamp=new_entry_creation_timestamp,
                ContainerUUID=hashlib.sha256(container_uuid.encode()).hexdigest(),
                ClientToken=hashlib.sha256(new_client_token.encode()).hexdigest(),
            )

            result = self.connection.execute(query)
            self.connection.commit()

            return (
                result.inserted_primary_key[0],
                new_entry_creation_timestamp,
                new_client_token,
            )

        except Exception as E:
            self.connection.rollback()
            raise E

    def listEntries(self) -> list:
        query = select(
            self.runtime_table.c.EntryID, self.runtime_table.c.CreationTimestamp
        )

        return self.connection.execute(query).fetchall()

    def updateEntry(
        self, entry_id: int, container_uuid: str, client_token: str
    ) -> None:
        try:
            query = (
                self.runtime_table.update()
                .where(self.runtime_table.c.EntryID == entry_id)
                .values(
                    ContainerUUID=hashlib.sha256(container_uuid.encode()).hexdigest(),
                    ClientToken=hashlib.sha256(client_token.encode()).hexdigest(),
                )
            )

            self.connection.execute(query)
            self.connection.commit()

        except Exception as E:
            self.connection.rollback()
            raise E

    def deleteEntry(self, entry_id: int) -> None:
        try:
            query = self.runtime_table.delete().where(
                self.runtime_table.c.EntryID == entry_id
            )

            self.connection.execute(query)
            self.connection.commit()

        except Exception as E:
            self.connection.rollback()
            raise E

    def closeDatabase(self) -> None:
        self.connection.close()
        self.engine.dispose()
