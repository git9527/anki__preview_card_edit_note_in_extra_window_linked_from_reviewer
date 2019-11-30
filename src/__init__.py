"""
anki-addon: 

Copyright (c) 2019 ignd
          (c) Ankitects Pty Ltd and contributors


This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import json
import re

from anki.hooks import (
    addHook,
    runFilter,
    wrap,
)
from anki.utils import (
    bodyClass,
)
from anki.sound import clearAudioQueue, allSounds, play

import aqt
from aqt.qt import *
from aqt.reviewer import Reviewer
from aqt.utils import (
    mungeQA,
    restoreGeom,
    saveGeom,
    showInfo,
    tooltip
)
from aqt.webview import AnkiWebView

from .config import gc
from .note_edit import MyEditNote


class MyDialog(QDialog):
    def __init__(self, parent, mw, txt, bodyclass, nid):
        super(MyDialog, self).__init__(parent)
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        self.mw = mw
        self.nid = nid
        self.setLayout(mainLayout)
        restoreGeom(self, "anki__standalone_preview_for_card_linkable")
        self.web = AnkiWebView(self)
        self.web.title = "Anki card preview"
        self.web.contextMenuEvent = self.contextMenuEvent
        mainLayout.addWidget(self.web)

        blayout = QHBoxLayout()
        
        if gc("edit note externally, dangerous"):
            edit = QPushButton("Edit")
            edit.clicked.connect(self.onEdit)
            blayout.addWidget(edit)

        edit = QPushButton("show in Browser")
        edit.clicked.connect(self.onBrowser)
        blayout.addWidget(edit)
        
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)     
        blayout.addItem(spacerItem)
        
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel)
        self.buttonBox.rejected.connect(self.onReject)
        QMetaObject.connectSlotsByName(self)
        blayout.addWidget(self.buttonBox)
        
        mainLayout.addLayout(blayout)
        self.exit_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.exit_shortcut.activated.connect(self.onReject)

        # adjusted from aqt.browser.Browser._setupPreviewWebview
        jsinc = ["jquery.js","browsersel.js",
                 "mathjax/conf.js", "mathjax/MathJax.js",
                 "reviewer.js"]
        self.web.stdHtml(self.mw.reviewer.revHtml(),
                                 css=["reviewer.css"],
                                 js=jsinc)
        self.web.eval(
            "{}({},'{}');window.scrollTo(0, 0);".format("_showAnswer", json.dumps(txt), bodyclass))
    
    def onEdit(self):
        d = MyEditNote(self.mw, self.nid)
        d.show()
        QDialog.reject(self)
    
    def onBrowser(self):
        browser = aqt.dialogs.open("Browser", self.mw)
        query = '"nid:' + str(self.nid) + '"'
        browser.form.searchEdit.lineEdit().setText(query)
        browser.onSearchActivated()


    def onReject(self):
        saveGeom(self, "anki__standalone_preview_for_card_linkable")
        QDialog.reject(self)

    def closeEvent(self, evnt):
        saveGeom(self, "anki__standalone_preview_for_card_linkable")


def external_card_dialog(self, cid):  # self=reviewer
    c = self.mw.col.getCard(cid)
    bodyclass = bodyClass(self.mw.col, c)
    questionAudio = []
    txt = c.a()
    txt = re.sub(r"\[\[type:[^]]+\]\]", "", txt)
    clearAudioQueue()
    if self.autoplay(c):
        # if we're showing both sides at once, play question audio first
        for audio in questionAudio:
            play(audio)
        # then play any audio that hasn't already been played
        for audio in allSounds(txt):
            if audio not in questionAudio:
                play(audio)
    txt = mungeQA(self.mw.col, txt)
    txt = runFilter("prepareQA", txt, c,
                    "preview"+"answer".capitalize())
    d = MyDialog(self.mw, self.mw, txt, bodyclass, c.nid)
    d.show()


def external_note_dialog(self, nid):  # self=reviewer
    d = MyEditNote(self.mw, nid)
    d.show()

pycmd_card = "card_in_extra_window"
pycmd_nid = "note_in_extra_window"


def onMungeQA(self, buf, _old):
    out = _old(self, buf)
    pattern = "(cid:\\d{13})"
    repl = """<a href='javascript:pycmd("%s\\1");'>\\1</a>""" % pycmd_card
    out = re.sub(pattern, repl, out)
    if gc("edit note externally, dangerous"):
        pattern = "(nid:\\d{13})"
        repl = """<a href='javascript:pycmd("%s\\1");'>\\1</a>""" % pycmd_nid
        out = re.sub(pattern, repl, out)
    return out
Reviewer._mungeQA = wrap(Reviewer._mungeQA, onMungeQA, "around")


def myLinkHandler(self, url, _old):
    if url.startswith(pycmd_card):
        cid = url.lstrip(pycmd_card)[1:]  # remove ":"
        external_card_dialog(self, int(cid))
    elif gc("edit note externally, dangerous") and url.startswith(pycmd_nid):
        nid = url.lstrip(pycmd_nid)[1:]  # remove ":"
        external_note_dialog(self, int(nid))
    else:
        return _old(self, url)
Reviewer._linkHandler = wrap(Reviewer._linkHandler, myLinkHandler, "around")



def nidcopy(browser):
    QApplication.clipboard().setText(str(browser.card.nid))


def cidcopy(browser):
    QApplication.clipboard().setText(str(browser.card.id))


def add_to_table_context_menu(browser, menu):
    ca = QAction(browser)
    ca.setText("Copy cid")
    ca.triggered.connect(lambda: cidcopy(browser))
    menu.addAction(ca)
    if gc("edit note externally, dangerous"):
        na = QAction(browser)
        na.setText("Copy nid")
        na.triggered.connect(lambda: nidcopy(browser))
        menu.addAction(na)
addHook("browser.onContextMenu", add_to_table_context_menu)
