from setuptools import setup, find_packages

setup(
    name='marccd',
    version='0.0.1',
    author='Jack B. Greisman',
    author_email='greisman@g.harvard.edu',
    packages=find_packages(),
    description='Read, write, and manipulate images that use the MarCCD format',
    install_requires=[
        "numpy >= 1.6",
    ],
)