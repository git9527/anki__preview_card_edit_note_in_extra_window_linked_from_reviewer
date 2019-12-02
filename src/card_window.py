import json

from anki.utils import (
    bodyClass,
)

import aqt
from aqt.utils import (
    restoreGeom,
    saveGeom,
)
from aqt.qt import *
from aqt.webview import AnkiWebView

from .config import gc
from .note_edit import MyEditNote


class CardPreviewWindow(QDialog):
    def __init__(self, parent, mw, txt, bodyclass, nid):
        super(CardPreviewWindow, self).__init__(parent)
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        self.mw = mw
        self.nid = nid
        self.setMinimumHeight(400)
        self.setMinimumWidth(250)
        self.setLayout(mainLayout)
        restoreGeom(self, "anki__standalone_preview_for_card_linkable")
        self.web = AnkiWebView(self)
        self.web.title = "Anki card preview"
        mainLayout.addWidget(self.web)

        blayout = QHBoxLayout()
        
        if gc("edit note externally"):
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
        note = self.mw.col.getNote(self.nid)
        d = MyEditNote(self.mw, note)
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
