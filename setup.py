from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(name='stimage',
      version='0.1',
      description='Python program to image different parts of a setup using an XY stage controlled by stepper motors.',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/hlgirard/stimage',
      author='Henri-Louis Girard',
      author_email='hl.girard@gmail.com',
      packages=find_packages(exclude=["tests.*", "tests"]),
      install_requires=[
          'click',
          'opencv-python',
          'adafruit_motorkit',
          'adafruit_motor',
          'gpiozero',
      ],
      entry_points={
          'console_scripts': [
              'stimage = stimage:cli',
          ],
      },
      zip_safe=False,
      include_package_data=True)