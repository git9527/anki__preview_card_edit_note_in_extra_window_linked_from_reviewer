from anki.hooks import addHook
from aqt.qt import *
from aqt.browser import Browser

from .config import gc


def nidcopy(browser):
    QApplication.clipboard().setText(str(browser.card.nid))


def cidcopy(browser):
    QApplication.clipboard().setText(str(browser.card.id))


def add_to_table_context_menu(browser, menu):
    ca = QAction(browser)
    ca.setText("Copy cid")
    ca.triggered.connect(lambda: cidcopy(browser))
    menu.addAction(ca)
    if gc("edit note externally"):
        na = QAction(browser)
        na.setText("Copy nid")
        na.triggered.connect(lambda: nidcopy(browser))
        menu.addAction(na)
addHook("browser.onContextMenu", add_to_table_context_menu) 


def add_to_context(view, menu):
    if gc("editor context menu in browser show cid/nid copy entries"):
        browser = view.editor.parentWindow
        if not isinstance(browser, Browser):
            print('not in browser')
            return
        a = menu.addAction("Copy cid")
        a.triggered.connect(lambda _, b=browser: cidcopy(b))
        a = menu.addAction("Copy nid")
        a.triggered.connect(lambda _, b=browser: nidcopy(b))
addHook("EditorWebView.contextMenuEvent", add_to_context)