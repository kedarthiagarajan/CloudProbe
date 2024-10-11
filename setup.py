from setuptools import setup, find_packages

setup(
    name="cloudprobe",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "paramiko",
        
        # other dependencies...
    ],
    entry_points={
        "console_scripts": [
            "cloudprobe=cloudprobe.deploy:main",  # This will create a `cloudprobe` command
        ],
    },
)
