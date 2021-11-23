from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()

setup(
    name="forge.pb",
    version="1.0.0",
    url='https://github.com/wbaker-figure/pbpm',
    author='Wyatt Baker',
    author_email='bakerwyatt19@gmail.com',
    packages=['forgepb'],
    install_requires = [requirements],
    python_requires='>=3.6',
    # scripts=['bin/forge'],
    # py_modules = ['forgepb'],
    entry_points={
        'console_scripts': [
            'forge=forgepb.forge:cli'
        ]
    },
    keyword="provenance, node, bootstrap",
    long_description=long_description,
    long_description_content_type="text/markdown",
)