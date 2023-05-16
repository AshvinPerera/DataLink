from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QLineEdit, QHBoxLayout, QVBoxLayout, QGridLayout, QPushButton, QLabel, QTableView, QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from DataLink.GUI.DataManager import CSVImportManager, SchemaManager, ValidationManager
from DataLink.GUI.Helper import (
    horizontal_line, Logger, error_dialog, creator_options, create_file_dialog, csv_search,
    directory_search_button,  edit_button, create_button, save_data_button,
    PandasModel, ComboBoxSelection, DTypeEnforcer
)


"""
Import specific data structure definitions
"""


class Editor(QMainWindow):
    def __init__(self, window_name: str, min_height: int, min_width: int):
        super().__init__()
        self.table = None
        self.layout = None
        self.save_button = None

        self.setWindowTitle(window_name)
        self.setup()
        self.setMinimumHeight(min_height)
        self.setMinimumWidth(min_width)

    def setup(self):
        self.setCentralWidget(QWidget())
        self.layout = QVBoxLayout()
        self.table = QTableView()
        self.layout.addWidget(self.table)
        self.centralWidget().setLayout(self.layout)


class SchemaEditor(Editor):
    def __init__(self, schema_manager: SchemaManager):
        super().__init__('Edit Schema', 500, 353)
        self.setWindowIcon(QIcon("icon.jpg"))
        self.model = None
        self.delegate = None
        self.is_loaded = True
        super().setup()
        self.schema_setup(schema_manager)

    def schema_setup(self, schema_manager: SchemaManager):
        filepath = schema_manager.filename
        schema = schema_manager.get_schema()

        if schema is None:
            self.is_loaded = False
            return

        self.save_button = save_data_button(filepath, schema)

        self.delegate = ComboBoxSelection()
        self.delegate.set_items(['integer', 'decimal', 'logical', 'categorical', 'text', 'date', 'time'])
        self.model = PandasModel(schema, ['Variable Name', 'Variable Type', 'Fill Missing Values'])
        self.table.setModel(self.model)

        self.table.setItemDelegateForColumn(1, self.delegate)
        self.table.setItemDelegateForColumn(2, DTypeEnforcer(str))

        self.layout.addWidget(self.save_button)


class ValidationEditor(Editor):
    def __init__(self, validation_editor: ValidationManager):
        super().__init__('Edit Validation Instructions', 500, 1253)
        self.setWindowIcon(QIcon("icon.jpg"))
        self.model = None
        self.delegates = None
        self.is_loaded = True
        super().setup()
        self.validation_setup(validation_editor)

    def validation_setup(self, validation_manager: ValidationManager):
        filepath = validation_manager.filename
        validation = validation_manager.get_validation()

        if validation is None:
            self.is_loaded = False
            return

        self.save_button = save_data_button(filepath, validation)
        self.model = PandasModel(validation)
        self.table.setModel(self.model)
        self.delegates = []
        self.set_delegates()
        self.layout.addWidget(self.save_button)

    def set_delegates(self):
        for i in [1, 4, 6, 7, 9, 11]:
            self.delegates.append(DTypeEnforcer(bool))
            self.table.setItemDelegateForColumn(i, self.delegates[-1])
        for i in [2, 3]:
            self.delegates.append(DTypeEnforcer(int))
            self.table.setItemDelegateForColumn(i, self.delegates[-1])
        for i in [5, 8]:
            self.delegates.append(DTypeEnforcer(str))
            self.table.setItemDelegateForColumn(i, self.delegates[-1])


