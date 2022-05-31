from collections import OrderedDict
from xml.etree.ElementTree import fromstring

import attrs
import pandas as pd
import requests
import streamlit as st
from xmljson import BadgerFish


def convert_datetime(x):
    return pd.to_datetime(x)


@attrs.define
class VersionDatetime:
    project: str
    title: str = attrs.field(converter=str)
    pub_date: "Timestamp" = attrs.field(converter=convert_datetime)


def extract_rss(project: str):
    url = f"https://pypi.org/rss/project/{project}/releases.xml"
    res = requests.get(url)
    res = requests.get(url)
    content = res.content
    rss = fromstring(content.decode("utf-8"))

    return rss


def extract_releases(rss, project):
    all_releases = []
    bf = BadgerFish(dict_type=OrderedDict)
    data = bf.data(rss)
    releases = data["rss"]["channel"]["item"]
    for release in releases:
        all_releases.append(
            VersionDatetime(project, release["title"]["$"], release["pubDate"]["$"])
        )

    return all_releases


@st.cache
def main(pip_compile_file):
    projects = extract_package_from_pip_compile(pip_compile_file)
    all_releases = []
    for project in projects:

        rss = extract_rss(project)
        releases = extract_releases(rss, project)
        print(project, rss)

        all_releases += releases
    df = create_master_df(all_releases)
    return df


pip_compile_file = """
anyconfig==0.10.1
    # via kedro (setup.py)
arrow==1.2.2
    # via jinja2-time
binaryornot==0.4.4
    # via cookiecutter
"""


def extract_package_from_pip_compile(pip_compile_str):
    packages = []
    lines = pip_compile_str.split("\n")
    for line in lines:
        if "==" in line:
            packages.append(line.split("==")[0])
    return packages


def create_master_df(all_releases: list):
    df = pd.DataFrame([attrs.asdict(release) for release in all_releases])
    return df.sort_values("pub_date", ascending=False)


####### UI #######

DEFAULT = """
anyconfig==0.10.1
    # via kedro (setup.py)
arrow==1.2.2
    # via jinja2-time
binaryornot==0.4.4
    # via cookiecutter
cachetools==4.2.4
    # via kedro (setup.py)
certifi==2022.5.18.1
    # via requests
chardet==4.0.0
    # via binaryornot
charset-normalizer==2.0.12
    # via requests
click==8.1.3
    # via
    #   cookiecutter
    #   kedro (setup.py)
    #   pip-tools
commonmark==0.9.1
    # via rich
cookiecutter==1.7.3
    # via kedro (setup.py)
dynaconf==3.1.8
    # via kedro (setup.py)
fsspec==2022.1.0
    # via kedro (setup.py)
gitdb==4.0.9
    # via gitpython
gitpython==3.1.27
    # via kedro (setup.py)
idna==3.3
    # via requests
importlib-metadata==4.11.4
    # via kedro (setup.py)
jinja2==3.1.2
    # via
    #   cookiecutter
    #   jinja2-time
jinja2-time==0.2.0
    # via cookiecutter
jmespath==0.10.0
    # via kedro (setup.py)
markupsafe==2.1.1
    # via jinja2
pep517==0.12.0
    # via pip-tools
pip-tools==6.6.2
    # via kedro (setup.py)
pluggy==1.0.0
    # via kedro (setup.py)
poyo==0.5.0
    # via cookiecutter
pygments==2.12.0
    # via rich
python-dateutil==2.8.2
    # via arrow
python-json-logger==2.0.2
    # via kedro (setup.py)
python-slugify==6.1.2
    # via cookiecutter
pyyaml==6.0
    # via kedro (setup.py)
requests==2.27.1
    # via cookiecutter
rich==12.4.4
    # via kedro (setup.py)
rope==0.21.1
    # via kedro (setup.py)
six==1.16.0
    # via
    #   cookiecutter
    #   python-dateutil
smmap==5.0.0
    # via gitdb
text-unidecode==1.3
    # via python-slugify
toml==0.10.2
    # via kedro (setup.py)
tomli==2.0.1
    # via pep517
toposort==1.7
    # via kedro (setup.py)
urllib3==1.26.9
    # via requests
wheel==0.37.1
    # via pip-tools
zipp==3.8.0
    # via importlib-metadata
"""

st.title("Pypi Monitor")
pip_compile_str = st.text_area("Pip-compile file", DEFAULT)
df = main(pip_compile_str)
print("***************")
print(type(df), df)
st.write(df)
