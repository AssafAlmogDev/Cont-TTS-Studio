from setuptools import setup, find_packages
import os

setup(
    name="conttts",
    version="1.0.0",
    author="Assaf Almog",
    description="ContTTS Studio - An advanced Coqui TTS GUI application",
    long_description=open("README.md", encoding="utf-8").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    url="https://github.com/AssafAlmogDev/Cont-TTS-Studio",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "numpy",
        "sounddevice",
        "soundfile",
        "pydub",
        "num2words",
        "TTS",  # Coqui TTS
        "pillow",  # for image handling if used
    ],
    entry_points={
        "console_scripts": [
            "conttts=conttts.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
