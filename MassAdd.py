# -*- coding: utf-8 -*-
#
# MassAdd - Quickly add multiple notes at once
# Updated for Anki 25.02.5
#

from aqt import mw, deckchooser, notetypechooser
from anki.models import NotetypeId
from anki.notes import Note, NoteId
from aqt.utils import showInfo
from aqt.qt import QDialog, QVBoxLayout, QHBoxLayout, QWidget, QTextEdit, QPushButton, QLabel, QLineEdit, QAction
from aqt.browser import Browser
from aqt.gui_hooks import browser_will_show
from aqt.tagedit import TagEdit
from PyQt6.QtCore import Qt
from typing import List


def gc(key, default=None):
    """Get config value"""
    conf = mw.addonManager.getConfig(__name__)
    if conf is None:
        return default
    return conf.get(key, default)


class MockEditor:
    """Mock editor to satisfy Quick Access addon requirements"""
    def __init__(self, parent):
        self.parent = parent
        self.parentWindow = parent  # For tag addons
        self.mw = mw
        self._note = None
        self.addMode = True
        self.web = MockWeb(parent)
        self.currentField = 0  # For tag addons
    
    @property
    def note(self):
        """Create a temporary note for tag editing"""
        if self._note is None and hasattr(self.parent, 'model_chooser'):
            model_id = self.parent.model_chooser.selected_notetype_id
            if model_id:
                m = mw.col.models.get(model_id)
                if m:
                    self._note = Note(mw.col, m)
                    # Set tags from the tag field if available
                    if hasattr(self.parent, 'tags_edit'):
                        tag_string = self.parent.tags_edit.text().strip()
                        if tag_string:
                            self._note.tags = mw.col.tags.split(tag_string)
        return self._note
    
    @note.setter
    def note(self, value):
        """Allow setting the note"""
        self._note = value
    
    def call_after_note_saved(self, callback):
        """Execute callback immediately since we don't have a real note to save"""
        callback()
    
    def loadNote(self, focusTo=None):
        """Update tag field from the note"""
        if self._note and hasattr(self.parent, 'tags_edit'):
            tag_string = mw.col.tags.join(self._note.tags)
            self.parent.tags_edit.setText(tag_string)
    
    def _save_current_note(self):
        """Mock method - does nothing in MassAdd"""
        pass
    
    def saveNow(self, callback):
        """Mock saveNow for tag addons - execute callback immediately"""
        callback()


class MockWeb:
    """Mock web object for editor"""
    def __init__(self, parent):
        self.parent = parent
    
    def setFocus(self):
        """Set focus to the text edit area"""
        if hasattr(self.parent, 'text_edit') and self.parent.text_edit:
            self.parent.text_edit.setFocus()
    
    def eval(self, js_code):
        """Mock eval method - does nothing"""
        pass


