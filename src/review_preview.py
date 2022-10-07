from anki.hooks import addHook

from aqt.gui_hooks import webview_will_show_context_menu
import aqt
from aqt.qt import *

from .card_window import SingleCardPreviewerMod 
from .nidcidcopy import cidcopy, nidcopy


def shortcut_helper_nid__reviewer():
    if aqt.mw.reviewer.card.nid:
        nidcopy(aqt.mw.reviewer.card.nid)


def shortcut_helper_cid__reviewer():   
    if aqt.mw.reviewer.card.id:
        cidcopy(aqt.mw.reviewer.card.id)


def shortcut_helper_nid__browser_previewer(view, previewer):
    nid = previewer.card().nid
    if nid:
        nidcopy(nid)


def shortcut_helper_cid__browser_previewer(view, previewer):
    cid = previewer.card().id
    if cid:
        cidcopy(cid)


def reviewer_previewer_context_menu(webview, menu):
    parent = webview.parent()
    already_added = False

    # webview.title == previewer might be dangerous since some classes in the previewer
    # don't have the method card()
    if isinstance(parent, (aqt.browser.previewer.BrowserPreviewer,SingleCardPreviewerMod)):
        menutext = "Copy nid"
        action_nid = menu.addAction(menutext)
        qconnect(action_nid.triggered, lambda _, v=webview,p=parent:shortcut_helper_nid__browser_previewer(v,p))

        menutext = "Copy cid"
        action_cid = menu.addAction(menutext)
        qconnect(action_cid.triggered, lambda _, v=webview,p=parent:shortcut_helper_cid__browser_previewer(v,p))
        already_added = True

    # https://forums.ankiweb.net/t/how-to-use-gui-hooks-reviewer-will-show-context-menu/21423/2
    # glutanimate calls "webview.title == "main webview":" shaky
    if aqt.mw.state == "review" and not already_added:
        menutext = "Copy nid"
        action_nid = menu.addAction(menutext)
        qconnect(action_nid.triggered, shortcut_helper_nid__reviewer)

        menutext = "Copy cid"
        action_cid = menu.addAction(menutext)
        qconnect(action_cid.triggered, shortcut_helper_cid__reviewer)  

# note: reviewer_will_show_context_menu hook doesn't help since it calls the More-Button menu
# and not the right click menu.
webview_will_show_context_menu.append(reviewer_previewer_context_menu)
