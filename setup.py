import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wtforms_piccolo",
    version="0.1.1",
    author="sinisaos",
    author_email="sinisaos@gmail.com",
    description="Form generation utilities for Piccolo ORM Table class",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/piccolo-orm/wtforms-piccolo",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    packages=["wtforms_piccolo"],
    package_data={
        "wtforms_piccolo": ["py.typed"],
    },
    install_requires=["piccolo", "wtforms", "wtforms[email]"],
    python_requires=">=3.7",
)
