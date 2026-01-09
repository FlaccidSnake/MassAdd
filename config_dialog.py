# -*- coding: utf-8 -*-
"""
MassAdd Config Dialog
"""
from aqt.qt import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QPushButton, QFrame, QGroupBox
from aqt import mw
from aqt.utils import tooltip


class MassAddConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        config = mw.addonManager.getConfig(__name__)
        
        # Handle missing config gracefully
        if config is None:
            config = {
                "show_in_main_window": True,
                "show_in_browser": True,
                "show_added_notes": False,
                "close_after_adding": False
            }
        
        self.show_in_main_window = config.get("show_in_main_window", True)
        self.show_in_browser = config.get("show_in_browser", True)
        self.show_added_notes = config.get("show_added_notes", False)
        self.close_after_adding = config.get("close_after_adding", False)
        
        self.setWindowTitle("MassAdd Configuration")
        self.setMinimumWidth(450)
        
        layout = QVBoxLayout()
        
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
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
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
        config = mw.addonManager.getConfig(__name__)
        
        # Create new config if it doesn't exist
        if config is None:
            config = {}
        
        config["show_in_main_window"] = self.main_window_checkbox.isChecked()
        config["show_in_browser"] = self.browser_checkbox.isChecked()
        config["show_added_notes"] = self.show_notes_checkbox.isChecked()
        config["close_after_adding"] = self.close_window_checkbox.isChecked()
        
        mw.addonManager.writeConfig(__name__, config)
        
        tooltip("Configuration saved! Restart Anki to see menu location changes.")
        self.accept()


def show_config_dialog():
    """Show the configuration dialog"""
    dialog = MassAddConfigDialog(mw)
    dialog.exec()