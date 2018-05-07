from setuptools import setup

setup(
    name="sendxml",
    version="0.0.1",
    author="Anthony DeDominic",
    author_email="adedomin@gmail.com",
    description="atom feed server",
    license="ISC",
    keywords="atom feed sendmail",
    url="https://github.com/adedomin/sendxml",
    packages=['flask', 'feedgen'],
    classifiers=[
        "License :: OSI Approved :: ISC License",
    ],
)
