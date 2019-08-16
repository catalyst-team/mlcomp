import os
from os.path import join
import shutil

from .__version__ import __version__  # noqa: F401

ROOT_FOLDER = os.getenv('ROOT_FOLDER', os.path.expanduser('~/mlcomp'))
DATA_FOLDER = join(ROOT_FOLDER, 'data')
MODEL_FOLDER = join(ROOT_FOLDER, 'models')
TASK_FOLDER = join(ROOT_FOLDER, 'tasks')
LOG_FOLDER = join(ROOT_FOLDER, 'logs')
CONFIG_FOLDER = join(ROOT_FOLDER, 'configs')
DB_FOLDER = join(ROOT_FOLDER, 'db')

os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(MODEL_FOLDER, exist_ok=True)
os.makedirs(TASK_FOLDER, exist_ok=True)
os.makedirs(LOG_FOLDER, exist_ok=True)
os.makedirs(CONFIG_FOLDER, exist_ok=True)
os.makedirs(DB_FOLDER, exist_ok=True)

# copy conf files if they do not exist

folder = os.path.dirname(__file__)
docker_folder = join(folder, 'docker')

for name in os.listdir(docker_folder):
    file = join(docker_folder, name)
    target_file = join(CONFIG_FOLDER, name)
    if not os.path.exists(target_file):
        shutil.copy(file, target_file)

# exporting environment variables
with open(join(CONFIG_FOLDER, '.env')) as f:
    for l in f.readlines():
        k, v = l.strip().split('=')
        os.environ[k] = v

# for debugging
os.environ['PYTHONPATH'] = '.'

MASTER_PORT_RANGE = list(map(int, os.getenv('MASTER_PORT_RANGE').split('-')))
MODE_ECONOMIC = os.getenv('MODE_ECONOMIC') == 'True'

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
REDIS_PORT = os.getenv('REDIS_PORT')

TOKEN = os.getenv('TOKEN')
DOCKER_IMG = os.getenv('DOCKER_IMG', 'default')
WEB_HOST = os.getenv('WEB_HOST')
WEB_PORT = int(os.getenv('WEB_PORT'))
WORKER_INDEX = os.getenv('WORKER_INDEX', -1)

CONSOLE_LOG_LEVEL = os.getenv('CONSOLE_LOG_LEVEL', 'DEBUG')
DB_LOG_LEVEL = os.getenv('DB_LOG_LEVEL', 'DEBUG')
FILE_LOG_LEVEL = os.getenv('FILE_LOG_LEVEL', 'INFO')

DB_TYPE = os.getenv('DB_TYPE')
if DB_TYPE == 'POSTGRESQL':
    DATABASE = {
        'dbname': os.getenv('POSTGRES_DB'),
        'user': os.getenv('POSTGRES_USER'),
        'password': os.getenv('POSTGRES_PASSWORD'),
        'host': os.getenv('POSTGRES_HOST'),
        'port': int(os.getenv('POSTGRES_PORT')),
    }

    SA_CONNECTION_STRING = f"postgresql+psycopg2://{DATABASE['user']}:" \
                           f"{DATABASE['password']}@{DATABASE['host']}:" \
                           f"{DATABASE['port']}/{DATABASE['dbname']}"
elif DB_TYPE == 'SQLITE':
    SA_CONNECTION_STRING = f'sqlite:///{DB_FOLDER}/sqlite3.sqlite'
else:
    raise Exception(f'Unknown DB_TYPE = {DB_TYPE}')

FLASK_ENV = os.getenv('FLASK_ENV')
DOCKER_MAIN = os.getenv('DOCKER_MAIN', 'True') == 'True'

IP = os.getenv('IP')
PORT = int(os.getenv('PORT'))

__all__ = [
    'ROOT_FOLDER', 'DATA_FOLDER', 'MODEL_FOLDER', 'TASK_FOLDER', 'LOG_FOLDER',
    'CONFIG_FOLDER', 'DB_FOLDER', 'MASTER_PORT_RANGE', 'REDIS_HOST',
    'REDIS_PASSWORD', 'REDIS_PORT', 'TOKEN', 'DOCKER_IMG', 'WEB_HOST',
    'WEB_PORT', 'WORKER_INDEX', 'CONSOLE_LOG_LEVEL', 'DB_LOG_LEVEL',
    'FILE_LOG_LEVEL', 'DB_TYPE', 'SA_CONNECTION_STRING', 'FLASK_ENV',
    'DOCKER_MAIN', 'IP', 'PORT', 'MODE_ECONOMIC'
]
