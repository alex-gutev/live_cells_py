import setuptools

# Load the long_description from README.md
with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='live-cells-py',
    version='0.1.4',
    author='Alexander Gutev',
    author_email='alex.gutev@gmail.com',
    description="A reactive programming library for Python ported from Live Cells for Dart",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alex-gutev/live_cells_py",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
