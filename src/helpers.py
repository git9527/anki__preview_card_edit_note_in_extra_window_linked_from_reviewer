import re

from anki.cards import Card
from anki.hooks import addHook

from aqt import mw
from aqt.utils import tooltip
from aqt import gui_hooks


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


def process_selectedtext(text, iscard):
    if iscard:
        cid = text.lstrip(gc("prefix_cid", "cidd"))
        try:
            card = mw.col.getCard(int(cid))
        except:
            tooltip('card with cid "%s" does not exist. Aborting ...' % str(cid))
        else:
            external_card_dialog(card)
            return True
    else:
        nid = text.lstrip(gc("prefix_nid", "nidd"))
        try:
            note = mw.col.getNote(int(nid))
        except:
            tooltip('Note with nid "%s" does not exist. Aborting ...' % str(nid))
        else:
            external_note_dialog(note)
            return True


def actually_transform(txt):
    pattern = "(%s)(\\d{13})" % gc("prefix_cid", "cidd")
    repl = """<a href='javascript:pycmd("%s\\2");'>\\1\\2</a>""" % pycmd_card
    txt = re.sub(pattern, repl, txt)
    if gc("edit note externally"):
        pattern = "(%s)(\\d{13})" % gc("prefix_nid", "nidd")
        repl = """<a href='javascript:pycmd("%s\\2");'>\\1\\2</a>""" % pycmd_nid
        txt = re.sub(pattern, repl, txt)
    return txt


def nid_cid_to_hyperlink(text, card, kind):
    if kind in [
        "previewQuestion", 
        "previewAnswer", 
        "reviewQuestion", 
        "reviewAnswer",
        "clayoutQuestion",
        "clayoutAnswer",
    ]:
        return actually_transform(text)
    else:
        return text

def on_profile_loaded():
    if gc("make nid cid clickable", True):
        gui_hooks.card_will_show.append(nid_cid_to_hyperlink)
addHook("profileLoaded", on_profile_loaded)