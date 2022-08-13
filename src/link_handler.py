import aqt
from aqt import mw
from aqt.utils import tooltip

from .anki_version_detection import anki_point_version
from .config import gc, pycmd_card, pycmd_nid


def process_urlcmd(url, external_card_dialog, external_note_dialog):
    # print(f"in process_urlcmd, pycmd_nid is {pycmd_nid} and url is {url}")
    if url.startswith(pycmd_card):
        cid = url.lstrip(pycmd_card)
        try:
            card = mw.col.getCard(int(cid)) if anki_point_version <= 49 else mw.col.get_card(int(cid))
        except:
            tooltip('card with cid "%s" does not exist. Aborting ...' % str(cid))
        else:
            external_card_dialog(card)
            return True
    elif url.startswith(pycmd_nid):
        nid = url.lstrip(pycmd_nid)
        try:
            note = mw.col.getNote(int(nid)) if anki_point_version <= 49 else mw.col.get_note(int(nid))
        except:
            tooltip('Note with nid "%s" does not exist. Aborting ...' % str(nid))
        else:
            if gc("edit note externally"):
                external_note_dialog(note)
            else:
                browser = aqt.dialogs.open("Browser", mw)
                browser.form.searchEdit.lineEdit().setText("nid:{}".format(note.id))
                browser.onSearchActivated()
                browser.form.tableView.selectRow(0)
            return True
    return False 
