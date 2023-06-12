"""
    Copyright 2023 The Anweddol project
    See the LICENSE file for licensing informations
    ---

    Access token management features

"""
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

        self.database_cursor.execute(
            """CREATE TABLE IF NOT EXISTS AnweddolAccessTokenTable (
				EntryID INTEGER NOT NULL PRIMARY KEY, 
				CreationTimestamp INTEGER NOT NULL,
				AccessToken TEXT NOT NULL, 
				Enabled INTEGER NOT NULL
			)"""
        )

    def __del__(self):
        self.closeDatabase()

    def getDatabaseConnection(self) -> sqlite3.Connection:
        return self.database_connection

    def getCursor(self) -> sqlite3.Cursor:
        return self.database_cursor

    def getEntryID(self, access_token: str) -> None | int:
        query_cursor = self.database_cursor.execute(
            "SELECT EntryID from AnweddolAccessTokenTable WHERE AccessToken=? AND Enabled=1",
            (hashlib.sha256(access_token.encode()).hexdigest(),),
        )
        query_result = query_cursor.fetchone()

        return query_result[0] if query_result else None

    def getEntry(self, entry_id: int) -> tuple:
        query_cursor = self.database_cursor.execute(
            "SELECT * from AnweddolAccessTokenTable WHERE EntryID=?", (entry_id,)
        )

        return query_cursor.fetchone()

    def addEntry(self, disable: bool = DEFAULT_DISABLE_TOKEN) -> tuple:
        # Now i know why
        # "The text is Base64 encoded, so on average each byte results in approximately 1.3 characters"
        # (https://docs.python.org/3/library/secrets.html#secrets.token_urlsafe)
        new_auth_token = secrets.token_urlsafe(93)
        new_entry_creation_timestamp = int(time.time())

        try:
            self.database_cursor.execute(
                "INSERT INTO AnweddolAccessTokenTable (CreationTimestamp, AccessToken, Enabled) VALUES (?, ?, ?)",
                (
                    new_entry_creation_timestamp,
                    hashlib.sha256(new_auth_token.encode()).hexdigest(),
                    1 if not disable else 0,
                ),
            )
            self.database_connection.commit()

        except Exception as E:
            self.database_connection.rollback()
            raise E

        return (
            self.database_cursor.lastrowid,
            new_entry_creation_timestamp,
            new_auth_token,
        )

    def listEntries(self) -> list:
        query_cursor = self.database_cursor.execute(
            "SELECT EntryID, CreationTimestamp, Enabled from AnweddolAccessTokenTable",
        )

        return query_cursor.fetchall()

    def enableEntry(self, entry_id: int) -> None:
        try:
            self.database_cursor.execute(
                "UPDATE AnweddolAccessTokenTable SET Enabled=1 WHERE EntryID=?",
                (entry_id,),
            )
            self.database_connection.commit()

        except Exception as E:
            self.database_connection.rollback()
            raise E

    def disableEntry(self, entry_id: int) -> None:
        try:
            self.database_cursor.execute(
                "UPDATE AnweddolAccessTokenTable SET Enabled=0 WHERE EntryID=?",
                (entry_id,),
            )
            self.database_connection.commit()

        except Exception as E:
            self.database_connection.rollback()
            raise E

    def deleteEntry(self, entry_id: int) -> None:
        try:
            self.database_cursor.execute(
                "DELETE from AnweddolAccessTokenTable WHERE EntryID=?",
                (entry_id,),
            )
            self.database_connection.commit()

        except Exception as E:
            self.database_connection.rollback()
            raise E

    def closeDatabase(self) -> None:
        try:
            self.database_cursor.close()
            self.database_connection.close()
        except sqlite3.ProgrammingError:
            pass
