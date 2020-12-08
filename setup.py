import setuptools

from steinloss import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

REQUIREMENTS = [i.strip() for i in open("requirements.txt").readlines()]

setuptools.setup(
    name="steinloss",  # Replace with your own username
    version=__version__,
    author="Steinwurf ApS",
    author_email="contact@steinwurf.com",
    description="Package loss measuring tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/steinwurf/steinloss",
    entry_points={"console_scripts": ['steinloss=steinloss.stein_parser:cli']},
    packages=['steinloss', 'steinloss.dashboard'],
    install_requires=REQUIREMENTS,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Framework :: Dash"
    ],
    python_requires='>=3.7',
)
