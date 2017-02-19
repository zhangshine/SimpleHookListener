import json
import os
import threading

import time
from queue import Queue

from flask import Flask

app = Flask(__name__)

tasks = {}


@app.route('/deploy/<name>/', methods=['GET', 'POST'])
def run_script(name):
    try:
        config_file_path = None
        for file_path in ['/etc/hook.json', './hook.json']:
            if os.path.exists(file_path):
                config_file_path = file_path
                break

        with open(config_file_path, 'r') as f:
            hook_config = json.load(f)
            if name in hook_config and 'cmd' in hook_config[name]:
                tasks.setdefault(name, Queue()).put(hook_config[name]['cmd'])
    except Exception as e:
        print(e)
    return name


def task_consumer():
    while True:
        time.sleep(2)

        try:
            for q in tasks.values():
                if not q.empty():
                    cmd = q.get()
                    print(cmd)
                    os.system(cmd)

        except Exception as e:
            print(e)

if __name__ == '__main__':
    t = threading.Thread(target=task_consumer)
    t.daemon = True
    t.start()

    app.run(host='0.0.0.0', debug=True)
