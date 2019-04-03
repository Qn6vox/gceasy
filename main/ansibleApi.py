#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import json
import shutil
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase
import ansible.constants as C

class ResultCallback(CallbackBase):
    def v2_runner_on_ok(self, result, **kwargs):
        host = result._host
        print(json.dumps({host.name: result._result}, indent=4))

def ansibleApi(hosts, module, args=""):
    Options = namedtuple('Options', ['connection', 'module_path', 'forks', 'become', 'become_method', 'become_user', 'check', 'diff'])
    options = Options(connection='ssh', module_path=['/to/mymodules'], forks=10, become=None, become_method=None, become_user=None, check=False, diff=False)

    loader = DataLoader()
    passwords = dict(vault_pass='secret')
    results_callback = ResultCallback()

    if isinstance(hosts,list):
        hosts = ",".join(hosts)
    inventory = InventoryManager(loader=loader, sources=hosts + ',')
    variable_manager = VariableManager(loader=loader, inventory=inventory)

    play_source =  dict(
        name = "Ansible Play",
        hosts = 'all',
        gather_facts = 'no',
        tasks = [
            dict(action=dict(module=module, args=args), register='shell_out')
        ]
    )

    play = Play().load(play_source, variable_manager=variable_manager, loader=loader)

    tqm = None
    try:
        tqm = TaskQueueManager(
            inventory=inventory,
            variable_manager=variable_manager,
            loader=loader,
            options=options,
            passwords=passwords,
            stdout_callback=results_callback,
        )
        tqm.run(play)
    finally:
        if tqm is not None:
            tqm.cleanup()

        shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)

if __name__ == '__main__':
    ansibleApi(['10.5.19.1','10.5.19.2'], "command", "touch /root/ansibletest")