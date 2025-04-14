# setup.py

from setuptools import setup, find_packages
import os

# Read the README file for a long description
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="performance_watch",
    version="0.1.0",
    author="Ihor Haivan",
    author_email="ihor.haivan@gmail.com",
    license="MIT",
    description="A monitoring tool for performance pages that detects free seats and sends notifications.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/performance_watch",
    packages=find_packages(),  # Automatically finds packages within the project
    install_requires=[
        "playwright",
        "requests",
        # Include any other dependencies required by your project.
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Update license if necessary
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',  # Specify the minimum Python version required
)
