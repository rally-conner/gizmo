@Library("pipeline-scripts") _

import com.rally.Robot
def semverScript = libraryResource 'semver.sh'

String serviceName = 'gizmo-playground'
Robot robot = new Robot()

/*

        withEnv([RELEASE="${params.release}",PACKAGE_PATH="${params.build_folder}", ARTI_REPO_NAME="${repoNameToBuild}"]){
          script {
            robot.execPythonSetup()
          }
        }

*/

pipeline {
  agent {
    node {
      label 'Pipeline_CI'
      customWorkspace "${serviceName}"
    }
  }
  environment {
      PIP_EXTRA_INDEX_URL = 'https://jenkins:$ARTIFACTORY_PASSWORD@artifacts.werally.in/artifactory/api/pypi/pypi-release-local'
    }
  parameters {
    choice(name: 'release', choices: 'rally-versioning\npatch\nminor\nmajor', description: 'Type of release to make.  Use rally-versions for a SNAPSHOT')
    choice(name: 'build_type', choices: 'SNAPSHOT\nRELEASE', description: 'Build type')
    string(name: 'sha1', defaultValue: 'master', description: 'SHA to release')
    choice(name: 'build_folder', choices: 'shared_library\ntool1', description: 'Give folder to be built')
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
          if ("${params.build_type}" == "SNAPSHOT"){
            repoNameToBuild = "${params.build_folder}_${params.build_type}"
            } else {
            repoNameToBuild = "${params.build_folder}"
          }
        }
        sh """
          echo 'test me'
          echo ${repoNameToBuild}
          echo 'test you'
          ls -a
          env
          echo $sha1
          pwd
          cat ~/.pypirc
        """.trim()
      }
    }
  }
}