from setuptools import setup


description = "Build single file Python scripts with builtin frozen file system"

setup(
    name="pybake",
    version="0.0.2",
    description=description,
    long_description=description,  # TODO: https://docs.python.org/2/distutils/packageindex.html#pypi-package-display
    author="Source Simian",
    author_email="sourcesimian@users.noreply.github.com",
    url='https://github.com/sourcesimian/pyBake',
    license='MIT',
    packages=['pybake'],
)
