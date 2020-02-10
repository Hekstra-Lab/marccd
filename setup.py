from setuptools import setup, find_packages
import marccd

__version__ = 0.2

setup(
    name='marccd',
    version=__version__,
    author='Jack B. Greisman',
    author_email='greisman@g.harvard.edu',
    packages=find_packages(),
    description='Read, write, and manipulate images that use the MarCCD format',
    install_requires=[
        "numpy >= 1.6",
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-cov'],
)
