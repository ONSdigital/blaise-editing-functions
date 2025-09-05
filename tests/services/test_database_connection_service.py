from unittest.mock import Mock, call, patch

import pytest
import sqlalchemy
from sqlalchemy import URL

from models.database_connection_model import DatabaseConnectionModel
from services.database_connection_service import DatabaseConnectionService


class TestDatabaseConnectionFunctionality:

    @pytest.fixture()
    def connection_model(self) -> DatabaseConnectionModel:
        return DatabaseConnectionModel(
            database_name="blaise",
            database_username="test_user",
            database_password="test_password",
            database_ip_address="0.0.0.0",
            database_port=3306,
        )

    @pytest.fixture()
    def mock_configuration_provider(self):
        return Mock()

    @pytest.fixture()
    def service_under_test(
        self, mock_configuration_provider, connection_model
    ) -> DatabaseConnectionService:
        mock_configuration_provider.get_database_connection_model.return_value = (
            connection_model
        )
        return DatabaseConnectionService(mock_configuration_provider)

    @patch.object(sqlalchemy, "create_engine")
    def test_get_database_uses_the_connection_model_database_url_and_connector_to_create_an_engine(
        self, mock_engine, service_under_test, connection_model
    ):
        # arrange
        expected_url = URL.create(
            drivername="mysql+pymysql",
            username=connection_model.database_username,
            password=connection_model.database_password,
            host=connection_model.database_ip_address,
            port=connection_model.database_port,
            database=connection_model.database_name,
        )

        # act
        service_under_test.get_database()

        # assert
        mock_engine.assert_has_calls(
            [call(url=expected_url, connect_args={"ssl": {"key": "blaise"}})]
        )
