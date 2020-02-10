from setuptools import setup, find_packages
import marccd

setup(
    name='marccd',
    version=marccd._version,
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
