#!/usr/bin/env python3
"""Setup script for TeamCoherenceMonitor."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="teamcoherencemonitor",
    version="1.0.0",
    author="ATLAS (Team Brain)",
    author_email="logan@metaphy.io",
    description="Real-Time Coordination Health Dashboard for Multi-Agent Teams",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DonkRonk17/TeamCoherenceMonitor",
    py_modules=["teamcoherencemonitor"],
    python_requires=">=3.8",
    install_requires=[],  # Zero dependencies!
    extras_require={
        "dev": [
            "pytest>=7.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "teamcoherencemonitor=teamcoherencemonitor:main",
            "tcm=teamcoherencemonitor:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: System :: Monitoring",
    ],
    keywords="monitoring, coordination, multi-agent, team, coherence, dashboard",
)
