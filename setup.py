import os
from setuptools import setup, find_packages


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

README = open(os.path.join(SCRIPT_DIR, "README.md")).read()


setup_dict = dict(
    name="computer-tennis",
    version="0.1.0",
    description="Virtual tennis reinforcement learning environment",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/christopher-hesse/computer-tennis",
    author="Christopher Hesse",
    license="Public Domain",
    packages=find_packages(),
    install_requires=[
        "moderngl>=5.6.0,<6.0.0",
        "gym3>=0.3.1,<0.4.0",
        "glcontext==2.3.dev0",
    ],
    extras_require={
        "dev": ["pytest", "pytest-benchmark"],
        # pycairo cannot be a dependency because it often fails to install
        # as it is lacking binary wheels
        "cairo": ["pycairo>=1.19.0,<2.0.0"],
    },
    python_requires=">=3.7.0",
)

setup(**setup_dict)
