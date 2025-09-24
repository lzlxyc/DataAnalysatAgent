from setuptools import setup, find_packages

setup(
    name="data_analyst_agent",
    version="0.1",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'data-analyst=data_analyst_agent.main:main',
        ],
    },
)