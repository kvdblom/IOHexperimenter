import os
import sys
import json
import shutil
import unittest
import io
from contextlib import redirect_stdout


BASE_DIR = os.path.realpath(
    os.path.join(os.path.dirname(__file__), "../../")
)
GB = globals()
LC = locals()

def iter_notebook(filename):
    with open(filename) as fp:
        nb = json.load(fp)

    for i, cell in enumerate(nb['cells'], 1):
        if cell['cell_type'] == 'code':
            source = ''.join(line for line in cell['source'] if not line.startswith('%'))
            yield i, source


class MetaTest(type):
    def __new__(cls, name, bases, dct):
        instance = super().__new__(cls, name, bases, dct)
        dirname = os.path.normpath(os.path.join(BASE_DIR, "example"))
        for f in filter(lambda x: x.endswith("ipynb"), os.listdir(dirname)):
            fname, *_ = os.path.basename(f).split(".")
            notebook =  os.path.join(dirname, f)
            def test_notebook_runner(self):
                self.assertTrue(os.path.isfile(notebook))
                for i, block in iter_notebook(notebook):
                    with io.StringIO() as buf, redirect_stdout(buf):
                        try:
                            exec(block, GB, LC)
                        except Exception as e:
                            raise RuntimeError(f"failed in cell {i}, reason:\n{e}")
            setattr(instance, f"test_notebook_{fname}", test_notebook_runner)
        return instance

class TestExamples(unittest.TestCase, metaclass=MetaTest):

    """Examples test"""
    @unittest.skipUnless(sys.version_info.minor >= 7, "python version > 3.7")
    def test_python_readme(self):
        try:
            fname = os.path.join(BASE_DIR, "ioh", "README.md")
            self.assertTrue(os.path.isfile(fname))
            with open(fname) as f:
                data = f.read().split("```")
                with io.StringIO() as buf, redirect_stdout(buf):
                    for i, x in enumerate(data):
                        if x.startswith("python"):
                            block = x[6:].strip()
                            if not 'help' in block:
                                try:
                                    exec(block, GB, LC)
                                except Exception as e:
                                    raise Exception(f"failed in cell {i}. Reasion {e}")
        except:
            raise
        finally:
            shutil.rmtree("temp", ignore_errors=True)
            shutil.rmtree("temp2", ignore_errors=True)
            shutil.rmtree("temp3", ignore_errors=True)
            shutil.rmtree("ioh_data", ignore_errors=True)
            if os.path.exists("ioh_data.zip"):
                os.remove("ioh_data.zip")
                                

if __name__ == "__main__":
    unittest.main()