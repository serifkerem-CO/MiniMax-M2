from setuptools import setup

setup(
    name="minimax-cli",
    version="1.0.0",
    py_modules=["main"],
    install_requires=[
        "openai>=1.0.0",
        "click>=8.0.0",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "minimax=main:cli",
        ],
    },
    author="MiniMax",
    description="MiniMax-M2 CLI Tool",
    python_requires=">=3.9",
)
