import logging

from utilities.custom_exceptions import RequestError


class ValidationService:
    def __init__(self) -> None:
        self.request_json = None

    @staticmethod
    def validate_request_values_are_not_empty(request):
        missing_values = []
        survey_type = request.json["survey_type"]
        if survey_type is None or survey_type == "":
            missing_values.append("survey_type")

        if missing_values:
            error_message = f"Missing required values from request: {missing_values}"
            logging.error(error_message)
            raise RequestError(error_message)
