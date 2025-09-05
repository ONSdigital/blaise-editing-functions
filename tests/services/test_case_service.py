from contextlib import contextmanager
from unittest.mock import ANY, MagicMock, Mock, call, patch

import pytest

from providers.configuration_provider import ConfigurationProvider
from services.blaise_service import BlaiseService
from services.case_service import CaseService
from services.database_connection_service import DatabaseConnectionService
from services.database_service import DatabaseService


@contextmanager
def does_not_raise(expected_exception):
    try:
        yield

    except expected_exception as error:
        raise AssertionError(f"Raised exception {error} when it should not!")

    except Exception as error:
        raise AssertionError(f"An unexpected exception {error} raised.")


class TestCaseService:

    @pytest.fixture()
    def mock_database_connection_service_provider(self) -> DatabaseConnectionService:
        return Mock()

    @pytest.fixture()
    def mock_database_service(
        self, mock_database_connection_service_provider
    ) -> DatabaseService:
        return DatabaseService(mock_database_connection_service_provider)

    @pytest.fixture()
    def mock_configuration_provider(self) -> ConfigurationProvider:
        return Mock()

    @pytest.fixture()
    def mock_blaise_service(self, mock_configuration_provider) -> BlaiseService:
        return BlaiseService(mock_configuration_provider)

    @pytest.fixture()
    def service_under_test(
        self, mock_database_service, mock_blaise_service
    ) -> CaseService:
        return CaseService(mock_database_service, mock_blaise_service)

    @pytest.mark.parametrize(
        "questionnaire_name",
        ["FRS2504A", "FRS2505A", "LCF2504A", "LCF2505A"],
    )
    def test_filter_questionnaires_by_survey_type_returns_expected_list_when_given_questionnaire_name(
        self,
        questionnaire_name,
        service_under_test,
    ):
        # arrange
        mock_cases = [
            {"name": "FRS2504A", "id": "1232"},
            {"name": "FRS2504A_EDIT", "id": "1233"},
            {"name": "FRS2505A", "id": "2344"},
            {"name": "FRS2505A_EDIT", "id": "2345"},
            {"name": "LCF2504A", "id": "3456"},
            {"name": "LCF2504A_EDIT", "id": "3457"},
            {"name": "LCF2505A", "id": "4568"},
            {"name": "LCF2505A_EDIT", "id": "4569"},
        ]
        # act
        result = service_under_test.filter_questionnaires_by_survey_type(
            mock_cases, questionnaire_name
        )

        # assert
        assert len(result) == 1
        assert result[0]["name"] == questionnaire_name

    def test_filter_questionnaires_by_survey_type_returns_expected_list_when_given_survey_name(
        self,
        service_under_test,
    ):
        # arrange
        mock_cases = [
            {"name": "FRS2504A", "id": "1232"},
            {"name": "FRS2504A_EDIT", "id": "1233"},
            {"name": "FRS2505A", "id": "2344"},
            {"name": "FRS2505A_EDIT", "id": "2345"},
            {"name": "LCF2504A", "id": "3456"},
            {"name": "LCF2504A_EDIT", "id": "3457"},
            {"name": "LCF2505A", "id": "4568"},
            {"name": "LCF2505A_EDIT", "id": "4569"},
        ]
        # act
        result = service_under_test.filter_questionnaires_by_survey_type(
            mock_cases, "FRS"
        )

        # assert
        assert len(result) == 2
        assert result[0]["name"] == "FRS2504A"
        assert result[1]["name"] == "FRS2505A"

    @patch.object(BlaiseService, "get_questionnaires")
    @patch.object(CaseService, "copy_cases_for_questionnaire")
    def test_copy_cases_has_calls_for_all_expected_questionnaires(
        self,
        _mock_copy_cases_for_questionnaire,
        _mock_get_questionnaires,
        service_under_test,
    ):
        # arrange
        mock_cases = [
            {"name": "FRS2504A", "id": "1232"},
            {"name": "FRS2504A_EDIT", "id": "1233"},
            {"name": "FRS2505A", "id": "2344"},
            {"name": "FRS2505A_EDIT", "id": "2345"},
            {"name": "LCF2504A", "id": "3456"},
            {"name": "LCF2504A_EDIT", "id": "3457"},
            {"name": "LCF2505A", "id": "4568"},
            {"name": "LCF2505A_EDIT", "id": "4569"},
        ]

        _mock_get_questionnaires.return_value = mock_cases

        # act
        service_under_test.copy_cases("FRS")

        # assert
        assert _mock_copy_cases_for_questionnaire.call_count == 2
        _mock_copy_cases_for_questionnaire.assert_has_calls(
            [call("FRS2504A"), call("FRS2505A")]
        )

    @patch.object(DatabaseService, "table_exists")
    @patch.object(DatabaseService, "database")
    @patch.object(DatabaseService, "copy_cases")
    def test_copy_cases_for_questionnaire_has_call_for_copy_cases(
        self,
        _mock_copy_cases,
        _mock_database,
        _mock_table_exists,
        service_under_test,
    ):
        # arrange
        _mock_database.begin().return_value = MagicMock()
        _mock_table_exists.return_value = True

        # act
        service_under_test.copy_cases_for_questionnaire("FRS2504A")

        # assert
        assert _mock_copy_cases.call_count == 1
        _mock_copy_cases.assert_has_calls(
            [call(ANY, "FRS2504A_EDIT_Form", "FRS2504A_Form")]
        )

    @patch.object(DatabaseService, "table_exists")
    @patch.object(DatabaseService, "database")
    @patch.object(DatabaseService, "copy_cases")
    def test_copy_cases_for_questionnaire_logs_an_error_when_edit_table_does_not_exist(
        self,
        _mock_copy_cases,
        _mock_database,
        _mock_table_exists,
        service_under_test,
        caplog,
    ):
        # arrange
        _mock_database.begin().return_value = MagicMock()
        _mock_table_exists.return_value = False

        # act
        service_under_test.copy_cases_for_questionnaire("FRS2504A")

        # assert
        error_message = "Edit questionnaire missing for: 'FRS2504A'"
        assert (
            "root",
            40,
            error_message,
        ) in caplog.record_tuples

    @patch.object(DatabaseService, "table_exists")
    @patch.object(DatabaseService, "database")
    @patch.object(DatabaseService, "copy_cases")
    def test_copy_cases_for_questionnaire_does_not_call_copy_cases_when_edit_table_does_not_exist(
        self,
        _mock_copy_cases,
        _mock_database,
        _mock_table_exists,
        service_under_test,
        caplog,
    ):
        # arrange
        _mock_database.begin().return_value = MagicMock()
        _mock_table_exists.return_value = False

        # act
        service_under_test.copy_cases_for_questionnaire("FRS2504A")

        # assert
        assert _mock_copy_cases.call_count == 0
