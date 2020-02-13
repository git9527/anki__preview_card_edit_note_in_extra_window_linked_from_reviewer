import re

from anki.hooks import (
    runFilter,
    wrap
)
from aqt.reviewer import Reviewer
from aqt.utils import (
    tooltip
)


from .config import gc
from .helpers import pycmd_card, pycmd_nid, process_urlcmd


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
    if process_urlcmd(url):
        return
    else:
        return _old(self, url)
Reviewer._linkHandler = wrap(Reviewer._linkHandler, myLinkHandler, "around")
