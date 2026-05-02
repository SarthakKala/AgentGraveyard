from setuptools import find_packages, setup

setup(
    name="agent-graveyard",
    version="0.1.1",
    description="Self-healing failure memory for AI agents",
    packages=find_packages(),
    install_requires=["httpx>=0.27.0", "python-dotenv>=1.0.1", "pydantic>=2.7.1", "rich>=13.7.1", "websockets>=12.0"],
    entry_points={
        "console_scripts": [
            "graveyard=agentgraveyard.cli:main",
        ]
    },
)
