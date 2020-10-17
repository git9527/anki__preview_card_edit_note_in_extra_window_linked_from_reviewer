from aqt import gui_hooks
from aqt.addcards import AddCards
from aqt.browser import Browser
from aqt.editcurrent import EditCurrent
from aqt.editor import Editor

from .config import gc
from .nidcidcopy import cidcopy, nidcopy
from .note_edit import EditNoteWindowFromThisLinkAddon


def append_js_to_Editor(web_content, context):
    if not gc("editor double click to open nidd/cidd"):
        return
    if not isinstance(context, Editor):
        return    
    script_str = """
<script>
var nidd_cidd_regex = new RegExp("((NIDPREFIX|CIDPREFIX)\\\\d{13})");
window.addEventListener('dblclick', function (e) {
    const st = window.getSelection().toString();
    if (st != ""){
        if (nidd_cidd_regex.test(st)){
            pycmd(st);
        }
    }
});
</script>
""".replace("NIDPREFIX", gc("prefix_nid"))\
   .replace("CIDPREFIX", gc("prefix_cid"))
    web_content.head += script_str
gui_hooks.webview_will_set_content.append(append_js_to_Editor)



def js_inserter_after_load(self):
    jsstring = """

"""
    self.web.eval(jsstring)
# gui_hooks.editor_did_init.append(js_inserter_after_load)



dddd = {
    # "AddCards": AddCards,  # never worked for cids, doesn't work for nids in 2.1.28+
    "Browser": Browser,
    "EditCurrent": EditCurrent,  # doesn't hold card/cid
    "EditNoteWindowFromThisLinkAddon": EditNoteWindowFromThisLinkAddon,
}


try:
    AdvancedBrowser = __import__("874215009").advancedbrowser.core.AdvancedBrowser
except:
    pass
else:
    dddd["Browser"] = AdvancedBrowser


def add_to_context(view, menu):
    parent = view.editor.parentWindow
    st = gc("editor context menu show note-id (nid) copy entries in", [])
    cs = []
    for entry in st:
        cs.append(dddd.get(entry))
    nid_showin = tuple(cs)
    if isinstance(parent, nid_showin):
        a = menu.addAction("Copy nid")
        a.triggered.connect(lambda _, nid=view.editor.note.id: nidcopy(nid))
    if isinstance(parent, Browser) and gc("editor context menu show card-id (cid) copy entries in Browser"):
        a = menu.addAction("Copy cid")
        a.triggered.connect(lambda _, cid=parent.card.id: cidcopy(cid))
gui_hooks.editor_will_show_context_menu.append(add_to_context)
