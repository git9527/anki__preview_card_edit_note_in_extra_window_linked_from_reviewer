import re

from anki.hooks import (
    runFilter
)
from aqt import mw
from aqt.utils import (
    # mungeQA
    tooltip,
)
from aqt.qt import *

from .config import gc
from .search import sqlite_regexp


def write_to_file(txt, filename):
    with open(filename, "w") as f:
        f.write(txt)


def text_for_card(cid):
    c = mw.col.getCard(cid)
    if gc("linked_cards_show_answer", True):
        txt = c.a()
    else:
        txt = c.q()
    txt = re.sub(r"\[\[type:[^]]+\]\]", "", txt)
    #txt = mungeQA(mw.col, txt)  # 2.1.20:  mungeQA() deprecated; use mw.prepare_card_text_for_display()
    txt = mw.prepare_card_text_for_display(txt)
    side = "answer" if gc("linked_cards_show_answer", True) else "question"
    txt = runFilter("prepareQA", txt, c,
                    "preview"+side.capitalize())
    return txt


def text_for_note(nid):
    # TODO maybe return special card?
    note = mw.col.getNote(nid)
    txt = ""
    for f in note.fields:
        txt += f + "<br><br>"
    return txt


sqlstring = r"""
SELECT
    id
FROM
    notes
WHERE
    flds REGEXP "%sidd\d{13}"
"""


def extract_linked_ids_from_field_content(iscid, notelist):
    outlist = []
    if iscid:
        regex = r'(?<=cidd)(\d{13})'
    else:
        regex = r'(?<=nidd)(\d{13})'
    ro = re.compile(regex)
    for nid in notelist:
        note = mw.col.getNote(nid)
        for f in note.fields:
            mo = ro.search(f)
            if mo:
                outlist.extend(mo.groups())
    return outlist


def createReferencesInMedia():
    # sync seems to remove the function sqlite_regexp - 
    mw.col.db._db.create_function('REGEXP', 2, sqlite_regexp)
    notes_with_cid_refs = mw.col.db.list(sqlstring % "c")
    linkedcids = extract_linked_ids_from_field_content(True, notes_with_cid_refs)
    for cid in linkedcids:
        txt = text_for_card(cid)
        filename = "_card" + str(cid) + ".html"
        write_to_file(txt, filename)
    notes_with_nid_refs = mw.col.db.list(sqlstring % "n")
    linked_nids = extract_linked_ids_from_field_content(False, notes_with_nid_refs)
    for nid in linked_nids:
        txt = text_for_note(nid)
        filename = "_note" + str(nid) + ".html"
        write_to_file(txt, filename) 
    tooltip("Exporting finished.")



rha = QAction("Reference Cards to media folder", mw)
rha.triggered.connect(createReferencesInMedia)
mw.form.menuTools.addAction(rha)