# setup.py - Let's get this party started! 🎉

from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='DatabaseDiscoInferno',
    version='0.1.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=required,
    entry_points={
        'console_scripts': [
            'database-disco-inferno=database_disco_inferno:main',
        ],
    },
    author='ParisNeo',
    author_email='parisneoai@gmail.com',
    description='Boogie down with your databases! Load, search, and query like a disco king! 🕺💃',
    license='MIT',
    keywords='database disco fun',
    url='https://github.com/ParisNeo/Database-Disco-Inferno',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
