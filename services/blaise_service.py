import logging
from typing import Any, Dict, List

import blaise_restapi

from providers.configuration_provider import ConfigurationProvider
from utilities.custom_exceptions import BlaiseError
from utilities.logging import function_name


class BlaiseService:
    def __init__(self, configuration_provider: ConfigurationProvider) -> None:
        self._configuration_provider = configuration_provider
        self._blaise_connection_model = (
            self._configuration_provider.get_blaise_connection_model()
        )

        self.restapi_client = blaise_restapi.Client(
            f"http://{self._blaise_connection_model.blaise_api_url}"
        )

        self._server_park_name = self._blaise_connection_model.blaise_server_park

    def get_questionnaires(self) -> List[Dict[str, Any]]:
        try:
            questionnaires = self.restapi_client.get_all_questionnaires_for_server_park(
                self._server_park_name
            )
            logging.info("Got questionnaires")
            return questionnaires
        except Exception as e:
            error_message = (
                f"Exception caught in {function_name()}. "
                f"Error getting questionnaires: {e}"
            )
            logging.error(error_message)
            raise BlaiseError(error_message)
