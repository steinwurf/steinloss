import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="steinloss-steinwurf", # Replace with your own username
    version="0.0.1",
    author="Steinwurf ApS",
    author_email="contact@steinwurf.com",
    description="This is a tool for measuring packages loss, between two endpoint, with a web visualizer.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/steinwurf/steinloss",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
