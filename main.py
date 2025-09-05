import logging

from factories.service_instance_factory import ServiceInstanceFactory
from utilities.custom_exceptions import BlaiseError, ConfigError, RequestError
from utilities.logging import setup_logger

setup_logger()


def copy_cases_to_edit(request) -> tuple[str, int]:
    try:
        logging.info("Running Cloud Function - 'copy_cases_to_edit'")

        validation_service = ServiceInstanceFactory.create_validation_service()
        validation_service.validate_request_values_are_not_empty(request)

        case_service = ServiceInstanceFactory.create_case_service()
        questionnaire_name = request.get_json()["survey_type"]
        case_service.copy_cases(questionnaire_name)

        logging.info("Finished Running Cloud Function - 'copy_cases_to_edit'")
        return "Successfully copied cases to edit", 200
    except (ConfigError, RequestError, BlaiseError) as e:
        error_message = f"Error copying cases to edit: {e}"
        logging.error(error_message)
        return error_message, 400
    except Exception as e:
        error_message = f"Error copying cases to edit: {e}"
        logging.error(error_message)
        return error_message, 500
