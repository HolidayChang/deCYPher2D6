from setuptools import setup, find_packages
import os


if not os.path.exists("install_dependencies.sh"):
    print("Error: install_dependencies.sh not found.")
else:
    print("Please run ./install_dependencies.sh to install minimap2 and k8.")

setup(
    name="deCYP2D6",
    version="1.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "decyp2d6 = deCYP2D6.decyp2d6:main",
        ],
    },
)
