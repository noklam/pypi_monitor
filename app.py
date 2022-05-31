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
    title: str
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
    print(df)
    return df.sort_values("pub_date", ascending=False)


####### UI #######
st.title("Pypi Monitor")
pip_compile_str = st.text_area("Pip-compile file")
df = main(pip_compile_str)
st.write(df)
