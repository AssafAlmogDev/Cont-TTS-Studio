from setuptools import setup, find_packages

setup(
    name='conttts',
    version='1.0.0',
    author='Your Name',
    description='A GUI + CLI for ContTTS',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'conttts=conttts.cli:main',
        ],
    },
    install_requires=[
        # Add your dependencies here if any
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)
