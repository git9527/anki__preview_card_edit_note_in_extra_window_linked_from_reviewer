import re

from anki.hooks import (
    runFilter,
    wrap
)
from anki.sound import clearAudioQueue, allSounds, play
from anki.utils import (
    bodyClass,
)
from aqt.reviewer import Reviewer
from aqt.utils import (
    mungeQA,
    tooltip
)

from .card_window import MyCardPreviewWindow, CardPreviewWindowClass
from .config import gc
from .note_edit import MyEditNote


def external_card_dialog(self, card):  # self=reviewer
    """
    # this code is for my first version that used less code from the browser preview functions
    # so that I had to do the preprocessing of the card here. 
        c = card
        bodyclass = bodyClass(self.mw.col, c)
        questionAudio = []
        if gc("linked_cards_show_answer", True):
            txt = c.a()
        else:
            txt = c.q()
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
        side = "answer" if gc("linked_cards_show_answer", True) else "question"
        txt = runFilter("prepareQA", txt, c,
                        "preview"+side.capitalize())
        d = MyCardPreviewWindow(self.mw, self.mw, txt, bodyclass, c.nid)
    """
    d = CardPreviewWindowClass(self.mw, self.mw, card)
    d.show()


def external_note_dialog(self, nid):  # self=reviewer
    d = MyEditNote(self.mw, nid)
    d.show()

pycmd_card = "card_in_extra_window"
pycmd_nid = "note_in_extra_window"


def onMungeQA(self, buf, _old):
    out = _old(self, buf)
    pattern = "(cidd\\d{13})"
    repl = """<a href='javascript:pycmd("%s\\1");'>\\1</a>""" % pycmd_card
    out = re.sub(pattern, repl, out)
    if gc("edit note externally"):
        pattern = "(nidd\\d{13})"
        repl = """<a href='javascript:pycmd("%s\\1");'>\\1</a>""" % pycmd_nid
        out = re.sub(pattern, repl, out)
    return out
Reviewer._mungeQA = wrap(Reviewer._mungeQA, onMungeQA, "around")


def myLinkHandler(self, url, _old):
    if url.startswith(pycmd_card):
        cid = url.lstrip(pycmd_card)
        try:
            card = self.mw.col.getCard(int(cid))
        except:
            tooltip('card with cid "%s" does not exist. Aborting ...' % str(cid))
        else:
            external_card_dialog(self, card)
    elif gc("edit note externally") and url.startswith(pycmd_nid):
        nid = url.lstrip(pycmd_nid)
        try:
            note = self.mw.col.getNote(int(nid))
        except:
            tooltip('Note with nid "%s" does not exist. Aborting ...' % str(nid))
        else:
            external_note_dialog(self, note)
    else:
        return _old(self, url)
Reviewer._linkHandler = wrap(Reviewer._linkHandler, myLinkHandler, "around")
