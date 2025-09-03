from setuptools import setup, find_packages

setup(
    name="automata_project",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'graphviz',
        'pythomata',
    ],
    python_requires='>=3.6',
)
