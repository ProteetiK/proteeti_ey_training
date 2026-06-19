from setuptools import setup, find_packages

setup(
    name="youtube_emotion_analyzer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "hume",
        "yt-dlp",
        "aiohttp",
    ],
)