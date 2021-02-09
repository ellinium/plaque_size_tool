from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='plaque-size-tool',
      version='1.0.1',
      description='Bacteriophage plaque size measurement tool',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='http://github.com/ellinium/plaque_size_tool',
      author='Ellina Trofimova, Ilya Trofimov',
      author_email='ellina.trofimova@gmail.com',
      license='Apache 2.0',
      install_requires=['numpy', 'opencv-python', 'imutils', 'pandas', 'Pillow'],
      py_modules=['plaque_size_tool'],
      zip_safe=False,
      keywords='bacteriophage phage virus viral plaque size')