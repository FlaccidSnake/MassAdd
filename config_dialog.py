# -*- coding: utf-8 -*-
"""
MassAdd Config Dialog
"""
from aqt import mw
from aqt.utils import tooltip, showInfo

# Qt5/Qt6 compatibility
try:
    from PyQt6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
        QCheckBox, QPushButton, QFrame, QGroupBox, QSpinBox
    )
    from PyQt6.QtCore import Qt
    qtmajor = 6
except ImportError:
    from PyQt5.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
        QCheckBox, QPushButton, QFrame, QGroupBox, QSpinBox
    )
    from PyQt5.QtCore import Qt
    qtmajor = 5


DEFAULT_NOTE_DELIMITER = "\n"
DEFAULT_FIELD_DELIMITER = "\t"


def parse_delimiter(value, default):
    """Turn a config value into a real delimiter.

    Empty means "use the default". You can type \\t for a tab and \\n for a
    line break.
    """
    if not isinstance(value, str) or not value:
        return default
    value = value.replace("\\t", "\t").replace("\\n", "\n")
    return value or default


def make_separator():
    sep = QFrame()
    if qtmajor == 6:
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
    else:
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)
    return sep


class MassAddConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        config = mw.addonManager.getConfig(__name__)

        # Handle missing config gracefully
        if config is None:
            config = {}

        self.show_in_main_window = config.get("show_in_main_window", True)
        self.show_in_browser = config.get("show_in_browser", True)
        self.show_added_notes = config.get("show_added_notes", False)
        self.close_after_adding = config.get("close_after_adding", False)
        self.recent_tags_limit = config.get("recent_tags_limit", 10)
        self.recent_tags_search_depth = config.get("recent_tags_search_depth", 100)
        self.note_delimiter = config.get("note_delimiter", "")
        self.field_delimiter = config.get("field_delimiter", "")

        self.setWindowTitle("MassAdd Configuration")
        self.setMinimumWidth(450)

        layout = QVBoxLayout()

        # Delimiter Settings
        delim_group = QGroupBox("Delimiters")
        delim_layout = QVBoxLayout()

        note_row = QHBoxLayout()
        note_label = QLabel("Separate notes with:")
        note_label.setMinimumWidth(140)
        self.note_delim_edit = QLineEdit()
        self.note_delim_edit.setPlaceholderText("Leave empty for line break")
        self.note_delim_edit.setText(self.note_delimiter)
        note_row.addWidget(note_label)
        note_row.addWidget(self.note_delim_edit)
        delim_layout.addLayout(note_row)

        field_row = QHBoxLayout()
        field_label = QLabel("Separate fields with:")
        field_label.setMinimumWidth(140)
        self.field_delim_edit = QLineEdit()
        self.field_delim_edit.setPlaceholderText("Leave empty for tab")
        self.field_delim_edit.setText(self.field_delimiter)
        field_row.addWidget(field_label)
        field_row.addWidget(self.field_delim_edit)
        delim_layout.addLayout(field_row)

        delim_hint = QLabel(
            "<i>Can be more than one character. "
            "You can also type \\t for a tab or \\n for a line break.</i>"
        )
        delim_hint.setWordWrap(True)
        delim_layout.addWidget(delim_hint)

        delim_group.setLayout(delim_layout)
        layout.addWidget(delim_group)

        layout.addWidget(make_separator())

        # Menu Location Settings
        menu_group = QGroupBox("Menu Location")
        menu_layout = QVBoxLayout()

        self.main_window_checkbox = QCheckBox("Show in main window menubar")
        self.main_window_checkbox.setChecked(self.show_in_main_window)
        menu_layout.addWidget(self.main_window_checkbox)

        self.browser_checkbox = QCheckBox("Show in browser menubar")
        self.browser_checkbox.setChecked(self.show_in_browser)
        menu_layout.addWidget(self.browser_checkbox)

        menu_group.setLayout(menu_layout)
        layout.addWidget(menu_group)

        layout.addWidget(make_separator())

        # Behavior Settings
        behavior_group = QGroupBox("Behavior")
        behavior_layout = QVBoxLayout()

        self.show_notes_checkbox = QCheckBox("Show added notes in browser after adding")
        self.show_notes_checkbox.setChecked(self.show_added_notes)
        behavior_layout.addWidget(self.show_notes_checkbox)

        self.close_window_checkbox = QCheckBox("Close MassAdd window after adding notes")
        self.close_window_checkbox.setChecked(self.close_after_adding)
        behavior_layout.addWidget(self.close_window_checkbox)

        behavior_group.setLayout(behavior_layout)
        layout.addWidget(behavior_group)

        layout.addWidget(make_separator())

        # Recent Tags Settings
        tags_group = QGroupBox("Recent Tags")
        tags_layout = QVBoxLayout()

        tags_limit_layout = QHBoxLayout()
        tags_limit_label = QLabel("Number of recent tags to show:")
        self.tags_limit_spinbox = QSpinBox()
        self.tags_limit_spinbox.setMinimum(5)
        self.tags_limit_spinbox.setMaximum(50)
        self.tags_limit_spinbox.setValue(self.recent_tags_limit)
        tags_limit_layout.addWidget(tags_limit_label)
        tags_limit_layout.addWidget(self.tags_limit_spinbox)
        tags_limit_layout.addStretch()
        tags_layout.addLayout(tags_limit_layout)

        search_depth_layout = QHBoxLayout()
        search_depth_label = QLabel("Search depth (notes to scan):")
        self.search_depth_spinbox = QSpinBox()
        self.search_depth_spinbox.setMinimum(50)
        self.search_depth_spinbox.setMaximum(1000)
        self.search_depth_spinbox.setValue(self.recent_tags_search_depth)
        search_depth_layout.addWidget(search_depth_label)
        search_depth_layout.addWidget(self.search_depth_spinbox)
        search_depth_layout.addStretch()
        tags_layout.addLayout(search_depth_layout)

        tags_group.setLayout(tags_layout)
        layout.addWidget(tags_group)

        # Info label
        info_label = QLabel(
            "<i>Note: Menu location changes require restarting Anki</i>"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_config)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def save_config(self):
        """Save configuration"""
        note_raw = self.note_delim_edit.text()
        field_raw = self.field_delim_edit.text()

        # The two delimiters must differ, otherwise notes can't be parsed
        if (parse_delimiter(note_raw, DEFAULT_NOTE_DELIMITER)
                == parse_delimiter(field_raw, DEFAULT_FIELD_DELIMITER)):
            showInfo("The note delimiter and the field delimiter must be different.")
            return

        config = mw.addonManager.getConfig(__name__)

        # Create new config if it doesn't exist
        if config is None:
            config = {}

        config["note_delimiter"] = note_raw
        config["field_delimiter"] = field_raw
        config["show_in_main_window"] = self.main_window_checkbox.isChecked()
        config["show_in_browser"] = self.browser_checkbox.isChecked()
        config["show_added_notes"] = self.show_notes_checkbox.isChecked()
        config["close_after_adding"] = self.close_window_checkbox.isChecked()
        config["recent_tags_limit"] = self.tags_limit_spinbox.value()
        config["recent_tags_search_depth"] = self.search_depth_spinbox.value()

        mw.addonManager.writeConfig(__name__, config)

        tooltip("Configuration saved! Restart Anki to see menu location changes.")
        self.accept()


def show_config_dialog(parent=None):
    """Show the configuration dialog"""
    dialog = MassAddConfigDialog(parent or mw)
    dialog.exec()