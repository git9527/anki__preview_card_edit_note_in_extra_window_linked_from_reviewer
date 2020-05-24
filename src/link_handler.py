from aqt import mw
from aqt.utils import tooltip

from .config import gc, pycmd_card, pycmd_nid


def process_urlcmd(url, external_card_dialog, external_note_dialog):
    # print(f"in process_urlcmd, pycmd_nid is {pycmd_nid} and url is {url}")
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
