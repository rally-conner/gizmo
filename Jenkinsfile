@Library("pipeline-scripts") _

import com.rally.Robot
import com.rally.Git
import java.text.SimpleDateFormat

def semverScript = libraryResource 'semver.sh'
def date = new Date()
def dateFormat = new SimpleDateFormat("yyyyMMddHHmm")
String runtimeTimeStemp = dateFormat.format(date)
String serviceName = "gizmo"
Robot robot = new Robot()
Git git = new Git()
PythonSetupRelease pystup = new PythonSetupRelease()

/*
This pipeline is designed for push release to Artifacotry
*/

pipeline {
  agent {
    node {
      label 'Pipeline_CI'
      customWorkspace "${serviceName}${runtimeTimeStemp}"
    }
  }
  environment {
      PIP_EXTRA_INDEX_URL = 'https://jenkins:$ARTIFACTORY_PASSWORD@artifacts.werally.in/artifactory/api/pypi/pypi-release-local'
    }
  parameters {
    choice(name: 'release', choices: 'patch\nminor\nmajor', description: 'Type of release to make.  Use rally-versions for a SNAPSHOT')
    choice(name: 'BUILD_TYPE', choices: 'SNAPSHOT\nRELEASE', description: 'Build type')
    string(name: 'sha1', defaultValue: 'master', description: 'SHA to release')
    choice(name: 'BUILD_FOLDER', choices: 'shared_library\ntool1\ntool2', description: 'Give folder to be built')
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
    }  // end of checkout SCM
    stage('Create .pypirc') {
      steps{
        script {
          pystup.createPypirc()
        }
      }
    }  // end of Create .pypirc
    stage('Get tag version') {
      steps {
        script {
          nextGitTagVersion = pystup.getNextTagNumber("${params.release}", "${params.BUILD_FOLDER}")
        }
      }
    } // end of Get tag version
    stage('Build: run setup.py and push AF') {
      steps {
        script {
          if ("${params.BUILD_TYPE}" == "SNAPSHOT") {
            repoNameToBuild = "${serviceName}_${params.BUILD_FOLDER}_${params.BUILD_TYPE}"
            artifactoryFolderName = "${params.BUILD_FOLDER}-${params.BUILD_TYPE}"
            pystup.runPythonSetup("${repoNameToBuild}", "${nextGitTagVersion}", "${artifactoryFolderName}", "${runtimeTimeStemp}") 
          } else {
            repoNameToBuild = "${serviceName}_${params.BUILD_FOLDER}"
            artifactoryFolderName = "${params.BUILD_TYPE}"
            pystup.runPythonSetup("${repoNameToBuild}", "${nextGitTagVersion}", "${artifactoryFolderName}", "${runtimeTimeStemp}")
          }
        }
      }
    } // end of run setup.py and push AF
    stage('Publish git tag to github') {
      steps {
        script {
          git.push("${nextGitTagVersion}-${params.BUILD_FOLDER}", "${BUILD_URL}")
          // set up email contents (This is free-form and each team can have their format)
          // Please make sure to provide recipients name, suggest to use group emial
          recipients = "joe.tang"
          emailSubject = "Build Success ${env.JOB_NAME} ${env.BUILD_NUMBER}"
          emailBody = """         
            \nYour New Git Tag is: '${nextGitTagVersion}-${params.BUILD_FOLDER}' 
            \nYour build type is: ${env.BUILD_TYPE} 
            \nYour release is: ${env.release}
            \nYour new Artifacotry file name is: '${nextGitTagVersion}-${artifactoryFolderName}-${runtimeTimeStemp}'
            \nand under folder '${repoNameToBuild}' 
            \nGit Link: https://github.com/AudaxHealthInc/${serviceName}/tags
            \nJenkin Link: https://rally-jenkins.werally.in/job/rallyhealth-release/job/${serviceName}/${env.BUILD_NUMBER}/ 
          """
        }
      }
      post {
        success {
          pystup.sendEmailNotification("${recipients}", "${emailSubject}","${emailBody}")
        }
      }
    } // end of Publish git tag to github
  } // end of stages
}  // end of pipeline