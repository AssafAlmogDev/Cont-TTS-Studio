from setuptools import setup, find_packages

setup(
    name='conttts',
    version='1.0.0',
    author='Assaf Almog',
    description='ContTTS: A GUI and CLI for TTS',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'conttts=conttts.cli:main',
        ],
    },
    install_requires=[],
    python_requires='>=3.6',
)
