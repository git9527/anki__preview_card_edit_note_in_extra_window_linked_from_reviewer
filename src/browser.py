from aqt import gui_hooks
from aqt.qt import (
    QAction,
    QApplication,
    QKeySequence,
    QShortcut,
    qconnect,
)
from aqt.browser import Browser

from .config import gc
from .nidcidcopy import cidcopy, nidcopy


def add_to_table_context_menu(browser, menu):
    ca = QAction(browser)
    ca.setText("Copy cid")
    ca.triggered.connect(lambda _, cid=browser.card.id: cidcopy(cid))
    menu.addAction(ca)
    if gc("edit note externally"):
        na = QAction(browser)
        na.setText("Copy nid")
        na.triggered.connect(lambda _, nid=browser.card.nid: nidcopy(nid))
        menu.addAction(na)
gui_hooks.browser_will_show_context_menu.append(add_to_table_context_menu)


def browser_shortcut_helper_nid(browser):
    if browser.card.nid:
        nidcopy(browser.card.nid)


def browser_shortcut_helper_cid(browser):
    if browser.card.id:
        cidcopy(browser.card.id)


def set_shortcuts(browser):
    ncombo = gc("shortcut: browser: copy nid")
    ccombo = gc("shortcut: browser: copy cid")
    if ncombo:
        nidd_shortcut = QShortcut(QKeySequence(ncombo), browser)
        qconnect(nidd_shortcut.activated, lambda b=browser:browser_shortcut_helper_nid(b))
    if ccombo:
        cidd_shortcut = QShortcut(QKeySequence(ccombo), browser)
        qconnect(cidd_shortcut.activated, lambda b=browser:browser_shortcut_helper_cid(b))
gui_hooks.browser_menus_did_init.append(set_shortcuts)
