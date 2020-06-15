from aqt import gui_hooks
from aqt.qt import (
    QAction,
    QApplication,
    QKeySequence,
    QMenu,
    QShortcut,
    qconnect,
)
from aqt.browser import Browser

from .config import gc
from .nidcidcopy import cidcopy, nidcopy


# the code below shows the shortcut in the context menu
# Downside: another entry in the menu (but without menu entries the shortcuts had no effect?)

def browser_shortcut_helper_nid(browser):
    if browser.card.nid:
        nidcopy(browser.card.nid)


def browser_shortcut_helper_cid(browser):
    if browser.card.id:
        cidcopy(browser.card.id)


def setup_menu_shortcut(self):
    browser = self
    try:
        m = self.menuLinking
    except:
        self.menuLinking = QMenu("&Linking")
        self.menuBar().insertMenu(self.mw.form.menuTools.menuAction(), self.menuLinking)
        m = self.menuLinking

    global action_copy_nid
    action_copy_nid = QAction(browser)
    action_copy_nid.setText("Copy nid")
    qconnect(action_copy_nid.triggered, lambda _, b=browser:browser_shortcut_helper_nid(b))
    ncombo = gc("shortcut: browser: copy nid")
    if ncombo:
        action_copy_nid.setShortcut(QKeySequence(ncombo))
    m.addAction(action_copy_nid)

    global action_copy_cid
    action_copy_cid = QAction(browser)
    action_copy_cid.setText("Copy cid")
    qconnect(action_copy_cid.triggered, lambda _, b=browser:browser_shortcut_helper_cid(b))
    ccombo = gc("shortcut: browser: copy cid")
    if ccombo:
        action_copy_cid.setShortcut(QKeySequence(ccombo))
    m.addAction(action_copy_cid)
gui_hooks.browser_menus_did_init.append(setup_menu_shortcut)


def add_to_table_context_menu(browser, menu):
    menu.addAction(action_copy_nid)
    menu.addAction(action_copy_cid)
gui_hooks.browser_will_show_context_menu.append(add_to_table_context_menu)
