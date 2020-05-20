import aqt
from aqt.previewer import SingleCardPreviewer
from aqt.previewer import CardListPreviewer
from aqt.qt import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QKeySequence,
    QPushButton,
    qconnect,
)
from aqt.utils import tooltip


from .config import gc
from .link_handler import process_urlcmd
from .note_edit import external_note_dialog, MyEditNote



class SingleCardPreviewerMod(SingleCardPreviewer):
    def _on_bridge_cmd(self, cmd):
        super()._on_bridge_cmd(cmd)
        process_urlcmd(cmd, external_card_dialog, external_note_dialog)

    def _create_gui(self):
        super()._create_gui()

        self.vbox.removeWidget(self.bbox)
        self.bottombar = QHBoxLayout()

        self.browser_button = QPushButton("show in browser")
        #self.browser_button.setShortcut(QKeySequence("b"))
        #self.browser_button.setToolTip("Shortcut key: %s" % "b")
        self.browser_button.clicked.connect(self._on_browser_button)
        self.bottombar.addWidget(self.browser_button)

        self.edit_button = self.bbox.addButton("edit", QDialogButtonBox.HelpRole)
        #self.edit_button.setShortcut(QKeySequence("e"))
        #self.edit_button.setToolTip("Shortcut key: %s" % "e")
        self.edit_button.clicked.connect(self._on_edit_button)
        self.bottombar.addWidget(self.edit_button)

        self.showRate = QPushButton("G")  # grade - "R" is already used for replay audio
        self.showRate.setFixedWidth(25)
        # self.showRate.setShortcut(QKeySequence("g"))
        # self.showRate.setToolTip("Shortcut key: %s" % "G")
        self.showRate.clicked.connect(self.onShowRatingBar)
        # self.bottombar.addWidget(self.showRate)

        self.bottombar.addWidget(self.bbox)
        self.vbox.addLayout(self.bottombar)

    def _setup_web_view(self):
        super()._setup_web_view()
        for child in self.bbox.children():
            if isinstance(child, QCheckBox):
                self.both_sides_button = child
        self._show_both_sides = self.check_preview_both_config()
        self.both_sides_button.setChecked(self._show_both_sides)

    def check_preview_both_config(self):
        # if True both sides are shown
        showboth = False
        if gc("card_preview__default_is_answer"):
            showboth ^= True
        overrides = gc("card_preview__override_toggle_from_default_for_notetypes")
        if self.card().model()['name'] in overrides:
            showboth ^= True
        return showboth

    def _on_browser_button(self):
        tooltip('browser clicked')
        browser = aqt.dialogs.open("Browser", self.mw)
        query = '"nid:' + str(self.card().nid) + '"'
        browser.form.searchEdit.lineEdit().setText(query)
        browser.onSearchActivated()

    def _on_edit_button(self):
        note = self.mw.col.getNote(self.card().nid)
        d = MyEditNote(self.mw, note)
        d.show()
        QDialog.reject(self)

    def onShowRatingBar(self):
        pass


def external_card_dialog(card):
    d = SingleCardPreviewerMod(card=card, parent=aqt.mw, mw=aqt.mw, on_close=lambda:None)
    d.open()
