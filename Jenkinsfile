@Library("pipeline-scripts") _

import com.rally.Robot
def semverScript = libraryResource 'semver.sh'

String serviceName = 'gizmo-playground'
Robot robot = new Robot()

/*

    stage("build") {
      steps {
        echo "i am in build step"
        script {
          def userInput = input(
            id: 'userInput', message: 'Please give the folder?', parameters: [
            [$class: 'TextParameterDefinition', defaultValue: 'Tool1', description: 'Package Name to build', name: 'folder_name']]
          )
          echo "show me the input ${userInput}"
        }
        echo "i m in build 2 now"
        echo "${userInput}"
        echo "check check"
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
      steps {
        script {
          echo "test me test me"
          robot.setPypirc()
          echo "test you test you"
        }
      }
      post {
        always {
          script {
            sh "cat  ~/.pypirc"
          }
        }
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
        withEnv([RELEASE="${params.release}",PACKAGE_PATH="${params.build_folder}", ARTI_REPO_NAME="${repoNameToBuild}"]){
          script {
            robot.execPythonSetup()
          }
        }
      }
    }
  }
}