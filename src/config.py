from aqt import mw


def gc(arg, fail=False):
    conf = mw.addonManager.getConfig(__name__.split(".")[0])
    if conf:
        return conf.get(arg, fail)
    else:
        return fail


pycmd_card = "card_in_extra_window"
pycmd_nid = "note_in_extra_window"