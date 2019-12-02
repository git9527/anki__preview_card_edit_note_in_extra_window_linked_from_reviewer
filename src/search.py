import re
from functools import lru_cache
from anki.hooks import addHook
from aqt import mw


@lru_cache()  # Memoize decorator to speed up
def create_regex(expr):
    regex = re.compile(expr)
    return regex

def sqlite_regexp(expr, item):
    regex = create_regex(expr)
    return regex.search(item) is not None

# addHook('profileLoaded', lambda: mw.col.db._db.create_function('REGEXP', 2, sqlite_regexp))