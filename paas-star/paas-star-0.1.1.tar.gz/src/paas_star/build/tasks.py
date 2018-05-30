import re

from os import makedirs
from os.path import join, exists
from star_builder.build.tasks import Task


class Backend(Task):
    """
    后台服务驱动
    """
    def create(self, env, **kwargs):
        task = kwargs.pop("task")
        names = kwargs.pop("name")
        driver = kwargs.pop("driver")

        for name in names:
            words = re.findall(r"([A-Za-z0-9]+)", name)
            assert words, f"name: {name} invalid!"
            assert words[0][0].isalpha(), f"name: {name} start with number!"
            makedirs(join(task, name.lower()), exist_ok=True)

            init = env.get_template(join(task, "__init__.py.tmpl"))
            fn = join(task, name, "__init__.py")
            if exists(fn) and input(f"文件{fn}已存在，是否覆盖y/n?") not in ["y", "yes"]:
                exit(0)

            with open(fn, "w") as f:
                f.write(init.render(client=name))

            client = env.get_template(join(task, "client.py.tmpl"))
            fn = join(task, name, f"{name.lower()}.py")
            if exists(fn) and input(f"文件{fn}已存在，是否覆盖y/n?") not in ["y", "yes"]:
                exit(0)

            with open(fn, "w") as f:
                assert ":" in driver, "Invalid driver module path."
                module, cls = driver.split(":", maxsplit=1)
                f.write(client.render(module=module, cls=cls, client=name))

        print("、".join(names), "后台服务驱动已完成创建。")

    @classmethod
    def enrich_parser(cls, sub_parser):
        sub_parser.add_argument("name", nargs="*", help="后台服务名称")
        sub_parser.add_argument(
            "-d", "--driver", help="后台服务驱动：如：pymongo:MongoClient")
