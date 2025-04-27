from setuptools import setup, find_packages

setup(
    name="qntropy",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "typer",
        "rich",
        "pydantic",
    ],
    python_requires=">=3.11",
    entry_points={
        "console_scripts": [
            "qntropy=qntropy.cli.main:app",
        ],
    },
)
