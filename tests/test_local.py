###############################################################
# pytest -v --capture=no tests/test_local.py
# pytest -v  tests/test_local.py
# pytest -v --capture=no -v --nocapture tests/test_local.py:Test_local.<METHIDNAME>
###############################################################
import os
from pprint import pprint

from cloudmesh.storage.Provider import Provider
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import path_expand
from pathlib import Path
from cloudmesh.common.util import writefile
from cloudmesh.variables import Variables
from cloudmesh.common.util import banner
from cloudmesh.common.parameter import Parameter
from cloudmesh.DEBUG import VERBOSE


import pytest


def create_file(location, content):
    d = Path(os.path.dirname(path_expand(location)))
    print()
    print("TESTDIR:", d)

    d.mkdir(parents=True, exist_ok=True)

    writefile(path_expand(location), content)

@pytest.mark.incremental
class Test_local:


    def setup_class(self):
        #variables = Variables()
        #service = Parameter.expand(variables['storage'])[0]

        self.service = "local"
        self.p = Provider(service=self.service)


    def test_00__config(self):

        VERBOSE(self.p)
        VERBOSE(self.p.kind)
        assert self.p.kind == self.service

    def test_01_create_source(self):
        HEADING()


        self.sourcedir = path_expand("~/.cloudmesh/storage/test/")
        create_file("~/.cloudmesh/storage/README.md", "content of a")
        create_file("~/.cloudmesh/storage/test/a/a.txt", "content of a")
        create_file("~/.cloudmesh/storage/test/a/b/b.txt", "content of b")
        create_file("~/.cloudmesh/storage/test/a/b/c/c.txt", "content of c")

        # test if the files are ok
        assert True

    def test_02_list(self):
        HEADING()
        src = '/'
        contents = self.p.list(source=src)

        VERBOSE(contents,label="c")

        for c in contents:
            VERBOSE(c)

    def test_05_search(self):
        HEADING()
        src = '/'
        filename = 'a.txt'
        #
        # bug use named arguments
        #
        files = self.p.search(directory=src, filename=filename, recursive=True)
        pprint(files)

        assert len(files) > 0


class a:

    def test_02_put(self):
        HEADING()
        src = path_expand("~/.cloudmesh/storage/test/a/a.txt")
        dst = "/"
        test_file = self.p.put(src, dst)
        pprint(test_file)

        assert test_file is not None

    def test_03_get(self):
        HEADING()
        src = path_expand("/a.txt")
        dst = path_expand("~/test.txt")
        file = self.p.get(src, dst)
        pprint(file)

        assert file is not None


        assert len(contents) > 0


    def test_06_create_dir(self):
        HEADING()
        src = '/created_dir'
        dir = self.p.create_dir(src)
        pprint(dir)

        assert dir is not None

    def test_07_delete(self):
        HEADING()
        src = '/created_dir'
        self.p.delete(src)



















