from aqt import gui_hooks
from aqt.editor import Editor

from .config import gc


def append_js_to_Editor(web_content, context):
    if not gc("editor double click to open nidd/cidd"):
        return
    if not isinstance(context, Editor):
        return    
    script_str = """
<script>
var nidd_cidd_regex = new RegExp("((NIDPREFIX|CIDPREFIX)\\\\d{13})");
window.addEventListener('dblclick', function (e) {
    const st = window.getSelection().toString();
    if (st != ""){
        if (nidd_cidd_regex.test(st)){
            pycmd(st);
        }
    }
});
</script>
""".replace("NIDPREFIX", gc("prefix_nid"))\
   .replace("CIDPREFIX", gc("prefix_cid"))
    web_content.head += script_str
gui_hooks.webview_will_set_content.append(append_js_to_Editor)



def js_inserter_after_load(self):
    jsstring = """

"""
    self.web.eval(jsstring)
# gui_hooks.editor_did_init.append(js_inserter_after_load)
