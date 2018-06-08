import sys
import subprocess
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from textwrap import dedent

import pybake
from pybake import PyBake


def run_code(cwd, code):
    args = [sys.executable, '-c', code]
    p = subprocess.Popen(args=args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    return p.returncode, p.stdout.read().decode('utf-8'), p.stderr.read().decode('utf-8')


def test_foo_as_module(tmpdir):
    header = '# HEADER'
    footer = '# FOOTER'
    width = 50
    pb = PyBake(header, footer, width=width, suffix='#|', python='python2')

    import tests.foo
    pb.add_module(tests.foo)

    pb.add_module(pybake, ('sub',))

    text = StringIO('Hello world!')
    pb.add_file(('res', 'msg.txt'), text)

    path = str(tmpdir.join('foobake.py'))
    pb.write_dist(path)

    with open(path, 'rt') as fh:
        bake_content_lines = fh.read().splitlines()

    assert len(bake_content_lines[1]) == width
    assert header in bake_content_lines[1]

    assert len(bake_content_lines[-2]) == width
    assert footer in bake_content_lines[-2]

    assert len(bake_content_lines[-1]) == width

    # Test dir() on module
    _, stdout, stderr = run_code(tmpdir.strpath,
        r"import foobake; print('\n'.join(sorted(dir(foobake))))")

    print(stderr)
    found = stdout.splitlines()
    expected = ('__builtins__', '__doc__', '__file__', '__name__', '__package__')
    for item in expected:
        assert item in found

    # Test module __file__
    _, stdout, _ = run_code(tmpdir.strpath,
        r"import foobake, os; print(foobake.__file__)")

    assert stdout.rstrip().endswith('foobake.pyc')

    # Test listdir() on blob file system
    _, stdout, _ = run_code(tmpdir.strpath,
        r"import foobake, os; print('\n'.join(sorted(os.listdir(os.path.join(foobake.__file__, 'sub/pybake')))))")

    found = stdout.splitlines()
    expected = (
        '__init__.py',
        'abstractimporter.py',
        'blobserver.py',
        'dictfilesystem.py',
        'dictfilesystembuilder.py',
        'dictfilesysteminterceptor.py',
        'dictimporter.py',
        'filesysteminterceptor.py',
        'launcher.py',
        'moduletree.py',
        'pybake.py',
        'six.py',
    )
    for item in expected:
        assert item in found

    # Test open() on blob file system
    _, stdout, _ = run_code(tmpdir.strpath,
        "import foobake, os; print open(os.path.join(foobake.__file__, 'res/msg.txt')).read()")

    assert stdout == 'Hello world!\n'


    # Test importing and inspection on blob file system
    _, stdout, _ = run_code(tmpdir.strpath,
        "import foobake; from tests.foo import Foo; f = Foo(); print(f.file()); print(f.src())")

    assert stdout.splitlines() == [
        'foobake.pyc/tests/foo/foo.py',
        'foobake.pyc/tests/foo/foo.py'
    ]

    # Test exception tracebacks on blob files system
    _, _, stderr = run_code(tmpdir.strpath,
        "import foobake; from tests.foo import Foo; f = Foo(); f.bang()")

    assert stderr == dedent('''\
        Traceback (most recent call last):
          File "<string>", line 1, in <module>
          File "foobake.pyc/tests/foo/foo.py", line 16, in bang
          File "foobake.pyc/tests/foo/foo.py", line 19, in _bang
        ValueError: from Foo
        ''')


    _, _, stderr = run_code(tmpdir.strpath,
                            "import foobake; import tests.foo.bad")

    print(stderr)
    assert stderr == dedent('''\
        Traceback (most recent call last):
          File "<string>", line 1, in <module>
          File "foobake.pyc/pybake/abstractimporter.py", line 93, in load_module
          File "foobake.pyc/pybake/abstractimporter.py", line 83, in load_module
        ImportError: SyntaxError: invalid syntax (bad.py, line 2), while importing 'tests.foo.bad'
        ''')

