# 🗒 MassAdd

An Anki add on for mass-adding cards from a block of text.

### Usage
 - Open the MassAdd window from the tools menu or shortcut in the menubar
   - The shortcuts can be toggled in the config; if you don't use the addon as much as me, you can turn them off.
 - Choose the card type and deck you would like the new cards to be added as. Please
   note that due to anki requiring the first field of a card be non-blank the first
   field of the selected card type will be used to add the text.
 - Copy and paste the text into the window.
 - Each new line of text will be a seperate card. To make this easier you can
   use the 'Add' button to seperate the text into new lines based on a specific
   character, for example you may want to use a full-stop (.) or a comma(,).
 - Click 'submit' and the cards will be created.

### Updates

* **2026-01-22**
    * Added tag field to MassAdd window.
    * Implemented code from Recent Tags addon to make tagging easier.

* **2026-01-09**
    * Added config UI.
    * Added `show_added_notes` configuration option.
    * Users can now have the group of mass-added notes displayed in the browser after adding them.

* **2026-01-06**
    * Added `close_after_add` configuration option.
    * Users can now choose to have the window automatically close after adding cards (default is false).
* **2025-02-05**
    * Updated for Anki 25.02.5 compatibility.
