from aqt.qt import QApplication

from .config import gc


def nidcopy(nid):
    prefix = ""
    if gc("browser_table_add_prefix_when_copying", True):
        prefix += gc("prefix_nid", "nidd")
    QApplication.clipboard().setText(prefix + str(nid))


def cidcopy(cid):
    prefix = ""
    if gc("browser_table_add_prefix_when_copying", True):
        prefix += gc("prefix_cid", "cidd")
    QApplication.clipboard().setText(prefix + str(cid))