class ImportUI(QWidget):
    def __init__(self):
        super().__init__()
        self.schema_editor = None
        self.validation_editor = None
        self.logger = Logger()

        self.import_button = QPushButton('Import Data')

        self.dataset_search_button = directory_search_button()

        self.schema_search_button = directory_search_button()
        self.schema_edit_button = edit_button()
        self.schema_create_button = create_button()

        self.validation_search_button = directory_search_button()
        self.validation_edit_button = edit_button()
        self.validation_create_button = create_button()

        self.dataset_filepath_input = QLineEdit()
        self.schema_filepath_input = QLineEdit()
        self.validation_filepath_input = QLineEdit()

        self.setup()

    def setup(self):
        panel_layout = QVBoxLayout()
        panel_layout.addSpacing(20)
        panel_layout.addLayout(self.create_panel())
        panel_layout.addSpacing(5)
        panel_layout.addWidget(self.import_button)
        panel_layout.addWidget(horizontal_line())
        panel_layout.addWidget(self.logger.log)
        panel_layout.addStretch()
        self.setLayout(panel_layout)

    def create_panel(self):
        import_layout = QGridLayout()
        dataset_search_label = QLabel('Dataset path:')
        schema_search_label = QLabel('Schema path:')
        schema_create_options = creator_options(self.schema_edit_button, self.schema_create_button)
        validation_search_label = QLabel('Validation path:')
        validation_create_options = creator_options(self.validation_edit_button, self.validation_create_button)

        import_layout.addWidget(horizontal_line(), 0, 1)
        import_layout.addWidget(dataset_search_label, 1, 0)
        import_layout.addWidget(self.dataset_filepath_input, 1, 1)
        import_layout.addWidget(self.dataset_search_button, 1, 2)
        import_layout.setRowStretch(2, 2)
        import_layout.addWidget(horizontal_line(), 3, 1)
        import_layout.addWidget(schema_search_label, 4, 0)
        import_layout.addWidget(self.schema_filepath_input, 4, 1)
        import_layout.addWidget(self.schema_search_button, 4, 2)
        import_layout.addWidget(schema_create_options, 5, 1)
        import_layout.setRowStretch(6, 2)
        import_layout.addWidget(horizontal_line(), 7, 1)
        import_layout.addWidget(validation_search_label, 8, 0)
        import_layout.addWidget(self.validation_filepath_input, 8, 1)
        import_layout.addWidget(self.validation_search_button, 8, 2)
        import_layout.addWidget(validation_create_options, 9, 1)

        return import_layout

    def set_panel(
            self,
            csv_import_manager: CSVImportManager,
            schema_manager: SchemaManager,
            validation_manager: ValidationManager
    ) -> None:
        try:
            self.import_button.clicked.disconnect()
            self.dataset_search_button.clicked.disconnect()
            self.schema_search_button.clicked.disconnect()
            self.schema_edit_button.clicked.disconnect()
            self.schema_create_button.clicked.disconnect()
            self.validation_search_button.clicked.disconnect()
            self.validation_edit_button.clicked.disconnect()
            self.validation_create_button.clicked.disconnect()
        except TypeError:
            pass

        self.import_button.clicked.connect(lambda: self.import_data(
            csv_import_manager,
            schema_manager,
            validation_manager
        ))
        self.dataset_search_button.clicked.connect(lambda: csv_search(self.dataset_filepath_input))
        self.validation_search_button.clicked.connect(lambda: csv_search(self.validation_filepath_input))
        self.schema_search_button.clicked.connect(lambda: csv_search(self.schema_filepath_input))

        self.schema_edit_button.clicked.connect(lambda: self.create_schema_editor(schema_manager))
        self.validation_edit_button.clicked.connect(lambda: self.create_validation_editor(validation_manager))
        self.schema_create_button.clicked.connect(lambda: self.create_schema_creator(
            schema_manager,
            csv_import_manager
        ))
        self.validation_create_button.clicked.connect(lambda: self.create_validation_creator(
            validation_manager,
            csv_import_manager
        ))
        csv_import_manager.logger = self.logger
        schema_manager.logger = self.logger
        validation_manager.logger = self.logger

        self.dataset_filepath_input.setText(csv_import_manager.filename)
        self.schema_filepath_input.setText(schema_manager.filename)
        self.validation_filepath_input.setText(validation_manager.filename)

    def save_panel(
            self,
            csv_import_manager: CSVImportManager,
            schema_manager: SchemaManager,
            validation_manager: ValidationManager
    ) -> None:
        csv_import_manager.filename = self.dataset_filepath_input.text()
        schema_manager.filename = self.schema_filepath_input.text()
        validation_manager.filename = self.validation_filepath_input.text()

    def import_data(
            self,
            csv_import_manager: CSVImportManager,
            schema_manager: SchemaManager,
            validation_manager: ValidationManager
    ) -> None:
        csv_import_manager.filename = self.dataset_filepath_input.text()
        schema_manager.filename = self.schema_filepath_input.text()
        validation_manager.filename = self.validation_filepath_input.text()
        csv_import_manager.import_data(schema_manager, validation_manager)
        self.handle_import_error(schema_manager.bad_filename,
                                 validation_manager.bad_filename,
                                 csv_import_manager.bad_filename,)

    def create_schema_editor(
            self,
            schema_manager: SchemaManager
    ) -> None:
        self.schema_editor = None
        schema_manager._schema = None

        schema_manager.filename = self.schema_filepath_input.text()
        schema_manager.read_schema()
        if schema_manager.bad_filename:
            error_message = 'missing/ incorrect schema filename\n'
            dialog = error_dialog(error_message)
            dialog.exec()
            return
        self.schema_editor = SchemaEditor(schema_manager)
        if self.schema_editor.is_loaded:
            self.schema_editor.show()

    def create_validation_editor(
            self,
            validation_manager: ValidationManager
    ) -> None:
        self.validation_editor = None
        validation_manager._validation = None

        validation_manager.filename = self.validation_filepath_input.text()
        validation_manager.read_validation()
        if validation_manager.bad_filename:
            error_message = 'missing/ incorrect validation instruction filename\n'
            dialog = error_dialog(error_message)
            dialog.exec()
            return
        self.validation_editor = ValidationEditor(validation_manager)
        if self.validation_editor.is_loaded:
            self.validation_editor.show()

    def create_schema_creator(
            self,
            schema_manager: SchemaManager,
            csv_import_manager: CSVImportManager
    ) -> None:
        self.schema_editor = None
        schema_manager._schema = None

        filepath = {}
        dialog = create_file_dialog('Create Schema', filepath)
        dialog.exec()

        if len(filepath) == 0:
            return

        filepath = filepath['path'] + filepath['name']
        schema_manager.create_schema(filepath, csv_import_manager)

        if csv_import_manager.bad_filename:
            error_message = 'missing/ incorrect dataset filename\n'
            dialog = error_dialog(error_message)
            dialog.exec()
            return

        if schema_manager.bad_filename:
            error_message = 'missing/ incorrect schema filename\n'
            dialog = error_dialog(error_message)
            dialog.exec()
            return

        self.schema_filepath_input.setText(filepath)
        self.schema_editor = SchemaEditor(schema_manager)
        if self.schema_editor.is_loaded:
            self.schema_editor.show()

    def create_validation_creator(
            self,
            validation_manager: ValidationManager,
            csv_import_manager: CSVImportManager
    ) -> None:
        self.validation_editor = None
        validation_manager._validation = None

        filepath = {}
        dialog = create_file_dialog('Create Validation Instructions', filepath)
        dialog.exec()

        if len(filepath) == 0:
            return

        filepath = filepath['path'] + filepath['name']
        validation_manager.create_validation(filepath, csv_import_manager)

        if csv_import_manager.bad_filename:
            error_message = 'missing/ incorrect dataset filename\n'
            dialog = error_dialog(error_message)
            dialog.exec()
            return

        if validation_manager.bad_filename:
            error_message = 'missing/ incorrect validation filename\n'
            dialog = error_dialog(error_message)
            dialog.exec()
            return

        self.validation_filepath_input.setText(filepath)
        self.validation_editor = ValidationEditor(validation_manager)
        if self.validation_editor.is_loaded:
            self.validation_editor.show()

    @staticmethod
    def handle_import_error(
            bad_config_filename,
            bad_validation_filename,
            bad_csv_filename
    ) -> None:
        is_error = False
        error_message = ''

        if bad_config_filename:
            error_message = error_message + 'missing/ incorrect schema filename\n'
            is_error = True
        if bad_validation_filename:
            error_message = error_message + 'missing/ incorrect validation filename\n'
            is_error = True
        if bad_csv_filename:
            error_message = error_message + 'missing/ incorrect csv dataset filename\n'
            is_error = True

        if is_error:
            dialog = error_dialog(error_message)
            dialog.exec()
