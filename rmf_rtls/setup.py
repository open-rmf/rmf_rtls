from setuptools import setup

package_name = 'rmf_rtls'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    author='youliang',
    author_email='youliang@openrobotics.org',
    zip_safe=True,
    maintainer='youliang',
    maintainer_email='youliang@openrobotics.org',
    description='A package containing scripts for rtls',
    license='Apache License Version 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
          'rmf_rtls_server = rmf_rtls.rmf_rtls_server:main',
        ],
    },
)
