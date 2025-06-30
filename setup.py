from setuptools import setup, find_packages

setup(
    name="advanced-python-calculator",
    version="1.0.0",
    description="Advanced Python Calculator with Design Patterns",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pandas>=1.5.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pylint>=2.15.0",
        ]
    },
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "advanced-calc=calculator.main:main",
        ],
    },
)