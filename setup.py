from setuptools import setup, find_packages

setup(
    name='project0',
    version='1.0',
    author='Your Name',
    author_email='your_ufl_email@example.com',
    packages=find_packages(exclude=('tests', 'docs', 'resources')),
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)

