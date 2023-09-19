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


@st.cache_data
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
absl-py==1.4.0
adlfs==2023.8.0
aiohttp==3.8.5
aiosignal==1.3.1
antlr4-python3-runtime==4.9.3
anyconfig==0.13.0
anyio==3.7.1
appdirs==1.4.4
argon2-cffi==23.1.0
argon2-cffi-bindings==21.2.0
arrow==1.2.3
astroid==2.15.6
asttokens==2.4.0
astunparse==1.6.3
async-timeout==4.0.3
attrs==23.1.0
aws-xray-sdk==0.95
azure-core==1.29.1
azure-datalake-store==0.0.53
azure-identity==1.14.0
azure-storage-blob==12.18.1
Babel==2.12.1
backcall==0.2.0
bandit==1.7.5
beautifulsoup4==4.12.2
behave==1.2.6
binaryornot==0.4.4
biopython==1.81
black==22.12.0
blacken-docs==1.9.2
bleach==6.0.0
blosc2==2.0.0
bokeh==3.2.2
boto==2.49.0
boto3==1.28.50
botocore==1.31.50
build==1.0.3
cachetools==5.3.1
certifi==2023.7.22
cffi==1.15.1
cfgv==3.4.0
chardet==5.2.0
charset-normalizer==3.2.0
click==8.1.7
click-plugins==1.1.1
cligj==0.7.2
cloudpickle==2.2.1
colorcet==3.0.1
comm==0.1.4
compress-pickle==2.1.0
contourpy==1.1.1
cookiecutter==2.3.0
coverage==7.3.1
cryptography==41.0.3
cycler==0.11.0
Cython==3.0.2
dask==2021.12.0
db-dtypes==1.1.1
debugpy==1.8.0
decorator==5.1.1
defusedxml==0.7.1
delta-spark==1.2.1
dill==0.3.7
distlib==0.3.7
distributed==2021.12.0
docker==6.1.3
docopt==0.6.2
dynaconf==3.2.3
ecdsa==0.18.0
entrypoints==0.4
et-xmlfile==1.1.0
exceptiongroup==1.1.3
execnet==2.0.2
executing==1.2.0
fastjsonschema==2.18.0
filelock==3.12.4
Fiona==1.9.4.post1
flatbuffers==23.5.26
frozenlist==1.4.0
fs==2.4.16
fsspec==2023.1.0
future==0.18.3
gast==0.4.0
gcsfs==2023.1.0
geopandas==0.14.0
gitdb==4.0.10
gitdb2==4.0.2
GitPython==3.0.6
google-api-core==2.11.1
google-auth==2.23.0
google-auth-oauthlib==1.0.0
google-cloud-bigquery==3.11.4
google-cloud-bigquery-storage==2.22.0
google-cloud-core==2.3.3
google-cloud-storage==2.10.0
google-crc32c==1.5.0
google-pasta==0.2.0
google-resumable-media==2.6.0
googleapis-common-protos==1.60.0
greenlet==2.0.2
grimp==3.0
grpcio==1.58.0
grpcio-status==1.58.0
h5py==3.9.0
hdfs==2.7.2
holoviews==1.17.1
identify==2.5.29
idna==3.4
import-linter==1.8.0
importlib-metadata==6.8.0
importlib-resources==6.0.1
iniconfig==2.0.0
ipykernel==6.25.2
ipython==8.15.0
ipython-genutils==0.2.0
ipywidgets==8.1.1
isodate==0.6.1
isort==5.12.0
jedi==0.19.0
Jinja2==3.0.3
jmespath==1.0.1
joblib==1.3.2
json5==0.9.14
jsondiff==1.1.1
jsonpickle==3.0.2
jsonschema==4.19.0
jsonschema-specifications==2023.7.1
jupyter==1.0.0
jupyter-console==6.6.3
jupyter-server==1.24.0
jupyter_client==7.4.9
jupyter_core==5.3.1
jupyterlab==3.5.3
jupyterlab-pygments==0.2.2
jupyterlab-widgets==3.0.9
jupyterlab_server==2.15.2
keras==2.13.1
kiwisolver==1.4.5
lazy-object-proxy==1.9.0
libclang==16.0.6
linkify-it-py==2.0.2
locket==1.0.0
lxml==4.9.3
lz4==4.3.2
Markdown==3.4.4
markdown-it-py==3.0.0
MarkupSafe==2.1.3
matplotlib==3.3.4
matplotlib-inline==0.1.6
mccabe==0.7.0
mdit-py-plugins==0.4.0
mdurl==0.1.2
memory-profiler==0.61.0
mistune==3.0.1
mock==5.1.0
more-itertools==10.1.0
moto==1.3.7
msal==1.24.0
msal-extensions==1.0.0
msgpack==1.0.5
multidict==6.0.4
mypy-extensions==1.0.0
nbclassic==1.0.0
nbclient==0.8.0
nbconvert==7.8.0
nbformat==5.9.2
nest-asyncio==1.5.8
networkx==2.8.8
nodeenv==1.8.0
notebook==6.5.5
notebook_shim==0.2.3
numexpr==2.8.6
numpy==1.24.3
oauthlib==3.2.2
omegaconf==2.3.0
opencv-python==4.5.5.64
openpyxl==3.1.2
opt-einsum==3.3.0
packaging==23.1
pandas==1.5.3
pandas-gbq==0.17.9
pandocfilters==1.5.0
panel==1.2.3
param==1.13.0
parse==1.19.1
parse-type==0.6.2
parso==0.8.3
partd==1.4.0
pathspec==0.11.2
pbr==5.11.1
pexpect==4.8.0
pickleshare==0.7.5
Pillow==9.5.0
pip-tools==7.3.0
platformdirs==3.10.0
plotly==5.17.0
pluggy==1.2.0
portalocker==2.8.2
pre-commit==2.21.0
prometheus-client==0.17.1
prompt-toolkit==3.0.39
proto-plus==1.22.3
protobuf==4.24.3
psutil==5.9.5
ptyprocess==0.7.0
pure-eval==0.2.2
py==1.11.0
py-cpuinfo==9.0.0
py4j==0.10.9.5
pyaml==23.9.6
pyarrow==9.0.0
pyasn1==0.5.0
pyasn1-modules==0.3.0
pycparser==2.21
pycryptodome==3.19.0
pyct==0.5.0
pydata-google-auth==1.8.2
Pygments==2.16.1
PyJWT==2.8.0
pylint==2.17.5
pyparsing==3.1.1
pyproj==3.6.0
pyproject_hooks==1.0.0
pyspark==3.2.4
pytest==7.4.2
pytest-cov==3.0.0
pytest-forked==1.6.0
pytest-mock==1.13.0
pytest-xdist==2.2.1
python-dateutil==2.8.2
python-jose==2.0.2
python-slugify==8.0.1
pytoolconfig==1.2.5
pytz==2023.3.post1
pyviz_comms==3.0.0
PyYAML==6.0.1
pyzmq==24.0.1
qtconsole==5.4.4
QtPy==2.4.0
redis==4.6.0
referencing==0.30.2
requests==2.31.0
requests-mock==1.11.0
requests-oauthlib==1.3.1
responses==0.23.3
rich==13.5.3
rope==1.9.0
rpds-py==0.10.3
rsa==4.9
s3fs==0.4.2
s3transfer==0.6.2
scikit-learn==1.3.0
scipy==1.11.2
semver==3.0.1
Send2Trash==1.8.2
shapely==2.0.1
six==1.16.0
smmap==5.0.1
sniffio==1.3.0
sortedcontainers==2.4.0
soupsieve==2.5
SQLAlchemy==1.4.49
stack-data==0.6.2
stevedore==5.1.0
tables==3.8.0
tblib==2.0.0
tenacity==8.2.3
tensorboard==2.13.0
tensorboard-data-server==0.7.1
tensorflow==2.13.0
tensorflow-estimator==2.13.0
tensorflow-io-gcs-filesystem==0.34.0
termcolor==2.3.0
terminado==0.17.1
text-unidecode==1.3
threadpoolctl==3.2.0
tinycss2==1.2.1
toml==0.10.2
tomli==2.0.1
tomlkit==0.12.1
toolz==0.12.0
toposort==1.10
tornado==6.3.3
tqdm==4.66.1
traitlets==5.10.0
triad==0.9.1
truffleHog==2.2.1
truffleHogRegexes==0.0.7
types-PyYAML==6.0.12.11
typing_extensions==4.5.0
uc-micro-py==1.0.2
urllib3==1.26.16
virtualenv==20.24.5
wcwidth==0.2.6
webencodings==0.5.1
websocket-client==1.6.3
Werkzeug==2.3.7
widgetsnbextension==4.0.9
wrapt==1.15.0
XlsxWriter==1.4.5
xmltodict==0.13.0
xyzservices==2023.7.0
yarl==1.9.2
zict==3.0.0
zipp==3.17.0
"""

st.image("demo-light.png")
st.title("PyPi Monitor - Tracking the latest release of your libraries")

pip_compile_str = st.text_area("Pip freeze file (default with [Kedro](https://github.com/kedro-org/kedro)'s dependencies)", DEFAULT)
df = main(pip_compile_str)

@st.cache_data
def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')


csv = convert_df(df)

st.download_button(
   "Press to Download",
   csv,
   "dependencies.csv",
   "text/csv",
   key='download-csv'
)
print("***************")
print(type(df), df)
st.write(df)
