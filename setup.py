from skbuild import setup
from setuptools import find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="prepl",
    author="Peter Thompson",
    author_email="peter.thompson92@gmail.com",
    description="Rerun command on source change",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/9pt7/prepl",
    packages=find_packages(),
    entry_points={"console_scripts": ["prepl=prepl.command_line:main"]},
    install_requires=["inotify_simple"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development",
        "Topic :: System :: Filesystems",
    ],
    python_requires=">=3.6",
    extras_require={
        "dev": [
            "setuptools>=42",
            "setuptools_scm[toml]",
            "scikit-build",
            "wheel",
            "cmake",
            "ninja",
            "tox",
            "pytest",
            "flake8",
            "twine",
        ]
    },
    use_scm_version=True,
)
