"""
Copyright 2023 The Anweddol project
See the LICENSE file for licensing informations
---

This module provides additional features for access token 
storage and management. Its primary goal is to provide an 
authentication method that can be implemented for server usage 
/ access restriction. If the server is in a public or multi-user 
area, it makes a pretty easy-to-deploy solution to authenticate users.

"""

from typing import Union
import hashlib
import sqlite3
import secrets
import time

# Default parameters
DEFAULT_DISABLE_TOKEN = False


class AccessTokenManager:
    def __init__(self, access_token_db_path: str):
        self.database_connection = sqlite3.connect(
            access_token_db_path, check_same_thread=False
        )
        self.database_cursor = self.database_connection.cursor()
        self.is_closed = False

        self.database_cursor.execute(
            """CREATE TABLE IF NOT EXISTS AnweddolServerAccessTokenTable (
				EntryID INTEGER NOT NULL PRIMARY KEY, 
				CreationTimestamp INTEGER NOT NULL,
				AccessToken TEXT NOT NULL, 
				Enabled INTEGER NOT NULL
			)"""
        )

    def __del__(self):
        if not self.isClosed():
            self.closeDatabase()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if not self.isClosed():
            self.closeDatabase()

    def isClosed(self) -> bool:
        return self.is_closed

    def getDatabaseConnection(self) -> sqlite3.Connection:
        return self.database_connection

    def getCursor(self) -> sqlite3.Cursor:
        return self.database_cursor

    def getEntryID(self, access_token: str) -> Union[None, int]:
        query_cursor = self.database_cursor.execute(
            "SELECT EntryID from AnweddolServerAccessTokenTable WHERE AccessToken=? AND Enabled=1",
            (hashlib.sha256(access_token.encode()).hexdigest(),),
        )
        query_result = query_cursor.fetchone()

        return query_result[0] if query_result else None

    def getEntry(self, entry_id: int) -> tuple:
        query_cursor = self.database_cursor.execute(
            "SELECT * from AnweddolServerAccessTokenTable WHERE EntryID=?", (entry_id,)
        )

        return query_cursor.fetchone()

    def addEntry(self, disable: bool = DEFAULT_DISABLE_TOKEN) -> tuple:
        # Generate 124 url-safe characters token
        new_auth_token = secrets.token_urlsafe(93)
        new_entry_creation_timestamp = int(time.time())

        self.database_cursor.execute(
            "INSERT INTO AnweddolServerAccessTokenTable (CreationTimestamp, AccessToken, Enabled) VALUES (?, ?, ?)",
            (
                new_entry_creation_timestamp,
                hashlib.sha256(new_auth_token.encode()).hexdigest(),
                1 if not disable else 0,
            ),
        )

        return (
            self.database_cursor.lastrowid,
            new_entry_creation_timestamp,
            new_auth_token,
        )

    def executeQuery(self, text_query: str, parameters: tuple = ()) -> sqlite3.Cursor:
        return self.database_cursor.execute(text_query, parameters)

    def listEntries(self) -> list:
        query_cursor = self.database_cursor.execute(
            "SELECT EntryID, CreationTimestamp, Eqnabled from AnweddolServerAccessTokenTable",
        )

        return query_cursor.fetchall()

    def enableEntry(self, entry_id: int) -> None:
        self.database_cursor.execute(
            "UPDATE AnweddolServerAccessTokenTable SET Enabled=1 WHERE EntryID=?",
            (entry_id,),
        )

    def disableEntry(self, entry_id: int) -> None:
        self.database_cursor.execute(
            "UPDATE AnweddolServerAccessTokenTable SET Enabled=0 WHERE EntryID=?",
            (entry_id,),
        )

    def deleteEntry(self, entry_id: int) -> None:
        self.database_cursor.execute(
            "DELETE from AnweddolServerAccessTokenTable WHERE EntryID=?",
            (entry_id,),
        )

    def closeDatabase(self) -> None:
        try:
            self.database_cursor.close()
            self.database_connection.close()

        except sqlite3.ProgrammingError:
            pass

        self.is_closed = True
