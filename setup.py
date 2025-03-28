from setuptools import setup, find_packages

setup(
    name="quicpro",
    version="1.0.0",
    description="A synchronous HTTP/3 client library built on QUIC, UDP, and TLS-like encryption without asyncio.",
    author="Jochen Schultz",
    author_email="js@intelligent-intern.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "cryptography"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)