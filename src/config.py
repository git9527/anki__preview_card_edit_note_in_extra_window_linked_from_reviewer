from aqt import mw


def gc(arg, fail=False):
    conf = mw.addonManager.getConfig(__name__.split(".")[0])
    if conf:
        return conf.get(arg, fail)
    else:
        return fail


pycmd_card = gc("prefix_cid")  # "card_in_extra_window"
pycmd_nid = gc("prefix_nid")  # "note_in_extra_window"


from anki.utils import pointVersion
if pointVersion() <= 49:
    my_point_version = pointVersion
else:
    from anki.utils import point_version
    my_point_version = point_version
