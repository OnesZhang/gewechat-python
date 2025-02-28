from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gewechat-client",
    version="0.1.5",
    author="hanfangyuan",
    author_email="i@hanfangyuan.cn",
    description="A package for interacting with the Gewechat API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hanfangyuan4396/gewechat-python",
    license='Apache-2.0',
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "Flask",
        "Flask-SocketIO",
        "requests",
        "qrcode==7.4.2"
    ],
    keywords='gewechat api client',
    include_package_data=True,
)