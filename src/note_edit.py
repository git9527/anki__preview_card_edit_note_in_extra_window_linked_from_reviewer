# quick mod of aqt/editcurrent.py which has this:
#     Copyright: Ankitects Pty Ltd and contributors
#     -*- coding: utf-8 -*-
#     License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
# (this mod is copyright 2019 ijgnd)

import unicodedata

from aqt import gui_hooks
from aqt.qt import *
from aqt.utils import tooltip
import aqt.editor
from aqt import mw
from aqt.utils import saveGeom, restoreGeom

from .anki_version_detection import anki_point_version
from .config import gc

class MyEditorUpTo49(aqt.editor.Editor):

    # no requireRest
    def onBridgeCmd(self, cmd):
        if not self.note:
            # shutdown
            return
        # focus lost or key/button pressed?
        if cmd.startswith("blur") or cmd.startswith("key"):
            (type, ord, nid, txt) = cmd.split(":", 3)
            ord = int(ord)
            try:
                nid = int(nid)
            except ValueError:
                nid = 0
            if nid != self.note.id:
                print("ignored late blur")
                return

            txt = unicodedata.normalize("NFC", txt)
            txt = self.mungeHTML(txt)
            # misbehaving apps may include a null byte in the text
            txt = txt.replace("\x00", "")
            # reverse the url quoting we added to get images to display
            txt = self.mw.col.media.escapeImages(txt, unescape=True)
            self.note.fields[ord] = txt
            if not self.addMode:
                self.note.flush()
                # self.mw.requireReset()
            if type == "blur":
                self.currentField = None
                # run any filters
                if gui_hooks.editor_did_unfocus_field(False, self.note, ord):
                    # something updated the note; update it after a subsequent focus
                    # event has had time to fire
                    self.mw.progress.timer(100, self.loadNoteKeepingFocus, False)
                else:
                    self.checkValid()
            else:
                gui_hooks.editor_did_fire_typing_timer(self.note)
                self.checkValid()
        # focused into field?
        elif cmd.startswith("focus"):
            (type, num) = cmd.split(":", 1)
            self.currentField = int(num)
            gui_hooks.editor_did_focus_field(self.note, self.currentField)
        elif cmd in self._links:
            self._links[cmd](self)
        else:
            print("uncaught cmd", cmd)


class EditNoteWindowFromThisLinkAddonUpTo49(QDialog):

    def __init__(self, mw, note):
        QDialog.__init__(self, None, Qt.WindowType.Window)
        mw.setupDialogGC(self)
        self.mw = mw
        self.form = aqt.forms.editcurrent.Ui_Dialog()
        self.form.setupUi(self)
        self.setWindowTitle("Anki: Edit underlying note (add-on window)")
        self.setMinimumHeight(400)
        self.setMinimumWidth(250)
        self.form.buttonBox.button(QDialogButtonBox.StandardButton.Close).setShortcut(
                QKeySequence("Ctrl+Return"))
        if False: # gc("when editing note externally - no reset"):
            self.editor = MyEditorUpTo49(self.mw, self.form.fieldsArea, self)
        else:
            self.editor = aqt.editor.Editor(self.mw, self.form.fieldsArea, self)
        self.editor.setNote(note, focusTo=0)
        restoreGeom(self, "note_edit")
        # addHook("reset", self.onReset)
        # self.mw.requireReset()
        self.show()
        self.activateWindow()
        # reset focus after open, taking care not to retain webview
        # pylint: disable=unnecessary-lambda
        self.mw.progress.timer(100, lambda: self.editor.web.setFocus(), False)

    def reject(self):
        self.saveAndClose()

    def saveAndClose(self):
        self.editor.saveNow(self._saveAndClose)  

    def _saveAndClose(self):
        # remHook("reset", self.onReset)
        # r = self.mw.reviewer
        # try:
        #     r.card.load()
        # except:
        #     # card was removed by clayout
        #     pass
        # else:
        #     self.mw.reviewer.cardQueue.append(self.mw.reviewer.card)

        # saveNow calls self.saveTags which calls self.note.flush()
        # self.editor.cleanup()
        saveGeom(self, "note_edit")
        QDialog.reject(self)

    def closeWithCallback(self, onsuccess):
        def callback():
            self._saveAndClose()
            onsuccess()
        self.editor.saveNow(callback)
 





if anki_point_version >= 50:
    from aqt.editcurrent import EditCurrent
    from aqt.utils import disable_help_button, tr

    class EditCurrentModFor50Plus(EditCurrent):
        # It should be possible to use EditCurrent when removing all
        # references to mw.reviewer. These are in only two methods
        # so I overwrite those.

        # copied over from editcurrent.EditCurrent.__init__ as
        # of anki commit 9d6cd4cd7 2022-10-06
        # should be unchanged since Anki 2.1.50
        def __init__(self, mw: aqt.AnkiQt, note) -> None:
            QDialog.__init__(self, None, Qt.WindowType.Window)
            mw.garbage_collect_on_dialog_finish(self)
            self.mw = mw
            self.form = aqt.forms.editcurrent.Ui_Dialog()
            self.form.setupUi(self)
            ### change
            #self.setWindowTitle(tr.editing_edit_current())
            self.setWindowTitle("Anki Add-on: show linked note")
            disable_help_button(self)
            self.setMinimumHeight(400)
            self.setMinimumWidth(250)
            self.form.buttonBox.button(QDialogButtonBox.StandardButton.Close).setShortcut(
                QKeySequence("Ctrl+Return")
            )
            self.editor = aqt.editor.Editor(
                self.mw,
                self.form.fieldsArea,
                self,
                editor_mode=aqt.editor.EditorMode.EDIT_CURRENT,
            )
            ### change
            # self.editor.card = self.mw.reviewer.card
            # self.editor.set_note(self.mw.reviewer.card.note(), focusTo=0)
            self.editor.card = None
            self.editor.set_note(note, focusTo=0)    
            ### change end
            restoreGeom(self, "editcurrent")
            gui_hooks.operation_did_execute.append(self.on_operation_did_execute)
            ### change
            # self.show()

        def reopen(self, mw: aqt.AnkiQt) -> None:
            # if card := self.mw.reviewer.card:
            #    self.editor.set_note(card.note())
            pass




if gc("nid link open in browser"):
    def external_note_dialog(note):
        browser = aqt.dialogs.open("Browser", mw)
        browser.form.searchEdit.lineEdit().setText(f"nid:{note.id}")
        browser.onSearchActivated()
else:
    if anki_point_version <= 49:
        def external_note_dialog(note):
            d = EditNoteWindowFromThisLinkAddonUpTo49(mw, note)
            d.show()
    else:
        def external_note_dialog(note):
            d = EditCurrentModFor50Plus(mw, note)
            d.show()