from setuptools import setup, find_packages

setup(
    name="librocco.bookdata",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "ibmcloudant",
        "click",
        "tqdm",
    ],
    extras_require={
        "test": ["pytest", "docker"],
    },
    author="Silvio Tomatis",
    author_email="silvio@codemyriad.io",
    description="Parse a book data CSV file and feed it to a librocco database.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://libroc.co",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
