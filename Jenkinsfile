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

/*



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
          createPypirc()
        }
      }
    }  // end of Create .pypirc
    stage('Get tag version') {
      steps {
        script {
          nextGitTagVersion = getNextTagNumber("${params.release}", "${params.BUILD_FOLDER}")
        }
        echo "Next Git Tag version is ${nextGitTagVersion}"
      }
    } // end of Get tag version
    stage('Build: run setup.py and push AF') {
      steps {
        script {
          if ("${params.BUILD_TYPE}" == "SNAPSHOT") {
            repoNameToBuild = "${serviceName}_${params.BUILD_FOLDER}_${params.BUILD_TYPE}"
            artifactoryFolderName = "${params.BUILD_FOLDER}-${params.BUILD_TYPE}"
          } else {
            repoNameToBuild = "${serviceName}_${params.BUILD_TYPE}"
            artifactoryFolderName = "${params.BUILD_TYPE}"
        }
       }
        sh """
          cd $BUILD_FOLDER
          sed -i -e \"1,/artifactory_repo_name.*/s/artifactory_repo_name.*/artifactory_repo_name = '${repoNameToBuild}'/\" setup.py
          sed -i -e \"1,/artifactory_version.*/s/artifactory_version.*/artifactory_version = '${nextGitTagVersion}-${artifactoryFolderName}-${runtimeTimeStemp}'/\" setup.py
          python setup.py sdist upload -r rallyhealth
        """.trim()
      }
    } // end of run setup.py and push AF
    stage('Publish git tag to github') {
      steps {
        script {
          git.push("${nextGitTagVersion}-${params.BUILD_FOLDER}", "${BUILD_URL}")
        }
      }
      post {
        success {
          script: emailext (
            to: joe.tang@rallyhealth.com,
            subject: "Build Success",
            body: "The new Git "
          )
        }
      }
    } // end of Publish git tag to github
  } // end of stages
}  // end of pipeline


def createPypirc() {
  rs = sh (
    script: """
      rm ~/.pypirc
      echo '[distutils]' >> ~/.pypirc
      echo 'index-servers = rallyhealth' >> ~/.pypirc
      echo '[rallyhealth]' >> ~/.pypirc
      echo 'repository: https://artifacts.werally.in/artifactory/api/pypi/pypi-release-local' >> ~/.pypirc
      echo 'username: $ARTIFACTORY_USER' >> ~/.pypirc
      echo 'password: $ARTIFACTORY_PASSWORD' >> ~/.pypirc
    """, returnStdout: true
    ) == 0
  sh "cat ~/.pypirc"
}


def getNextTagNumber(String releaseType, String releaseFolder) {
    tag = sh  (
            script: 'git describe --first-parent --tags --abbrev=0 --match "v[0-9]*"',
            returnStdout: true
    ).trim()
    tag = tag.replaceAll("[^.0-9]","")
    def versions = []
    versions = tag.tokenize(".").collect {it as int}
    snapshot = false

    switch(releaseType) {
        case "major":
            versions[0] = versions[0] + 1
            versions[1] = 0
            versions[2] = 0
            break
        case "minor":
            versions[1] = versions[1] + 1
            versions[2] = 0
            break
        case "patch":
            versions[2] = versions[2] + 1
            break
        default:
            println("Invalid release value set.  Valid values are: major/minor/patch.  Releasing SNAPSHOT")
            snapshot = true
    }

    version = "${versions.collect {it.toString()}.join(".")}"

    return "v${version}"
}