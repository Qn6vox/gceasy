#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import json
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.plugins.callback import CallbackBase
from ansible.errors import AnsibleParserError

class ResultCallback(CallbackBase):
    def __init__(self, * args, **kwargs):
        super(ResultCallback, self).__init__(* args, **kwargs)
        self.host_ok = {}
        self.host_unreachable = {}
        self.host_failed = {}

    def v2_runner_on_ok(self, result, * args, **kwargs):
        self.host_ok[result._host.get_name()] = result

    def v2_runner_on_failed(self, result, *args, **kwargs):
        self.host_failed[result._host.get_name()] = result

    def v2_runner_on_unreachable(self, result):
        self.host_unreachable[result._host.get_name()] = result

class ansibleApi:
    def __init__(self, hosts):
        self.loader = DataLoader()
        self.passwords = dict(vault_pass='secret')
        self.callback = ResultCallback()
        Options = namedtuple('Options',
                             ['connection',
                              'module_path',
                              'forks',
                              'become',
                              'become_method',
                              'become_user',
                              'check',
                              'diff',
                              'listhosts',
                              'listtasks',
                              'listtags',
                              'syntax'])
        self.options = Options(connection='ssh',
                               module_path=['/to/mymodules'],
                               forks=10,
                               become=None,
                               become_method=None,
                               become_user=None,
                               check=False,
                               diff=False,
                               listhosts=None,
                               listtasks=None,
                               listtags=None,
                               syntax=None)

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
                stdout_callback=self.callback
            )
            tqm.run(play)
            status = True
            msg = "Ansible play success."
        except AnsibleParserError:
            status = False
            msg = "Ansible play failed."
        finally:
            if tqm is not None:
                tqm.cleanup()

        results_raw = {'success': {}, 'failed': {}, 'unreachable': {}}

        for host, result in self.callback.host_ok.items():
            results_raw['success'][host] = result._result

        for host, result in self.callback.host_failed.items():
            results_raw['failed'][host] = result._result['msg']

        for host, result in self.callback.host_unreachable.items():
            results_raw['unreachable'][host] = result._result['msg']

        print json.dumps(results_raw, indent=4)
        return status, msg, results_raw

    def playbook(self, yamlpath):
        self.variable_manager.extra_vars = {'customer': 'test', 'disabled': 'yes'}
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
    #ansibleApi(['10.5.19.1','10.5.19.2']).ansible("file", "path=/root/ansibletest state=touch")
    ansibleApi(['10.5.19.1','10.5.19.2']).playbook(["/etc/ansible/roles/test.yml"])