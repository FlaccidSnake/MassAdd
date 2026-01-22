# -*- coding: utf-8 -*-
"""
Recent Tags Dialog for MassAdd with Modify functionality
"""
from aqt import mw
from aqt.qt import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QDialogButtonBox,
    QLabel,
)
from aqt.tagedit import TagEdit
from aqt.utils import tooltip
from PyQt6.QtCore import Qt


class TagButton(QHBoxLayout):
    """A tag button with a modify button that can turn into an editable field."""
    
    def __init__(self, tag_text, parent_dialog):
        super().__init__()
        self.parent_dialog = parent_dialog
        self.original_tag = tag_text
        self.is_editing = False
        self.is_selected = False
        
        # Modify button (toggles edit mode)
        self.modify_btn = QPushButton("Modify")
        self.modify_btn.setFixedWidth(90)
        self.modify_btn.clicked.connect(self.toggle_edit_mode)
        self.addWidget(self.modify_btn)
        
        # Tag button (can be replaced with tag edit)
        self.tag_btn = QPushButton(tag_text)
        self.tag_btn.setCheckable(True)
        self.tag_btn.clicked.connect(self.on_tag_clicked)
        self.tag_btn.setStyleSheet("")
        self.addWidget(self.tag_btn, 1)
        
        # Tag edit with autocomplete (hidden by default)
        self.tag_edit = TagEdit(parent_dialog)
        self.tag_edit.setCol(mw.col)
        self.tag_edit.setText(tag_text)
        self.tag_edit.hide()
        self.tag_edit.returnPressed.connect(self.finish_editing)
        self.addWidget(self.tag_edit, 1)
    
    def toggle_edit_mode(self):
        """Toggle between edit and display mode."""
        if self.is_editing:
            self.finish_editing()
        else:
            self.start_editing()
    
    def start_editing(self):
        """Switch to edit mode."""
        self.is_editing = True
        self.tag_btn.hide()
        self.tag_edit.setText(self.tag_btn.text())
        self.tag_edit.show()
        self.tag_edit.setFocus()
        self.tag_edit.selectAll()
        self.modify_btn.setText("OK")
    
    def finish_editing(self):
        """Finish editing and update the tag."""
        self.is_editing = False
        
        # Hide the completer before getting text
        if hasattr(self.tag_edit, 'hideCompleter'):
            self.tag_edit.hideCompleter()
        
        new_text = self.tag_edit.text().strip()
        if new_text:
            self.tag_btn.setText(new_text)
        self.tag_edit.hide()
        self.tag_btn.show()
        self.modify_btn.setText("Modify")
        
        # Auto-select after modifying
        if new_text:
            self.is_selected = True
            self.tag_btn.setChecked(True)
            self.update_button_style()
    
    def on_tag_clicked(self):
        """Handle tag button click to toggle selection."""
        self.is_selected = self.tag_btn.isChecked()
        self.update_button_style()
    
    def update_button_style(self):
        """Update button background based on selection state."""
        if self.is_selected:
            self.tag_btn.setStyleSheet("background-color: #90EE90;")  # Light green
        else:
            self.tag_btn.setStyleSheet("")
    
    def get_tag_text(self):
        """Get the current tag text."""
        return self.tag_btn.text()
    
    def is_tag_selected(self):
        """Check if this tag is selected."""
        return self.is_selected


class RecentTagsDialog(QDialog):
    """Dialog for selecting and modifying recent tags."""
    
    def __init__(self, parent, recent_tags):
        super().__init__(parent, Qt.WindowType.Window)
        self.setWindowTitle("Add Recent Tags")
        self.setMinimumWidth(450)
        self.setMinimumHeight(400)
        
        self.tag_buttons = []
        self.selected_tags = []  # Store selected tags
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Header label
        header = QLabel("Select tags to add (click to toggle, modify to edit):")
        main_layout.addWidget(header)
        
        # Add tag buttons
        for tag in recent_tags:
            tag_button = TagButton(tag, self)
            self.tag_buttons.append(tag_button)
            main_layout.addLayout(tag_button)
        
        # Add stretch to push buttons to top
        main_layout.addStretch()
        
        # Button box
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.on_accept)
        self.button_box.rejected.connect(self.on_reject)
        main_layout.addWidget(self.button_box)
        
        # Install event filter to handle clicks outside line edits
        self.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """Handle clicks outside of line edits to close them."""
        if event.type() == event.Type.MouseButtonPress:
            for tag_btn in self.tag_buttons:
                if tag_btn.is_editing:
                    # Get global position (Qt6 compatibility)
                    try:
                        global_pos = event.globalPosition().toPoint()
                    except AttributeError:
                        # Qt5 fallback
                        global_pos = event.globalPos()
                    
                    # Check if click is outside the line edit
                    if not tag_btn.tag_edit.geometry().contains(
                        tag_btn.tag_edit.mapFromGlobal(global_pos)
                    ):
                        tag_btn.finish_editing()
        return super().eventFilter(obj, event)
    
    def on_accept(self):
        """Handle dialog acceptance - hide all completers first."""
        for tag_btn in self.tag_buttons:
            if hasattr(tag_btn.tag_edit, 'hideCompleter'):
                tag_btn.tag_edit.hideCompleter()
        
        # Collect selected tags
        self.selected_tags = [
            tag_btn.get_tag_text() 
            for tag_btn in self.tag_buttons 
            if tag_btn.is_tag_selected()
        ]
        
        super().accept()
    
    def on_reject(self):
        """Handle dialog rejection - hide all completers first."""
        for tag_btn in self.tag_buttons:
            if hasattr(tag_btn.tag_edit, 'hideCompleter'):
                tag_btn.tag_edit.hideCompleter()
        self.selected_tags = []
        super().reject()
    
    def get_selected_tags(self):
        """Return list of selected tag texts."""
        return self.selected_tags


def get_recent_tags(limit=None):
    """Get tags from the most recently added notes."""
    config = mw.addonManager.getConfig(__name__)
    if config is None:
        config = {}
    
    if limit is None:
        limit = config.get("recent_tags_limit", 10)
    
    # Get search depth from config
    search_limit = config.get("recent_tags_search_depth", 100)
    
    # Get all note IDs sorted by ID (which corresponds to creation time)
    note_ids = mw.col.db.list(
        "SELECT id FROM notes ORDER BY id DESC LIMIT ?", 
        search_limit
    )
    
    recent_tags = []
    seen_tags = set()
    
    for nid in note_ids:
        note = mw.col.get_note(nid)
        for tag in note.tags:
            if tag not in seen_tags:
                recent_tags.append(tag)
                seen_tags.add(tag)
                if len(recent_tags) >= limit:
                    return recent_tags
    
    return recent_tags