from skbuild import setup
from setuptools import find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()


def cmake_process_manifest_hook(file_list):
    return [file for file in file_list if file.endswith(".so")]


setup(
    name="pwatch",
    version="1.0.0",
    author="Peter Thompson",
    author_email="peter.thompson92@gmail.com",
    description="Rerun command on source change",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/9pt7/pwatch",
    packages=find_packages(),
    entry_points={"console_scripts": ["pwatch=pwatch.command_line:main"]},
    install_requires=["inotify_simple"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    cmake_process_manifest_hook=cmake_process_manifest_hook,
)
