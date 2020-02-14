import re

from anki.hooks import addHook, wrap
from aqt import mw
from aqt.browser import Browser
from aqt.reviewer import Reviewer

from .config import gc
from .helpers import process_urlcmd, process_selectedtext


def myLinkHandler(self, url, _old):
    if process_urlcmd(url):
        return
    else:
        return _old(self, url)
Reviewer._linkHandler = wrap(Reviewer._linkHandler, myLinkHandler, "around")
Browser._on_preview_bridge_cmd = wrap(Browser._on_preview_bridge_cmd, myLinkHandler, "around")


def contexthelper(view, menu, selectedtext):
    if not selectedtext:
        return
    if re.match(r"%s\d{13}" % gc("prefix_nid", "nidd"), selectedtext):
        a = menu.addAction('open note in external window')
        a.triggered.connect(lambda _, s=selectedtext: process_selectedtext(s, False))
    if re.match(r"%s\d{13}" % gc("prefix_cid", "cidd"), selectedtext):
        a = menu.addAction('open card in external window')
        a.triggered.connect(lambda _, s=selectedtext: process_selectedtext(s, True))


def EditorContextMenu(view, menu):
    editor = view.editor
    selectedtext = editor.web.selectedText()
    contexthelper(view, menu, selectedtext)


def ReviewerContextMenu(view, menu):
    if mw.state != "review":
        return
    selectedtext = view.page().selectedText()
    contexthelper(view, menu, selectedtext)


def on_profile_loaded():
    """user config only available when profile is loaded"""
    if gc('context menu entries in reviewer', True):
        addHook("AnkiWebView.contextMenuEvent", ReviewerContextMenu)
    if gc('context menu entries in editor', True):
        addHook("EditorWebView.contextMenuEvent", EditorContextMenu)
addHook("profileLoaded", on_profile_loaded)
