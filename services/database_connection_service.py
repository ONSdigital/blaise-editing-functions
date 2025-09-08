import sqlalchemy
from sqlalchemy import URL, Engine

from providers.configuration_provider import ConfigurationProvider


class DatabaseConnectionService:
    def __init__(self, configuration_provider: ConfigurationProvider):
        self._configuration_provider = configuration_provider
        self._connection_model = (
            self._configuration_provider.get_database_connection_model()
        )

    def get_database(self) -> Engine:
        sql_url = URL.create(
            drivername="mysql+pymysql",
            username=self._connection_model.database_username,
            password=self._connection_model.database_password,
            host=self._connection_model.database_ip_address,
            port=self._connection_model.database_port,
            database=self._connection_model.database_name,
        )
        return sqlalchemy.create_engine(
            url=sql_url, connect_args={"ssl": {"key": "blaise"}}
        )
