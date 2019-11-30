from aqt import mw

def gc(arg, fail=False):
    return mw.addonManager.getConfig(__name__.split(".")[0]).get(arg, fail)