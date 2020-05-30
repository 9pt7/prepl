from skbuild import setup
from setuptools import find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="pwatch",
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
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: C++",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development",
        "Topic :: System :: Filesystems",
    ],
    python_requires=">=3.6",
    use_scm_version=True,
)
