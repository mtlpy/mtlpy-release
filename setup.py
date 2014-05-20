from setuptools import setup, find_packages

setup(name='mtlpyrelease',
      version='0.1',
      description='Montreal-Python',
      author='mtlpy',
      author_email='mtlpyteam@googlegroups.com',
      url='http://montrealpython.org/',
      packages=find_packages(),
      entry_points = {
          'console_scripts': [
          'mtlpyr = mtlpyrelease:main'
          ]
      },
      install_requires=['translate>=0.0.6']
      )
