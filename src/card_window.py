# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
# The classes in this file are a minimal modification of the preview related methods
# from aqt.browser.Browser
# Copyright: Ankitects Pty Ltd and contributors
#            ijgnd

from __future__ import annotations

import json
import re
import time
from typing import Union # Callable, List, Optional

from anki.hooks import runFilter
from anki.lang import _
from anki.sound import clearAudioQueue, allSounds, play
from anki.utils import (
    bodyClass,
)

import aqt
from aqt import mw
from aqt import gui_hooks
from aqt.browser import PreviewDialog
from aqt.qt import *
from aqt.sound import av_player, play_clicked_audio
from aqt.theme import theme_manager
from aqt.utils import (
    restoreGeom,
    saveGeom,
    tooltip,
)
from aqt.webview import AnkiWebView

from .config import gc
from .helpers import pycmd_card, pycmd_nid
from .note_edit import MyEditNote


# same functions here to circumvent circular imports, TODO
def external_card_dialog(card):
    d = CardPreviewWindowClass(mw, mw, card)
    d.show()


def external_note_dialog(nid):
    d = MyEditNote(mw, nid)
    d.show()


def process_urlcmd(url):
    if url.startswith(pycmd_card):
        cid = url.lstrip(pycmd_card)
        try:
            card = mw.col.getCard(int(cid))
        except:
            tooltip('card with cid "%s" does not exist. Aborting ...' % str(cid))
        else:
            external_card_dialog(card)
            return True
    elif gc("edit note externally") and url.startswith(pycmd_nid):
        nid = url.lstrip(pycmd_nid)
        try:
            note = mw.col.getNote(int(nid))
        except:
            tooltip('Note with nid "%s" does not exist. Aborting ...' % str(nid))
        else:
            external_note_dialog(note)
            return True


class CardPreviewWindowClass(QDialog):
    _previewTimer = None
    _lastPreviewRender: Union[int, float] = 0
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
        vbox.setContentsMargins(0, 0, 0, 0)
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
        # if not self._previewWindow:
        #     return
        # current = self.currentRow()
        # canBack = current > 0 or (
        #     current == 0
        #     and self._previewState == "answer"
        #     and not self._previewBothSides
        # )
        # self._previewPrev.setEnabled(not not (self.singleCard and canBack))
        # canForward = (
        #     self.currentRow() < self.model.rowCount(None) - 1
        #     or self._previewState == "question"
        # )
        # self._previewNext.setEnabled(not not (self.singleCard and canForward))


    def _closePreview(self):
        self.close()
        self._onClosePreview()

    def _onClosePreview(self):
        self._previewPrev = self._previewNext = None

    def _setupPreviewWebview(self):
        jsinc = [
            "jquery.js",
            "browsersel.js",
            "mathjax/conf.js",
            "mathjax/MathJax.js",
            "reviewer.js",
        ]
        self._previewWeb.stdHtml(
            self.mw.reviewer.revHtml(), css=["reviewer.css"], js=jsinc
        )
        self._previewWeb.set_bridge_command(
            self._on_preview_bridge_cmd,
            PreviewDialog(dialog=self, browser=self),
        )

    def _on_preview_bridge_cmd(self, cmd: str) -> Any:
        if cmd.startswith("play:"):
            play_clicked_audio(cmd, self.card)
        process_urlcmd(cmd)


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
            if self._previewState == "answer":
                func = "_showAnswer"
                txt = c.a()
            txt = re.sub(r"\[\[type:[^]]+\]\]", "", txt)

            bodyclass = theme_manager.body_classes_for_card_ord(c.ord)

            if self.mw.reviewer.autoplay(c):
                if self._previewBothSides:
                    # if we're showing both sides at once, remove any audio
                    # from the answer that's appeared on the question already
                    question_audio = c.question_av_tags()
                    only_on_answer_audio = [
                        x for x in c.answer_av_tags() if x not in question_audio
                    ]
                    audio = question_audio + only_on_answer_audio
                elif self._previewState == "question":
                    audio = c.question_av_tags()
                else:
                    audio = c.answer_av_tags()
                av_player.play_tags(audio)

            txt = self.mw.prepare_card_text_for_display(txt)
            txt = gui_hooks.card_will_show(
                txt, c, "preview" + self._previewState.capitalize()
            )
            self._lastPreviewState = self._previewStateAndMod()
        self._updatePreviewButtons()
        self._previewWeb.eval("{}({},'{}');".format(func, json.dumps(txt), bodyclass))
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