class MassAddWindow(QDialog):
    def __init__(self) -> None:
        super().__init__(None)
        self.setWindowFlags(Qt.WindowType.Window)

        self.deck_widget = None
        self.model_widget = None
        self.text_edit = None
        self.processor_widget = None
        self.processor_layout = None
        self.processor_label = None
        self.processor_text = None
        self.processor_button = None
        self.submit_button = None
        self.deck_chooser = None
        self.model_chooser = None
        self.notetype_chooser = None  # Alias for compatibility
        self.editor = None  # Will be initialized in setup_ui
        self.mw = mw  # Reference to main window
        self.tags_edit = None  # Tag field

    def setup_ui(self):
        layout = QVBoxLayout()
        self.deck_widget = QWidget(self)
        self.model_widget = QWidget(self)
        self.text_edit = QTextEdit(self)
        self.submit_button = QPushButton(self)

        # Create mock editor for Quick Access addon compatibility
        self.editor = MockEditor(self)

        self.deck_chooser = deckchooser.DeckChooser(mw, self.deck_widget)
        # Add reference back to this window for Quick Access compatibility
        self.deck_chooser.addcards = self

        defaults = mw.col.defaults_for_adding(current_review_card=mw.reviewer.card)
        self.model_chooser = notetypechooser.NotetypeChooser(
            mw=mw,
            widget=self.model_widget,
            starting_notetype_id=NotetypeId(defaults.notetype_id),
        )
        # Add reference back to this window for Quick Access compatibility
        self.model_chooser.addcards = self
        # Create alias for compatibility with Quick Access addon
        self.notetype_chooser = self.model_chooser

        self.processor_widget = QWidget(self)
        self.processor_layout = QHBoxLayout()
        self.processor_label = QLabel("Character to split on:")
        self.processor_text = QLineEdit(self)
        self.processor_text.setMaxLength(1)
        self.processor_text.setFixedWidth(60)
        self.processor_button = QPushButton("Split", self)

        self.processor_button.clicked.connect(self.split_text)

        self.processor_layout.addWidget(self.processor_label)
        self.processor_layout.addWidget(self.processor_text)
        self.processor_layout.addWidget(self.processor_button)
        self.processor_widget.setLayout(self.processor_layout)

        # Add tags field
        tags_widget = QWidget(self)
        tags_layout = QHBoxLayout()
        tags_label = QLabel("Tags:")
        tags_label.setFixedWidth(45)  # Reduced from 80 to give more space to the field
        self.tags_edit = TagEdit(self)
        self.tags_edit.setCol(mw.col)
        # Make tag edit accessible to editor for addons
        self.tags_edit.editor = self.editor
        # Set placeholder text to help users
        self.tags_edit.setPlaceholderText("Enter tags separated by spaces...")
        
        # Add recent tags button
        recent_tags_btn = QPushButton("Recent")
        recent_tags_btn.setMinimumWidth(90)
        recent_tags_btn.clicked.connect(self.show_recent_tags)
        recent_tags_btn.setToolTip("Add recently used tags")
        
        tags_layout.addWidget(tags_label)
        tags_layout.addWidget(self.tags_edit)
        tags_layout.addWidget(recent_tags_btn)
        tags_widget.setLayout(tags_layout)

        # Add informational label
        info_label = QLabel("<b>New notes are divided by line breaks</b><br>"
                           "Use tabs to separate fields within a note")
        info_label.setWordWrap(True)

        self.submit_button.setText("Add")
        self.submit_button.clicked.connect(self.add_current_sentences)

        layout.addWidget(self.model_widget)
        layout.addWidget(self.deck_widget)
        layout.addWidget(tags_widget)
        layout.addWidget(info_label)
        layout.addWidget(self.processor_widget)
        layout.addWidget(self.text_edit)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)
        self.setWindowTitle("MassAdd")
        self.setMinimumHeight(300)
        self.setMinimumWidth(400)

    def show_window(self):
        if self.submit_button is None:
            self.setup_ui()
        self.text_edit.setText("")
        # Don't clear tags - keep them for multiple additions
        self.show()

    def split_text(self):
        text = self.text_edit.toPlainText()
        split_marker = self.processor_text.text()

        if not split_marker:
            showInfo("Please enter a character to split on.")
            return

        new_text = (split_marker + "\n").join(text.split(split_marker))
        self.text_edit.setText(new_text)
        self.processor_text.clear()
    
    def show_recent_tags(self):
        """Show recent tags dialog"""
        from . import recent_tags_dialog
        
        recent_tags = recent_tags_dialog.get_recent_tags()
        if not recent_tags:
            from aqt.utils import tooltip
            tooltip("No recent tags found")
            return
        
        dialog = recent_tags_dialog.RecentTagsDialog(self, recent_tags)
        if dialog.exec():
            selected_tags = dialog.selected_tags
            if selected_tags:
                # Add selected tags to existing tags
                current_tags = self.tags_edit.text().strip()
                if current_tags:
                    # Parse existing tags and add new ones
                    existing = set(mw.col.tags.split(current_tags))
                    existing.update(selected_tags)
                    new_tags = mw.col.tags.join(sorted(existing))
                else:
                    new_tags = mw.col.tags.join(selected_tags)
                self.tags_edit.setText(new_tags)
                from aqt.utils import tooltip
                tooltip(f"Added {len(selected_tags)} tag(s)")

    def add_current_sentences(self):
        deck_id = self.deck_chooser.selectedId()
        model_id = self.model_chooser.selected_notetype_id
        
        if not model_id:
            showInfo("Please select a note type.")
            return
        
        m = mw.col.models.get(model_id)
        
        if not m or not m["flds"]:
            showInfo("Selected note type has no fields.")
            return

        # Get the list of field names for the selected note type
        field_names = [fld["name"] for fld in m["flds"]]
        
        # Get tags from the tag field
        tag_string = self.tags_edit.text().strip()
        tags = mw.col.tags.split(tag_string) if tag_string else []

        # Split the input text into lines (each line is a note)
        lines = self.text_edit.toPlainText().split("\n")
        
        # Filter out empty lines
        lines = [line.strip() for line in lines if line.strip()]

        if not lines:
            showInfo("No content to add.")
            return

        # Add notes with progress indicator
        mw.progress.start(label="Adding notes...", max=len(lines))
        count = 0
        added_note_ids: List[NoteId] = []
        
        for idx, line in enumerate(lines):
            # Split the line into values based on tabs
            values = line.split("\t")
            
            note = Note(mw.col, m)
            
            # Assign values to fields
            for i, field_name in enumerate(field_names):
                if i < len(values):
                    # Assign the corresponding value to the field
                    note[field_name] = values[i].strip()
                else:
                    # If there are more fields than values, assign an empty string
                    note[field_name] = ""
            
            # Add tags to the note
            note.tags = tags.copy()
            
            note.note_type()["did"] = deck_id
            mw.col.addNote(note)
            added_note_ids.append(note.id)
            count += 1
            mw.progress.update(value=idx + 1)

        mw.progress.finish()
        
        # Update the collection without full reset to avoid addon conflicts
        mw.col.reset()
        
        showInfo(f"Added {count} note(s).")
        self.text_edit.setText("")
        
        # Show added notes in browser if enabled
        if gc("show_added_notes", False) and added_note_ids:
            self.show_notes_in_browser(added_note_ids)
        
        # Close window if enabled
        if gc("close_after_adding", False):
            self.close()
    
    def show_notes_in_browser(self, note_ids: List[NoteId]):
        """Open browser and show the added notes"""
        from aqt import dialogs
        browser: Browser = dialogs.open("Browser", mw)
        browser.search_for(f"nid:{','.join(str(nid) for nid in note_ids)}")
        browser.activateWindow()


# Create global instance
MAWindow = MassAddWindow()


def add_massadd_action_to_browser(browser: Browser):
    """Add MassAdd action to browser menubar"""
    if not gc("show_in_browser", True):
        return
    
    action = QAction("🗒 MassAdd", browser)
    browser.form.menubar.addAction(action)
    action.triggered.connect(MAWindow.show_window)


def add_massadd_action_to_main():
    """Add MassAdd action to main window menubar"""
    if not gc("show_in_main_window", True):
        return
    
    action = QAction("🗒 MassAdd", mw)
    mw.form.menubar.addAction(action)
    action.triggered.connect(MAWindow.show_window)


# Initialize addon
add_massadd_action_to_main()
browser_will_show.append(add_massadd_action_to_browser)


# Add config dialog to Anki's add-ons menu
from . import config_dialog
mw.addonManager.setConfigAction(__name__, config_dialog.show_config_dialog)