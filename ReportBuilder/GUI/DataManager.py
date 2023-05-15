import sys
from typing import Any
import ReportBuilder.DataTool.Preprocessing as pr


class DataManager:
    def __init__(self):
        self.logger = None
        self.bad_filename = False

    def set_logger(self, logger: Any):
        self.logger = logger

    def log_message(self, type_name: str, args: Any):
        message = 'An exception of type {0} occurred. Arguments:\n{1!r}'.format(type_name, args)
        self.logger.log.clear()
        old_stdout = sys.stdout
        sys.stdout = self.logger
        print(message)
        sys.stdout = old_stdout


class SchemaManager(DataManager):
    def __init__(self):
        super().__init__()
        self._schema = None
        self.filename = ""

    def read_schema(self):
        self.bad_filename = False
        try:
            self._schema = pr.read_config(self.filename)
        except OSError:
            self._schema = None
            self.bad_filename = True
            return
        except Exception as ex:
            self._schema = None
            self.log_message(type(ex).__name__, ex.args)
            return

    def create_schema(self, filepath: str, csv_import_manager):
        csv_import_manager.read_csv()
        if csv_import_manager.bad_filename:
            return

        schema = pr.create_schema(list(csv_import_manager.get_columns()))

        try:
            schema.to_csv(filepath, index=False)
        except OSError:
            self.bad_filename = True
            return
        except Exception as ex:
            self.log_message(type(ex).__name__, ex.args)
            return
        self._schema = schema

    def get_schema(self):
        return self._schema


class ValidationManager(DataManager):
    def __init__(self):
        super().__init__()
        self._validation = None
        self.filename = ""

    def read_validation(self):
        self.bad_filename = False
        try:
            self._validation = pr.read_validation(self.filename)
        except OSError:
            self._validation = None
            self.bad_filename = True
            return
        except Exception as ex:
            self._validation = None
            self.log_message(type(ex).__name__, ex.args)
            return

    def create_validation(self, filepath: str, csv_import_manager):
        csv_import_manager.read_csv()
        if csv_import_manager.bad_filename:
            return

        validation = pr.create_validation(list(csv_import_manager.get_columns()))

        try:
            validation.to_csv(filepath, index=False)
        except OSError:
            self.bad_filename = True
            return
        except Exception as ex:
            self.log_message(type(ex).__name__, ex.args)
            return
        self._validation = validation

    def get_validation(self):
        return self._validation


class CSVImportManager(DataManager):
    def __init__(self):
        super().__init__()
        self._dataset = None
        self.filename = ""

    def read_csv(self):
        self.bad_filename = False
        try:
            self._dataset = pr.read_csv(self.filename)
        except OSError:
            self.bad_filename = True
            return
        except Exception as ex:
            self.log_message(type(ex).__name__, ex.args)
            return

    def import_data(self, schema_manager: SchemaManager = None, validation_manager: ValidationManager = None):
        self.bad_filename = False

        schema_manager.read_schema()
        validation_manager.read_validation()
        if schema_manager.bad_filename or validation_manager.bad_filename:
            return

        try:
            self.logger.log.clear()
            if validation_manager.get_validation() is not None:
                self._dataset = pr.read_data(self.filename,
                                             schema_manager.get_schema(),
                                             pr.convert_validation(validation_manager.get_validation()),
                                             self.logger)
            else:
                self._dataset = pr.read_data(self.filename,
                                             schema_manager.get_schema(),
                                             None,
                                             self.logger)
        except OSError:
            self.bad_filename = True
            return
        except Exception as ex:
            self.log_message(type(ex).__name__, ex.args)
            return

    def get_columns(self):
        return self._dataset.columns
