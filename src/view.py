import re

from anki.hooks import addHook, wrap
from aqt import gui_hooks
from aqt import mw
from aqt.browser import Browser
from aqt.previewer import Previewer
from aqt.reviewer import Reviewer
from aqt.utils import tooltip

from .card_window import external_card_dialog
from .config import gc, pycmd_card, pycmd_nid
from .link_handler import process_urlcmd
from .note_edit import external_note_dialog


def myLinkHandler(self, url, _old):
    if process_urlcmd(url, external_card_dialog, external_note_dialog):
        return
    else:
        return _old(self, url)
Reviewer._linkHandler = wrap(Reviewer._linkHandler, myLinkHandler, "around")
Previewer._on_bridge_cmd = wrap(Previewer._on_bridge_cmd, myLinkHandler, "around")


def contexthelper(view, menu, selectedtext):
    if not selectedtext:
        return
    if re.match(r"%s\d{13}" % gc("prefix_nid", "nidd"), selectedtext):
        a = menu.addAction('open note in external window')
        a.triggered.connect(lambda _, s=selectedtext: process_selectedtext(s, False))
    if re.match(r"%s\d{13}" % gc("prefix_cid", "cidd"), selectedtext):
        a = menu.addAction('open card in external window')
        a.triggered.connect(lambda _, s=selectedtext: process_selectedtext(s, True))
    if re.match(r"\d{13}", selectedtext):
        o = mw.col.findCards("cid:" + selectedtext, False)
        if len(o) == 1:
            a = menu.addAction('open card in external window')
            a.triggered.connect(lambda _, s=selectedtext: process_selectedtext(s, True))
        o = mw.col.findNotes("nid:" + selectedtext)
        if len(o) == 1:
            a = menu.addAction('open note in external window')
            a.triggered.connect(lambda _, s=selectedtext: process_selectedtext(s, False))


def EditorContextMenu(view, menu):
    editor = view.editor
    selectedtext = editor.web.selectedText()
    contexthelper(view, menu, selectedtext)


def ReviewerContextMenu(view, menu):
    if mw.state != "review":
        return
    selectedtext = view.page().selectedText()
    contexthelper(view, menu, selectedtext)


def process_selectedtext(text, iscard):
    if iscard:
        cid = text.lstrip(gc("prefix_cid", "cidd"))
        try:
            card = mw.col.getCard(int(cid))
        except:
            tooltip('card with cid "%s" does not exist. Aborting ...' % str(cid))
        else:
            external_card_dialog(card)
            return True
    else:
        nid = text.lstrip(gc("prefix_nid", "nidd"))
        try:
            note = mw.col.getNote(int(nid))
        except:
            tooltip('Note with nid "%s" does not exist. Aborting ...' % str(nid))
        else:
            external_note_dialog(note)
            return True


def actually_transform(txt):
    pattern = "(%s)(\\d{13})" % gc("prefix_cid", "cidd")
    repl = """<a href='javascript:pycmd("%s\\2");'>\\1\\2</a>""" % pycmd_card
    txt = re.sub(pattern, repl, txt)
    if gc("edit note externally"):
        pattern = "(%s)(\\d{13})" % gc("prefix_nid", "nidd")
        repl = """<a href='javascript:pycmd("%s\\2");'>\\1\\2</a>""" % pycmd_nid
        txt = re.sub(pattern, repl, txt)
    return txt


def nid_cid_to_hyperlink(text, card, kind):
    if kind in [
        "previewQuestion", 
        "previewAnswer", 
        "reviewQuestion", 
        "reviewAnswer",
        "clayoutQuestion",
        "clayoutAnswer",
    ]:
        return actually_transform(text)
    else:
        return text


def on_profile_loaded():
    """user config only available when profile is loaded"""
    if gc('context menu entries in reviewer', True):
        addHook("AnkiWebView.contextMenuEvent", ReviewerContextMenu)
    if gc('context menu entries in editor', True):
        addHook("EditorWebView.contextMenuEvent", EditorContextMenu)
    if gc("make nid cid clickable", True):
        gui_hooks.card_will_show.append(nid_cid_to_hyperlink)
addHook("profileLoaded", on_profile_loaded)
