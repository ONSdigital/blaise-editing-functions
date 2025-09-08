from providers.configuration_provider import ConfigurationProvider
from services.blaise_service import BlaiseService
from services.case_service import CaseService
from services.database_connection_service import DatabaseConnectionService
from services.database_service import DatabaseService
from services.validation_service import ValidationService


class ServiceInstanceFactory:

    @staticmethod
    def create_validation_service() -> ValidationService:
        return ValidationService()

    @staticmethod
    def create_case_service() -> CaseService:
        configuration_provider = ConfigurationProvider()
        database_connection_service = DatabaseConnectionService(configuration_provider)
        database_service = DatabaseService(database_connection_service)
        blaise_service = BlaiseService(configuration_provider)
        return CaseService(database_service, blaise_service)
