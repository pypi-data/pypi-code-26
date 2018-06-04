from setuptools import setup, find_packages

setup(
    name="iotile_support_firm_arduino_bridge_0",
    packages=find_packages(include=["iotile_support_firm_arduino_bridge_0.*", "iotile_support_firm_arduino_bridge_0"]),
    version="0.2.0",
    install_requires=[],
    entry_points={'iotile.proxy': ['arduino_bridge_proxy = iotile_support_firm_arduino_bridge_0.arduino_bridge_proxy']},
    author="Arch",
    author_email="info@arch-iot.com"
)