#!/usr/bin/env python

from setuptools import setup, find_packages

import codecs
import os.path


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as fp:
        return fp.read()


def get_parameter(name="PROJECT_NAME"):
    with open("config.mk") as fp:
        for line in fp:
            fline = line[:-1].split("=")
            if len(fline) == 2 and name == fline[0]:
                return fline[1]


def get_version():
    for line in read(f"{get_parameter()}/__init__.py").splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


def get_console_scripts():
    scripts = []
    with open("config.mk") as fp:
        for line in fp:
            fline = line[:-1].split("=")
            if len(fline) == 2 and "SCRIPT:" in fline[0]:
                scripts.append(line[7:-1])
    return scripts


setup(
    # Package info
    name=get_parameter(),
    version=get_version(),
    packages=find_packages(),
    author="guydegnol",
    # Dependencies
    install_requires=["pandas"],
    # Script info
    entry_points={"console_scripts": get_console_scripts()},
)
