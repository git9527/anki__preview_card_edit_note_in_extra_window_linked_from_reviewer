from aqt import mw
from aqt.utils import tooltip


pycmd_card = "card_in_extra_window"
pycmd_nid = "note_in_extra_window"

from .config import gc
from .card_window import CardPreviewWindowClass
from .note_edit import MyEditNote


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
    return False