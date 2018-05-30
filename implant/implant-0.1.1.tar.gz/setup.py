# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['implant', 'implant.bootstrap', 'implant.commands']

package_data = \
{'': ['*'], 'implant': ['.ropeproject/*', 'testing/*']}

install_requires = \
['click', 'ruamel.yaml==0.15.37']

entry_points = \
{'console_scripts': ['implant = implant.scripts:run'],
 'pytest11': ['implant = implant.testing']}

setup_kwargs = {
    'name': 'implant',
    'version': '0.1.1',
    'description': 'Remote execution via stdin/stdout messaging.',
    'long_description': 'implant\n**********\n\n.. inclusion-marker-do-not-remove\n\n.. image:: https://travis-ci.org/diefans/implant.svg?branch=master\n   :target: https://travis-ci.org/diefans/implant\n\nA proof-of-concept for asynchronous adhoc remote procedure calls in Python.\n\nThis is work in progress and serves basically as an exercise.\n\n\nFeatures\n========\n\n- Python >= 3.5 asyncio\n\n- adhoc transferable remote procedures\n\n- remote part of a `implant.core.Command` may reside in a separate module\n\n- a `implant.core.Command` specific `implant.core.Channel`\n  enables arbitrary protocols between local and remote side\n\n- events\n\n- quite small core\n\n- tests\n\n\nLimitations\n===========\n\n- Python >= 3.5\n\n- only pure Python modules are supported for remote import, if no venv is used\n\n- `implant.core.Command` s must reside in a module other then `__main__`\n\n- at the moment sudo must not ask for password\n\n\n\nExample\n=======\n\n\nGeneral application\n-------------------\n\n.. code:: python\n\n    import asyncio\n    import pathlib\n\n    from implant import core, connect, commands\n\n\n    async def remote_tasks():\n        # create a connector for a python process\n        connector = connect.Lxd(\n            container=\'zesty\',\n            hostname=\'localhost\'\n        )\n        connector_args = {\n            \'python_bin\': pathlib.Path(\'/usr/bin/python3\')\n        }\n        # connect to a remote python process\n        remote = await connector.launch(**connector_args)\n\n        # start remote communication tasks\n        com_remote = asyncio.ensure_future(remote.communicate())\n        try:\n            # execute command\n            cmd = commands.SystemLoad()\n            result = await remote.execute(cmd)\n\n            print("Remote system load:", result)\n\n        finally:\n            # stop communication tasks\n            com_remote.cancel()\n            await com_remote\n\n\n    if __name__ == \'__main__\':\n        loop = asyncio.get_event_loop()\n        loop.run_until_complete(remote_tasks())\n        loop.close()\n\n\nAn example Echo Command\n-----------------------\n\n.. code:: python\n\n    import logging\n    import os\n\n    from implant import core\n\n\n    log = logging.getLogger(__name__)\n\n\n    class Echo(core.Command):\n\n        """Demonstrate the basic command API."""\n\n        async def local(self, context):\n            """The local side of the RPC.\n\n               :param context: :py:obj:`implant.core.DispatchLocalContext`\n            """\n            # custom protocol\n            # first: send\n            await context.channel.send_iteration("send to remote")\n\n            # second: receive\n            from_remote = []\n            async for x in context.channel:\n                from_remote.append(x)\n            log.debug("************ receiving from remote: %s", from_remote)\n\n            # third: wait for remote to finish and return result\n            remote_result = await context.remote_future\n\n            result = {\n                \'from_remote\': \'\'.join(from_remote),\n            }\n            result.update(remote_result)\n            return result\n\n        async def remote(self, context):\n            """The remote side of the RPC.\n\n               :param context: :py:obj:`implant.core.DispatchRemoteContext`\n            """\n            # first: receive\n            from_local = []\n            async for x in context.channel:\n                from_local.append(x)\n            log.debug("************ receiving from local: %s", from_local)\n\n            # second: send\n            await context.channel.send_iteration("send to local")\n\n            # third: return result\n            return {\n                \'from_local\': \'\'.join(from_local),\n                \'remote_self\': self,\n                \'pid\': os.getpid()\n            }\n\n\nInternals\n=========\n\n::\n\n    master <-----------------------------------------> remote\n                                |\n                           stdin/stdout\n                                |\n                              chunks\n                                |\n                             channels\n                                |\n        --> send ---> |                   |  --> queue -->\n                      | module:class/fqin |\n        <-- queue <-- |                   |  <--- send <--\n\n',
    'author': 'Oliver Berger',
    'author_email': 'diefans@gmail.com',
    'url': 'https://github.com/diefans/implant',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
