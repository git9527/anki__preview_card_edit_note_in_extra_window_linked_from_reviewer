from aqt import gui_hooks
from aqt.qt import (
    QAction,
    QApplication,
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
