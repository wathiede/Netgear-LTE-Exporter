from setuptools import setup, find_packages

setup(
    name='Netgear-LTE-Exporter',
    version='0.0.1',
    url='https://github.com/wathiede/Netgear-LTE-Exporter',
    author='Bill Thiede',
    author_email='git@xinu.tv',
    description='Netgear LTE Modem Exporter',
    py_modules=['main.py'],
    install_requires=['prometheus_client', 'eternalegypt', 'python-dotenv'],
    entry_points={  # Optional
        "console_scripts": [
            "netgear-lte-exporter=netgear-lte-exporter:main",
        ],
    },
)
