import pdb

import ipywidgets as widgets
from IPython.display import display
from src.constants import WATCHER_PATH
import subprocess


def get_control_panel(turk,file_id):
    output = widgets.Output()

    b_listhits = widgets.Button(description='list hits')
    def listhits(b):
        df = turk.list_hits()
        display(df,output)
    b_listhits.on_click(listhits)

    b_createhits = widgets.Button(description='create hits')
    b_createhits.on_click(lambda b: turk.create_forms_hits())

    b_appcorrdry = widgets.Button(description='approve_correct (dry)')
    b_appcorrdry.on_click(lambda b:turk.approve_correct_hits(dry_run=True))
    b_appcorrdry.style.button_color = 'lightgreen'


    appcorr = widgets.Button(description='approve_correct')
    appcorr.on_click(lambda x:turk.approve_correct_hits(dry_run=False))
    appcorr.style.button_color = 'lightgreen'


    b_appall = widgets.Button(description='approve_all')
    b_appall.on_click(lambda x:turk.approve_all_hits())
    b_appall.style.button_color = 'lightgreen'

    b_allass = widgets.Button(description='list assignments')
    def f_allass(b):
        df = turk.list_all_assignments()
        display(df)
    b_allass.on_click(f_allass)

    bstop = widgets.Button(description='stop hits')
    bstop.on_click(lambda x:turk.stop_all_hits())
    bstop.style.button_color = 'orange'

    bdelete = widgets.Button(description='delete',button_style='danger')
    bdelete.on_click(lambda x:turk.delete_all_hits())

    bmonitor = widgets.Button(description='monitor',button_style='info')
    def f8(b):
        if turk.watcher_process is None:
            sub = subprocess.Popen(['python3',
                                    WATCHER_PATH,
                                    f"--id={file_id}",
                                    f"--max_forms={turk.p.max_forms_per_worker}",
                                    f"--qualifid={turk.p.qualifid}",
                                    f"--production={turk.p.production}"],
                                close_fds=True)
            print(f"Started subprocess {sub}")
            turk.watcher_process = sub
        else:
            print("Watcher already in use")
    bmonitor.on_click(f8)


    bstopmon = widgets.Button(description='stop monitor',button_style='primary')
    def stopmonitor(b):
        if turk.watcher_process is None:
            print("No monitor to stop")
        else:
            turk.watcher_process.kill()
            print(f"Killed monitor {turk.watcher_process}")
            turk.watcher_process = None
    bstopmon.on_click(stopmonitor)

    b_resform = widgets.Text( placeholder='Results HITid/formidx',
)
    def f10(sender):
        df = turk.get_results(b_resform.value)
        display(df)
    b_resform.on_submit(f10)

    display(widgets.HBox((b_listhits, b_createhits)))
    display(widgets.HBox((b_allass,b_appall)))
    display(widgets.HBox((b_appcorrdry, appcorr)))
    display(widgets.HBox((bstop, bdelete)))

    display(widgets.HBox((bmonitor, bstopmon)))
    display(b_resform)



