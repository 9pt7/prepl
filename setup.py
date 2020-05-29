from skbuild import setup
from setuptools import find_packages
import subprocess
from pathlib import Path

with open("README.md", "r") as fh:
    long_description = fh.read()


rev_commit = (
    subprocess.check_output(["git", "rev-list", "--tags", "--max-count=1"])
    .decode("utf8")
    .strip()
)
version = (
    subprocess.check_output(["git", "describe", "--tags", rev_commit])
    .decode("utf8")
    .strip()
)


def test_path(path):
    path = Path(path)
    return path.suffix == ".so" or path.name == "test_helper"


def cmake_process_manifest_hook(file_list):
    return filter(test_path, file_list)


setup(
    name="pwatch",
    version=version,
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
