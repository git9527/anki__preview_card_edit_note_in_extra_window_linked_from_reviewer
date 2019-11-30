### Add-on for Anki

- see [Ankiweb](https://ankiweb.net/shared/info/1423933177).
- for license see src/License
- use it at your own risk.

#### alternatives
[Modified reviewer context menu search with browser search](https://ankiweb.net/shared/info/930944997) and maybe [Browser Maximize/Hide Table/Editor](https://ankiweb.net/shared/info/1819291495)

maybe add to "modified reviewer" extra option that directly goes into previewer if 13 digits are selected (that's just a double click)-

Append to lookup_and_preview something like

    if showpreview:
        browser._openPreview()
    
into add_lookup_action something like 

    a = menu.addAction(label)
    a.triggered.connect(lambda _, t=selected: lookup_browser(t, False))
    if re.search("\\d{13}", selected):
        a = menu.addAction("lookup in browser and preview")
        a.triggered.connect(lambda _, t=selected: lookup_and_preview(t, True))
    
#### ideas
- card preview window: option to rate (c.f. advanced previewer)
- card preview window: button to go to next/prev (maybe include two comboboxes to select meaning of "prev", "next": date created, due, etc. and scope deck, parentdeck, all? That's better than the preview where I can only go through the list in the table.
- note window: same buttons as for card preview window, see above.
