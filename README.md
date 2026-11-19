# 🗒 MassAdd

An Anki add-on for mass-adding notes from a block of text.

### Usage
 - Open the MassAdd window from the menubar in the main window or the browser.
   - These shortcuts can be toggled in the config; if you don't use the add-on as much as me, you can turn them off.
 - Choose the note type and deck you would like the new notes to be added to.
 - Optionally enter tags (or click **Recent** to pick from recently used tags). They are added to every new note.
 - Paste the text into the window.
   - By default each new line becomes a separate note.
   - By default fields within a note are separated by a tab. Text before the first tab goes in the first field, and so on. Missing fields are left empty.
 - To make splitting easier, use the **Split** tool to break the text into separate notes at a specific character, for example a full stop (.) or a comma (,).
 - Click **Add** and the notes will be created.

### Custom delimiters
The characters that separate notes and fields can be changed. Click **Change** next to the delimiter info in the MassAdd window, or open the add-on config.
 - Leave a field empty to use the default (line break for notes, tab for fields).
 - Delimiters can be more than one character, e.g. `;;`.
 - You can type `\t` for a tab or `\n` for a line break.
 - The two delimiters must be different.

### Updates

* **2026-11-19**
    * Added configurable note and field delimiters (`note_delimiter`, `field_delimiter`), with a link to change them from the MassAdd window.
    * The Split tool now inserts the current note delimiter.
    * Fixed a Qt5 import error on older Anki versions.

* **2026-01-22**
    * Added tag field to MassAdd window.
    * Implemented code from Recent Tags addon to make tagging easier.

* **2026-01-09**
    * Added config UI.
    * Added `show_added_notes` configuration option.
    * Users can now have the group of mass-added notes displayed in the browser after adding them.

* **2026-01-06**
    * Added `close_after_adding` configuration option.
    * Users can now choose to have the window automatically close after adding notes (default is false).

* **2025-02-05**
    * Updated for Anki 25.02.5 compatibility.  