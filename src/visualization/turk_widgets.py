import pdb

import ipywidgets as widgets
from IPython.display import display
from src.constants import WATCHER_PATH
import subprocess


def get_buttons(turk,file_id):
    output = widgets.Output()

    b1 = widgets.Button(description='list hits')
    def f1(b):
        df = turk.list_hits()
        display(df,output)
    b1.on_click(f1)

    b2 = widgets.Button(description='create forms')
    b2.on_click(lambda b: turk.create_forms_hits())
    display(widgets.HBox((b1, b2)))

    b3 = widgets.Button(description='approve_correct (dry)')
    b3.on_click(lambda b:turk.approve_correct_hits(dry_run=True))
    b3.style.button_color = 'lightgreen'


    b4 = widgets.Button(description='approve_correct')
    b4.on_click(lambda x:turk.approve_correct_hits(dry_run=False))
    b4.style.button_color = 'lightgreen'

    display(widgets.HBox((b3, b4)))

    b5 = widgets.Button(description='approve_all')
    b5.on_click(lambda x:turk.approve_all_hits())
    b5.style.button_color = 'lightgreen'

    b6 = widgets.Button(description='stop')
    b6.on_click(lambda x:turk.stop_all_hits())
    display(widgets.HBox((b5, b6)))
    b6.style.button_color = 'orange'

    b7 = widgets.Button(description='delete',button_style='danger')
    b7.on_click(lambda x:turk.delete_all_hits())

    b8 = widgets.Button(description='monitor',button_style='info')
    def f8(b):
        if turk.watcher_process is None:
            sub = subprocess.Popen(['python3', WATCHER_PATH,f"--id={file_id}"], close_fds=True)
            print(f"Started subprocess {}sub")
            turk.watcher_process = sub
        else:
            print("Watcher already in use")
    b8.on_click(f8)

    b9 = widgets.Button(description='stop monitor',button_style='primary')
    display(widgets.HBox((b7, b8)))
    def f9(b):
        if turk.watcher_process is None:
            print("No monitor to stop")
        else:
            turk.watcher_process.kill()
            print(f"Killed monitor {turk.watcher_process}")
            turk.watcher_process = None

    b9.on_click(f9)
    display(b9)

