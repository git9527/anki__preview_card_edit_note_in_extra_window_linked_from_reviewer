# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
# The classes in this file are a minimal modification of the preview related methods
# from aqt.browser.Browser
# Copyright: Ankitects Pty Ltd and contributors
#            ijgnd

import json
import re
import time

from anki.hooks import runFilter
from anki.lang import _
from anki.sound import clearAudioQueue, allSounds, play
from anki.utils import (
    bodyClass,
)

import aqt
from aqt.utils import (
    mungeQA,
    restoreGeom,
    saveGeom,
)
from aqt.qt import *
from aqt.webview import AnkiWebView

from .config import gc
from .note_edit import MyEditNote
 

class MyCardPreviewWindow(QDialog):
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



class CardPreviewWindowClass(QDialog):
    _previewTimer = None
    _lastPreviewRender = 0
    _lastPreviewState = None
    _previewCardChanged = False

    def __init__(self, parent, mw, card):
        self.mw = mw
        self.col = self.mw.col
        self.card = card
        super(CardPreviewWindowClass, self).__init__(parent)
        self._previewState = "answer" if self.showAnswerInitially() else "question"
        self._lastPreviewState = None
        self.setWindowTitle(_("Preview"))
        self.finished.connect(self._onPreviewFinished)
        self.silentlyClose = True
        vbox = QVBoxLayout()
        vbox.setContentsMargins(0,0,0,0)
        self._previewWeb = AnkiWebView()
        vbox.addWidget(self._previewWeb)

        blayout = QHBoxLayout()

        """
        self.showModify = QPushButton("<>")
        self.showModify.setFixedWidth(25)
        # self.showRate.setShortcut(QKeySequence("M"))
        # self.showRate.setToolTip(_("Shortcut key: %s" % "M"))
        self.showModify.clicked.connect(self.onShowModify)
        blayout.addWidget(self.showModify)

        self.showRate = QPushButton("E")  # ease - "R" is already used for replay audio
        self.showRate.setFixedWidth(25)
        # self.showRate.setShortcut(QKeySequence("E"))
        # self.showRate.setToolTip(_("Shortcut key: %s" % "E"))
        self.showRate.clicked.connect(self.onShowRatingBar)
        blayout.addWidget(self.showRate)
        """

        if gc("edit note externally"):
            edit = QPushButton("Edit")
            edit.clicked.connect(self.onEdit)
            blayout.addWidget(edit)

        edit = QPushButton("show in Browser")
        edit.clicked.connect(self.onBrowser)
        blayout.addWidget(edit)
        
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)     
        blayout.addItem(spacerItem)

        bbox = QDialogButtonBox()
        self._previewReplay = bbox.addButton(_("Replay Audio"), QDialogButtonBox.ActionRole)
        self._previewReplay.setAutoDefault(False)
        self._previewReplay.setShortcut(QKeySequence("R"))
        self._previewReplay.setToolTip(_("Shortcut key: %s" % "R"))

        """
        self._previewPrev = bbox.addButton("<", QDialogButtonBox.ActionRole)
        self._previewPrev.setAutoDefault(False)
        self._previewPrev.setShortcut(QKeySequence("Left"))
        self._previewPrev.setToolTip(_("Shortcut key: Left arrow"))

        self._previewNext = bbox.addButton(">", QDialogButtonBox.ActionRole)
        self._previewNext.setAutoDefault(True)
        self._previewNext.setShortcut(QKeySequence("Right"))
        self._previewNext.setToolTip(_("Shortcut key: Right arrow or Enter"))

        self._previewPrev.clicked.connect(self._onPreviewPrev)
        self._previewNext.clicked.connect(self._onPreviewNext)
        """
        self._previewReplay.clicked.connect(self._onReplayAudio)

        self.previewShowBothSides = QCheckBox(_("Show Answer"))
        self.previewShowBothSides.setShortcut(QKeySequence("A"))
        self.previewShowBothSides.setToolTip(_("Shortcut key: %s" % "A"))
        bbox.addButton(self.previewShowBothSides, QDialogButtonBox.ActionRole)
        self._previewBothSides = self.showAnswerInitially()
        self.previewShowBothSides.setChecked(self._previewBothSides)
        self.previewShowBothSides.toggled.connect(self._onPreviewShowBothSides)

        self._setupPreviewWebview()

        blayout.addWidget(bbox)
        vbox.addLayout(blayout)
        self.setLayout(vbox)
        restoreGeom(self, "preview_1423933177")
        self.show()
        self._renderPreview(True)


    def showAnswerInitially(self):
        isq = False
        if gc("card_preview__default_is_answer"):
            isq ^= True
        overrides = gc("card_preview__override_toggle_from_default_for_notetypes")
        if self.card.model()['name'] in overrides:
            isq ^= True
        return isq

    def onShowRatingBar(self):
        pass

    def onShowModify(self):
        pass

    def onEdit(self):
        note = self.mw.col.getNote(self.card.nid)
        d = MyEditNote(self.mw, note)
        d.show()
        QDialog.reject(self)
    
    def onBrowser(self):
        browser = aqt.dialogs.open("Browser", self.mw)
        query = '"nid:' + str(self.card.nid) + '"'
        browser.form.searchEdit.lineEdit().setText(query)
        browser.onSearchActivated()


    def _onPreviewFinished(self, ok):
        saveGeom(self, "preview_1423933177")
        self.mw.progress.timer(100, self._onClosePreview, False)

    def _onPreviewPrev(self):
        if self._previewState == "answer" and not self._previewBothSides:
            self._previewState = "question"
            self._renderPreview()
        else:
            pass
            # self.editor.saveNow(lambda: self._moveCur(QAbstractItemView.MoveUp))

    def _onPreviewNext(self):
        if self._previewState == "question":
            self._previewState = "answer"
            self._renderPreview()
        else:
            pass 
            # self.editor.saveNow(lambda: self._moveCur(QAbstractItemView.MoveDown))

    def _onReplayAudio(self):
        self.mw.reviewer.replayAudio(self)

    def _updatePreviewButtons(self):
        pass
        # current = self.currentRow()
        # canBack = (current > 0 or (current == 0 and self._previewState == "answer"
        #                            and not self._previewBothSides))
        # self._previewPrev.setEnabled(not not (self.singleCard and canBack))
        # canForward = self.currentRow() < self.model.rowCount(None) - 1 or \
        #              self._previewState == "question"
        # self._previewNext.setEnabled(not not (self.singleCard and canForward))

    def _closePreview(self):
        self.close()
        self._onClosePreview()

    def _onClosePreview(self):
        self._previewPrev = self._previewNext = None

    def _setupPreviewWebview(self):
        jsinc = ["jquery.js","browsersel.js",
                 "mathjax/conf.js", "mathjax/MathJax.js",
                 "reviewer.js"]
        self._previewWeb.stdHtml(self.mw.reviewer.revHtml(),
                                 css=["reviewer.css"],
                                 js=jsinc)


    def _renderPreview(self, cardChanged=False):
        self._cancelPreviewTimer()
        # Keep track of whether _renderPreview() has ever been called
        # with cardChanged=True since the last successful render
        self._previewCardChanged |= cardChanged
        # avoid rendering in quick succession
        elapMS = int((time.time() - self._lastPreviewRender)*1000)
        if elapMS < 500:
            self._previewTimer = self.mw.progress.timer(
                500-elapMS, self._renderScheduledPreview, False)
        else:
            self._renderScheduledPreview()

    def _cancelPreviewTimer(self):
        if self._previewTimer:
            self._previewTimer.stop()
            self._previewTimer = None

    def _renderScheduledPreview(self):
        self._cancelPreviewTimer()
        self._lastPreviewRender = time.time()

        c = self.card
        func = "_showQuestion"
        if False: #not c or not self.singleCard:
            txt = _("(please select 1 card)")
            bodyclass = ""
            self._lastPreviewState = None
        else:
            if self._previewBothSides:
                self._previewState = "answer"
            elif self._previewCardChanged:
                self._previewState = "question"

            currentState = self._previewStateAndMod()
            if currentState == self._lastPreviewState:
                # nothing has changed, avoid refreshing
                return

            # need to force reload even if answer
            txt = c.q(reload=True)
            questionAudio = []
            if self._previewBothSides:
                questionAudio = allSounds(txt)
            if self._previewState == "answer":
                func = "_showAnswer"
                txt = c.a()
            txt = re.sub(r"\[\[type:[^]]+\]\]", "", txt)

            bodyclass = bodyClass(self.mw.col, c)

            clearAudioQueue()
            if self.mw.reviewer.autoplay(c):
                # if we're showing both sides at once, play question audio first
                for audio in questionAudio:
                    play(audio)
                # then play any audio that hasn't already been played
                for audio in allSounds(txt):
                    if audio not in questionAudio:
                        play(audio)

            txt = mungeQA(self.col, txt)
            txt = runFilter("prepareQA", txt, c,
                            "preview"+self._previewState.capitalize())
            self._lastPreviewState = self._previewStateAndMod()
        self._updatePreviewButtons()
        self._previewWeb.eval(
            "{}({},'{}');".format(func, json.dumps(txt), bodyclass))
        self._previewCardChanged = False

    def _onPreviewShowBothSides(self, toggle):
        self._previewBothSides = toggle
        self.col.conf["previewBothSides"] = toggle
        self.col.setMod()
        if self._previewState == "answer" and not toggle:
            self._previewState = "question"
        self._renderPreview()

    def _previewStateAndMod(self):
        c = self.card
        n = c.note()
        n.load()
        return (self._previewState, c.id, n.mod)