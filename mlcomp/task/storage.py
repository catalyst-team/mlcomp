from glob import glob
import os
import logging
from os.path import isdir
import hashlib
from typing import List, Tuple

from sqlalchemy.orm import joinedload

from mlcomp.db.models import *
from mlcomp.db.providers import FileProvider, DagStorageProvider, TaskProvider, DagLibraryProvider
import pkgutil
import inspect
from mlcomp.utils.config import Config
import sys
import pathspec
from mlcomp.utils.req import control_requirements, read_lines
from importlib import reload
import site
from types import ModuleType
import pkg_resources

from task.executors import Executor

logger = logging.getLogger(__name__)


class Storage:
    def __init__(self):
        self.file_provider = FileProvider()
        self.provider = DagStorageProvider()
        self.task_provider = TaskProvider()
        self.library_provider = DagLibraryProvider()

    def upload(self, folder: str, dag: Dag):
        hashs = self.file_provider.hashs(dag.project)
        ignore_file = os.path.join(folder, 'file.ignore.txt')
        if not os.path.exists(ignore_file):
            with open(ignore_file, 'w') as f:
                f.write('')

        ignore_patterns = read_lines(ignore_file)
        ignore_patterns.extend(['log', 'data', '__pycache__'])

        files = []
        spec = pathspec.PathSpec.from_lines(pathspec.patterns.GitWildMatchPattern, ignore_patterns)

        for o in glob(os.path.join(folder, '**'), recursive=True):
            path = os.path.relpath(o, folder)
            if spec.match_file(path) or path == '.':
                continue

            if isdir(o):
                self.provider.add(DagStorage(dag=dag.id, path=path, is_dir=True))
                continue
            content = open(o, 'rb').read()
            md5 = hashlib.md5(content).hexdigest()
            if md5 in hashs:
                file_id = hashs[md5]
            else:
                file = File(md5=md5, content=content, project=dag.project, dag=dag.id)
                self.file_provider.add(file)
                file_id = file.id
                hashs[md5] = file.id
                files.append(o)

            self.provider.add(DagStorage(dag=dag.id, path=path, file=file_id, is_dir=False))

        reqs = control_requirements(folder, files=files)
        for name, rel, version in reqs:
            self.library_provider.add(DagLibrary(dag=dag.id, library=name, version=version))

    def download(self, task: int):
        task = self.task_provider.by_id(task, joinedload(Task.dag_rel))
        folder = f'/tmp/mlcomp/{task.id}'
        os.makedirs(folder, exist_ok=True)
        items = self.provider.by_dag(task.dag)
        items = sorted(items, key=lambda x: x[1] is not None)
        for item, file in items:
            path = os.path.join(folder, item.path)
            if item.is_dir:
                os.makedirs(path, exist_ok=True)
            else:
                with open(path, 'wb') as f:
                    f.write(file.content)

        config = Config.from_yaml(task.dag_rel.config)
        info = config['info']
        if 'data_folder' in info:
            try:
                os.symlink(info['data_folder'], os.path.join(folder, 'data'))
            except FileExistsError:
                pass

        sys.path.insert(0, folder)
        return folder

    def import_folder(self, folder: str, executor: str, libraries: List[Tuple]):
        folders = [p for p in glob(f'{folder}/*', recursive=True) if os.path.isdir(p) and not '__pycache__' in p]
        folders += [folder]
        packages_folder = site.getsitepackages()[0]
        library_names = set(n for n, v in libraries)
        library_versions = {n: v for n, v in libraries}

        for n in library_names:
            try:
                version = pkg_resources.get_distribution(n).version
                need_install = library_versions[n]!=version
            except Exception:
                need_install = True

            if need_install:
                os.system(f'pip install {n}=={library_versions[n]}')

        for (module_loader, module_name, ispkg) in pkgutil.iter_modules(folders):
            module = module_loader.find_module(module_name).load_module(module_name)
            reload(module)

            for v in module.__dict__.values():
                if isinstance(v, ModuleType):
                    import_path = os.path.relpath(v.__file__, packages_folder)
                    import_name = import_path.split(os.path.sep)[0]
                    if import_name in library_names:
                        reload(v)

            reload(module)

        assert Executor.is_registered(executor), f'Executor {executor} was not found'

if __name__ == '__main__':
    storage = Storage()
    storage.download(77)
