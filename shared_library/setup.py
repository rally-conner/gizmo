from os.path import abspath, dirname, join
from setuptools import setup, find_packages


artifactory_repo_name = 'robotfw_core_resources'
# line below is replaced by script in Jenkins - LEAVE IT
artifactory_version = 'DEV'

CURDIR = dirname(abspath(__file__))


def get_requirements():
    requirements = []
    with open(join(CURDIR, 'requirements.txt')) as f:
        for line in f.readlines():
            line = line.strip()
            # Remove empty lines and comment lines
            if line and not line.startswith('#'):
                requirements.append(line)
    return requirements

def get_packages():
    return find_packages(exclude=['doc', 'imgs', 'test'])


setup(
    name=artifactory_repo_name,
    version=artifactory_version,
    dependency_links=['https://artifacts.werally.in/artifactory/api/pypi/pypi-release/simple'],
    maintainer='Core QA',
    maintainer_email='core-qa@rallyhealth.com',
    install_requires=['robotfw_resources', get_requirements()],
    packages=get_packages(),
    package_dir={'': '.'},
    include_package_data=True,
    zip_safe=False,
    description='Accounts Robot Framework Resources',
    url='https://github.com/AudaxHealthInc/Core-AutomatedTests/SharedLibrary',
)
