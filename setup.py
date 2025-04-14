
from setuptools import setup, find_packages

setup(
    name="capstone",
    version="0.1",
    package_dir={"": "src_v3"},
    packages=find_packages(where='src_v3'),
    install_requires=[
        "langchain-aws",
        "boto3",
        "python-dotenv",
	"pytest",
    ],
)
