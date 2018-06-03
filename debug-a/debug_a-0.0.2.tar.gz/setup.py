# -*- coding: utf-8 -*-
import debug_a
from setuptools import setup, find_packages

setup(
    name='debug_a',
    version=debug_a.__version__,
    keywords=('debug_a', 'robot', 'A股', '盯盘'),
    description="A股盯盘机器人",
    long_description="A股变化莫测，光靠一双眼睛、 四台显示器盯盘难免会有疏漏。如果能有个程序， 模拟人的盯盘动作，实时监控盘面变化， 一旦发现“异常变化”还能发送预警消息， 那就再好不过了。本项目的目标就是实现这样一个程序， 即实现A股交易时间自动盯盘， 检测到“异常情况”，实时发送通知预警。",
    license='MIT Licence',

    url="https://github.com/zengbin93/Debug_A",
    author='zengbin93',
    author_email="zeng_bin93@163.com",

    packages=find_packages(exclude=['test', 'imgs', 'doc']),
    include_package_data=True,
    install_requires=[
        'tushare',
        'retrying',
        'pandas',
        'click'
    ],
    python_requires='>=3',
    entry_points={
        'console_scripts': [
            "da = debug_a.cli:debug_a"
        ]
    }

)
