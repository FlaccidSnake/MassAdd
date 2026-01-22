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
                "close_after_adding": False,
                "recent_tags_limit": 10,
                "recent_tags_search_depth": 100
            }
        
        self.show_in_main_window = config.get("show_in_main_window", True)
        self.show_in_browser = config.get("show_in_browser", True)
        self.show_added_notes = config.get("show_added_notes", False)
        self.close_after_adding = config.get("close_after_adding", False)
        self.recent_tags_limit = config.get("recent_tags_limit", 10)
        self.recent_tags_search_depth = config.get("recent_tags_search_depth", 100)
        
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
        
        # Separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator2)
        
        # Recent Tags Settings
        from aqt.qt import QSpinBox
        tags_group = QGroupBox("Recent Tags")
        tags_layout = QVBoxLayout()
        
        # Number of recent tags
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
        
        # Search depth
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
        config = mw.addonManager.getConfig(__name__)
        
        # Create new config if it doesn't exist
        if config is None:
            config = {}
        
        config["show_in_main_window"] = self.main_window_checkbox.isChecked()
        config["show_in_browser"] = self.browser_checkbox.isChecked()
        config["show_added_notes"] = self.show_notes_checkbox.isChecked()
        config["close_after_adding"] = self.close_window_checkbox.isChecked()
        config["recent_tags_limit"] = self.tags_limit_spinbox.value()
        config["recent_tags_search_depth"] = self.search_depth_spinbox.value()
        
        mw.addonManager.writeConfig(__name__, config)
        
        tooltip("Configuration saved! Restart Anki to see menu location changes.")
        self.accept()


def show_config_dialog():
    """Show the configuration dialog"""
    dialog = MassAddConfigDialog(mw)
    dialog.exec()