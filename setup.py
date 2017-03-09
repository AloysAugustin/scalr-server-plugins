from setuptools import setup, find_packages

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='scalr_server_plugins',
      version='0.0.1',
      description='Plugin manager for Scalr',
      long_description=readme(),
      url='https://github.com/momohawari/scalr-server-plugins',
      author='Mohammed Hawari, Aloys Augustin',
      author_email='mohammed@scalr.com, aloys@scalr.com',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'virtualenv',
      ],
      entry_points = {
          'console_scripts': ['scalr-server-plugins=scalr_server_plugins:main'],
      },
      include_package_data=True,
      zip_safe=False)
