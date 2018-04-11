@Library("pipeline-scripts") _

import com.rally.Robot
def semverScript = libraryResource 'semver.sh'

Robot robot = new Robot()

/*



*/

pipeline {
  agent {
    node {
      label 'Pipeline_CI'
    }
  }
  environment {
      PIP_EXTRA_INDEX_URL = 'https://jenkins:$ARTIFACTORY_PASSWORD@artifacts.werally.in/artifactory/api/pypi/pypi-release-local'
    }
  parameters {
    choice(name: 'RELEASE', choices: 'rally-versioning\npatch\nminor\nmajor', description: 'Type of release to make.  Use rally-versions for a SNAPSHOT')
    choice(name: 'BUILD_TYPE', choices: 'SNAPSHOT\nRELEASE', description: 'Build type')
    string(name: 'SHA1', defaultValue: 'master', description: 'SHA to release')
    choice(name: 'BUILD_FOLDER', choices: 'shared_library\ntool1', description: 'Give folder to be built')
    }
  stages {
    stage('Checkout SCM') {
      steps {
        checkout scm: [
            $class: 'GitSCM',
            branches: scm.branches,
            doGenerateSubmoduleConfigurations: scm.doGenerateSubmoduleConfigurations,
            extensions: [[$class: 'CloneOption', noTags: false, reference: '', shallow: false]],
            userRemoteConfigs: scm.userRemoteConfigs
        ]
      } 
    }
    stage('Create .pypirc') {
      steps{
        sh """
          echo '[distutils]
          index-servers = rallyhealth
          [rallyhealth]
          repository: https://artifacts.werally.in/artifactory/api/pypi/pypi-release-local
          username: $ARTIFACTORY_USER
          password: $ARTIFACTORY_PASSWORD' > ~/.pypirc
        """.trim()
      }
    }
    stage('Build: run setup.py and push AF'){
      steps {
        script {
          if ("${params.BUILD_TYPE}" == "SNAPSHOT"){
            repoNameToBuild = "${params.BUILD_FOLDER}_${params.BUILD_TYPE}"
            } else {
            repoNameToBuild = "${params.BUILD_TYPE}"
            version = "v1.0"
          }
        }
        sh """
          cd $BUILD_FOLDER
          echo ${repoNameToBuild}
          sed -i -e \"1,/artifactory_repo_name.*/s/artifactory_repo_name.*/artifactory_repo_name = '${repoNameToBuild}'/\" setup.py
          sed -i -e \"1,/artifactory_version.*/s/artifactory_version.*/artifactory_version = '${version}'/\" setup.py
          python setup.py sdist upload -r rallyhealth
        """.trim()
      }
    }
  }
}