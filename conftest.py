import pathlib

ROOT = pathlib.Path(__file__).parent
PATH = ROOT / "serialize" / "testsuite"
GENERATED_PATH = PATH / "generated"
TEST_README = GENERATED_PATH / "test_readme.py"
README = ROOT / "README.md"


def setup_test_readme():
    GENERATED_PATH.mkdir(exist_ok=True)

    INDENT = " " * 4
    with TEST_README.open("w") as out, README.open("r") as readme:
        mode = None
        output = []

        output.append("def test_all():\n")
        for i, line in enumerate(readme.readlines()):
            output.append("\n")
            if mode is None and line.strip() == "```python":
                mode = "first_line"
                output[i] = INDENT + "# line %04d" % i
                # output[i] = 'def test_line_%04d():\n' % i
                continue
            elif line.strip() == "```":
                continue
            elif mode == "first_line":
                if line.strip() == "":
                    mode = None
                    output[i - 1] = "\n"
                    continue
                if line.strip().startswith(">>>"):
                    mode = "doctest"
                    output[i - 2] = (
                        output[i - 1][:-1] + "  " + output[i - 2]
                    )  # move the def line one line up
                    output[i - 1] = '    """\n'
                else:
                    mode = "test"
            if mode in ("doctest", "test"):
                output[i] = "    " + line
            else:
                pass
                # output[i] = '# %s' % line

        output.append(INDENT + '"""\n')
        out.writelines(output)


def pytest_sessionstart(session):
    try:
        setup_test_readme()
    except ImportError:
        pass


def rm_tree(pth):
    for child in pth.glob("*"):
        if child.is_file():
            child.unlink()
        else:
            rm_tree(child)
    pth.rmdir()


def pytest_sessionfinish(session, exitstatus):
    try:
        rm_tree(GENERATED_PATH)
        pass
    except FileNotFoundError:
        pass
