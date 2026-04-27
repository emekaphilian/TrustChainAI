from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="trustchainai",
    version="0.1.0",
    author="Your Name",
    description="AI-Powered Smart Contract Auditor with Bias & Ethics Dashboard",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/trustchainai",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Security",
    ],
    python_requires=">=3.10",
    install_requires=[
        "torch>=2.0.0",
        "transformers>=4.30.0",
        "web3>=6.0.0",
        "streamlit>=1.25.0",
        "shap>=0.42.0",
        "lime>=0.2.0",
        "scikit-learn>=1.3.0",
    ],
)
