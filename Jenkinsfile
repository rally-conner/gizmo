@Library("pipeline-scripts") _

import com.rally.Robot
def semverScript = libraryResource 'semver.sh'

String serviceName = 'gizmo-playground'
Robot robot = new Robot()

/*





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
    stage("build") {
      steps {
        echo "i am in build step"
        script {
          def userInput = input(
            id: 'userInput', message: 'Please give the folder?', parameters: [
            [$class: 'TextParameterDefinition', defaultValue: 'Tool1', description: 'Package Name to build', name: 'folder_name']]
          )
        }
        echo "i m in build 2 now"
        abc = "${params.userInput}"
        echo "$abc"
        echo "check check"
      }
    }
    stage('Create .pypirc') {
      steps {
        script {
          robot.setPypirc()
        }
      }
      post {
        always {
            sh "cat  ~/.pypirc"
        }
      }
    }
    stage('Build: run setup.py and push AF'){
      steps {
        script {
          if ("${params.build_type}" == "SNAPSHOT"){
            repoNameToBuild = "${params.userInput}_${params.build_type}"
            } else {
            repoNameToBuild = "${params.userInput}"
          }
        }
        withEnv([RELEASE="${params.release}",PACKAGE_PATH="${params.userInput}", ARTI_REPO_NAME="${repoNameToBuild}"]){
          script {
            robot.execPythonSetup()
          }
        }
      }
    }
  }
}