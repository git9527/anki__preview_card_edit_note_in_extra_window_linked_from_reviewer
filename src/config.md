### config keys

- `"transform quoted for these notetypes"`: You can add note type (model) names or ids into this list. My add-on transforms entries like nidd1234567890123 into clickable hyperlinks in the reviewer and previewer. If in your card template you have a field in some javascript code using backticks like ``` var myfield = `{{fieldname}}` ``` this transformation from a simple string like nidd1234567890123 to a clickable hyperlink only works if you add your note type to this config key. Limitation: For these note types the transformation in fields that are not surrounded by backticks in your card template no longer works.

### technical note about a minor feature removed from my add-on

- The behavior of the Add dialog recently changed. In old Anki verisons until Spring 2020 when 
you opened an Add window Anki had already assigned a preliminary note-id (nid) to the note you 
were creating in the Add window. So in the past I could add a context menu entry "copy note-id"
into the Add window. But in Anki 2.1.28 there was a change and the note-id is only assigned 
after you click the "Add" button in the lower right of the Add window. For details see
[here](https://forums.ankiweb.net/t/assign-note-id-to-new-notes-in-addnote-window-revert-a-change-in-2-1-28/2354).
So setting "AddCards" for `editor context menu show note-id (nid) copy entries in` no longer has any
effect.


