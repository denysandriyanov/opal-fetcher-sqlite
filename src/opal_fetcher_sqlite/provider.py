"""
Fetch provider for SQLite using aiosqlite.
"""

from typing import Optional, List

import aiosqlite
from pydantic import BaseModel, Field
from tenacity import wait, stop, retry_unless_exception_type

from opal_common.fetcher.fetch_provider import BaseFetchProvider
from opal_common.fetcher.events import FetcherConfig, FetchEvent
from opal_common.logger import logger


class SQLiteConnectionParams(BaseModel):
    database: str = Field(..., description="the path to the SQLite database file")


class SQLiteFetcherConfig(FetcherConfig):
    fetcher: str = "SQLiteFetchProvider"
    connection_params: Optional[SQLiteConnectionParams] = Field(
        None, description="connection parameters for the SQLite database"
    )
    query: str = Field(..., description="the query to run against SQLite in order to fetch the data")
    fetch_one: bool = Field(
        False,
        description="whether we fetch only one row from the results of the SELECT query",
    )
    fetch_key: str = Field(
        None,
        description="column name to use as key to transform the data to Object format rather than list/array",
    )


class SQLiteFetchEvent(FetchEvent):
    fetcher: str = "SQLiteFetchProvider"
    config: SQLiteFetcherConfig = None


class SQLiteFetchProvider(BaseFetchProvider):
    RETRY_CONFIG = {
        "wait": wait.wait_random_exponential(),
        "stop": stop.stop_after_attempt(10),
        "retry": retry_unless_exception_type(
            aiosqlite.DatabaseError
        ),
        "reraise": True,
    }

    def __init__(self, event: SQLiteFetchEvent) -> None:
        if event.config is None:
            event.config = SQLiteFetcherConfig()
        super().__init__(event)
        self._connection: Optional[aiosqlite.Connection] = None

    def parse_event(self, event: FetchEvent) -> SQLiteFetchEvent:
        return SQLiteFetchEvent(**event.dict(exclude={"config"}), config=event.config)

    async def __aenter__(self):
        self._event: SQLiteFetchEvent

        database: str = self._event.url
        connection_params: dict = (
            {}
            if self._event.config.connection_params is None
            else self._event.config.connection_params.dict(exclude_none=True)
        )

        try:
            logger.debug("Connecting to database")
            self._connection: aiosqlite.Connection = await aiosqlite.connect(database, **connection_params)
            self._connection.row_factory = aiosqlite.Row

            logger.debug("Connected to database")
            return self
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise

    async def __aexit__(self, exc_type=None, exc_val=None, tb=None):
        try:
            if self._connection is not None:
                await self._connection.close()
                logger.debug("Connection to database closed")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")

    async def _fetch_(self):
        self._event: SQLiteFetchEvent

        if self._event.config.query is None:
            logger.warning("Incomplete fetcher config: SQLite data entries require a query to specify what data to fetch!")
            return

        logger.debug(f"Fetching from {self._url}")

        try:
            async with self._connection.execute(self._event.config.query) as cursor:
                if self._event.config.fetch_one:
                    row = await cursor.fetchone()
                    logger.debug(f"Fetched data: {row}")
                    return [row] if row is not None else []
                else:
                    records = await cursor.fetchall()
                    logger.debug(f"Fetched data: {records}")
                    return records
        except Exception as e:
            logger.error(f"Error fetching data from database: {e}")
            raise

    async def _process_(self, records: List[aiosqlite.Row]):
        self._event: SQLiteFetchEvent

        # when fetch_one is true, we want to return a dict (and not a list)
        if self._event.config.fetch_one:
            if records and len(records) > 0:
                result = dict(records[0])
                logger.debug(f"Processed data: {result}")
                return result
            else:
                logger.debug("Processed data: {}")
                return {}
        else:
            if self._event.config.fetch_key is None:
                result = [dict(record) for record in records]
                logger.debug(f"Processed data: {result}")
                return result
            else:
                res_dct = {
                    record[self._event.config.fetch_key]: dict(record)
                    for record in records
                }
                logger.debug(f"Processed data: {res_dct}")
                return res_dct
