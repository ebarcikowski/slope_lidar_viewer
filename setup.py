from setuptools import setup


setup(
    name="lidar_viewer",
    version="0.1",
    packages=['viewer'],
    entry_points={'console_scripts': ['viewer=viewer.master_main.main']}
)
