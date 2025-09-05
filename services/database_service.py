from sqlalchemy import Connection, Engine, text

from services.database_connection_service import DatabaseConnectionService


class DatabaseService:
    def __init__(self, database_connection_service: DatabaseConnectionService) -> None:
        self._database_engine: Engine = database_connection_service.get_database()

    @property
    def database(self) -> Engine:
        return self._database_engine

    def table_exists(self, connection: Connection, table_name: str):
        return self._database_engine.dialect.has_table(connection, table_name)

    def copy_cases(
        self,
        connection: Connection,
        edit_table_name: str,
        questionnaire_table_name: str,
    ):
        connection.execute(
            self.copy_cases_command(edit_table_name, questionnaire_table_name)
        )

    @staticmethod
    def copy_cases_command(edit_table_name: str, questionnaire_table_name: str):
        return text(
            f"INSERT INTO {edit_table_name} \
                    SELECT UNEDITED.* \
                    FROM {questionnaire_table_name} UNEDITED \
                    LEFT JOIN {edit_table_name}  EDITED \
                    ON UNEDITED.Serial_Number = EDITED.Serial_Number \
                    WHERE IFNULL(EDITED.QEdit_edited, 0) <> 1 \
                    ON DUPLICATE KEY UPDATE \
                    Serial_Number = VALUES(Serial_Number), \
                    QEdit_edited = VALUES( QEdit_edited), \
                    QEdit_LastUpdated = VALUES(QEdit_LastUpdated), \
                    QHAdmin_HOut = VALUES(QHAdmin_HOut), \
                    DataStream = VALUES(DataStream);"
        )
