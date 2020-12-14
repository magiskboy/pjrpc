from setuptools import setup


setup(
    name='pjrpc',
    version='0.0.1',
    author='Nguyen Khac Thanh',
    install_requires=[
        'Click',
    ],
    entry_points='''
    [console_scripts]
    pj=pjrpc.cli:cli
    ''',
    packages=['pjrpc',],
)
