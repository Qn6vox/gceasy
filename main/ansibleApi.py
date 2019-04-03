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
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.plugins.callback import CallbackBase
import ansible.constants as C

class ResultCallback(CallbackBase):
    def v2_runner_on_ok(self, result, **kwargs):
        host = result._host
        print(json.dumps({host.name: result._result}, indent=4))

class ansibleApi:
    def __init__(self, hosts):
        self.loader = DataLoader()
        self.passwords = dict(vault_pass='secret')
        self.results_callback = ResultCallback()
        Options = namedtuple('Options', ['connection', 'module_path', 'forks', 'become', 'become_method', 'become_user', 'check', 'diff', 'listhosts', 'listtasks', 'listtags', 'syntax'])
        self.options = Options(connection='ssh', module_path=['/to/mymodules'], forks=10, become=None, become_method=None, become_user=None, check=False, diff=False, listhosts=None, listtasks=None, listtags=None, syntax=None)

        if isinstance(hosts, list):
            hosts = ",".join(hosts)
        self.inventory = InventoryManager(loader=self.loader, sources=hosts + ',')
        self.variable_manager = VariableManager(loader=self.loader, inventory=self.inventory)

    def ansible(self, module, args=""):
        play_source = dict(
            name = "Ansible Play",
            hosts = 'all',
            gather_facts = 'no',
            tasks = [
                dict(action=dict(module=module, args=args), register='shell_out')
            ]
        )

        play = Play().load(play_source, variable_manager=self.variable_manager, loader=self.loader)

        tqm = None
        try:
            tqm = TaskQueueManager(
                inventory=self.inventory,
                variable_manager=self.variable_manager,
                loader=self.loader,
                options=self.options,
                passwords=self.passwords,
                stdout_callback=self.results_callback
            )
            tqm.run(play)
        finally:
            if tqm is not None:
                tqm.cleanup()

            shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)

    def playbook(self, yamlpath):
        pb = PlaybookExecutor(
            playbooks=yamlpath,
            inventory=self.inventory,
            variable_manager=self.variable_manager,
            loader=self.loader,
            options=self.options,
            passwords=self.passwords
        )
        pb.run()

if __name__ == '__main__':
    #ansibleApi(['10.5.19.1','10.5.19.2']).ansible("command", "touch /root/ansibletest")
    ansibleApi(['10.5.19.1','10.5.19.2']).playbook(["/etc/ansible/roles/agent.yml"])