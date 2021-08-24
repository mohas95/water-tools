import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="RPi-water-tools",
    keywords = 'Raspberry Pi, Raspi, Python, GPIO, API, non-blocking, ph, temperature, DFRobot, water, monitoring',
    version="0.1.5",
    author="Mohamed Debbagh",
    author_email="moha7108@protonmail.com",
    description="This package provides various water monitoring tools for sensor and pump integration. This package uses the RPI-Control-center gpio engine as its driver to make RPI api-ification easy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/moha7108/water-tools",
    project_urls={
        "Bug Tracker": "https://github.com/moha7108/water-tools/issues",
        "Github": "https://github.com/moha7108/water-tools"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Development Status :: 3 - Alpha",
    ],
    license='GNU GPLv3',
    packages=['water_tools'],
    python_requires=">=3",
    install_requires=[
          'logzero',
          'DFRobot-EC-PH-ADC',
          'RPI-control-center'
      ]
)
