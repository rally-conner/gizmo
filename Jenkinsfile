@Library("pipeline-scripts") _

import com.rally.Robot
import com.rally.Git
import java.text.SimpleDateFormat



def semverScript = libraryResource 'semver.sh'
def date = new Date()
def dateFormat = new SimpleDateFormat("yyyyMMddHHmm")

String serviceName = 'gizmo'
Robot robot = new Robot()
Git git = new Git()

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
        sh "rm ~/.pypirc"
        sh "echo '[distutils]' >> ~/.pypirc"
        sh "echo 'index-servers = rallyhealth' >> ~/.pypirc"
        sh "echo '[rallyhealth]' >> ~/.pypirc"
        sh "echo 'repository: https://artifacts.werally.in/artifactory/api/pypi/pypi-release-local' >> ~/.pypirc"
        sh "echo 'username: $ARTIFACTORY_USER' >> ~/.pypirc"
        sh "echo 'password: $ARTIFACTORY_PASSWORD' >> ~/.pypirc"
      }
    }  // end of Create .pypirc
    stage ('Get Release Note') {
      steps {
        script {
          testCurl()
        }
      }
    }
    // stage('Get tag version') {
    //   steps {
    //     script {
    //       sh "git tag -d v2.0.0-shared_library"
    //       rs = isTagExist("${params.BUILD_FOLDER}")
    //       if ( !rs ) {
    //         git.push("v0.0.0-${params.BUILD_FOLDER}", "${BUILD_URL}")
    //       }
    //       nextGitTagVersion = getNextTagNumber("${params.release}", "${params.BUILD_FOLDER}")
    //       echo "Next release is ${nextGitTagVersion}"
    //       //runTime = dateFormat.format(date)
    //     }
    //   }
    // } // end of Get tag version
    // stage('Build: run setup.py and push AF') {
    //  steps {
    //    script {
    //     if ("${params.BUILD_TYPE}" == "SNAPSHOT"){
    //       repoNameToBuild = "${serviceName}_${params.BUILD_FOLDER}_${params.BUILD_TYPE}"
    //       artifactoryFolderName = "${params.BUILD_FOLDER}-${params.BUILD_TYPE}"
    //       } else {
    //       repoNameToBuild = "${serviceName}_${params.BUILD_TYPE}"
    //       artifactoryFolderName = "${params.BUILD_TYPE}"
    //     }
    //    }
    //   sh """
    //     cd $BUILD_FOLDER
    //     sed -i -e \"1,/artifactory_repo_name.*/s/artifactory_repo_name.*/artifactory_repo_name = '${repoNameToBuild}'/\" setup.py
    //     sed -i -e \"1,/artifactory_version.*/s/artifactory_version.*/artifactory_version = '${nextGitTagVersion}-${artifactoryFolderName}-${runTime}'/\" setup.py
    //     python setup.py sdist upload -r rallyhealth
    //   """.trim()
    // }
    // } // end of run setup.py and push AF
    // stage('Publish git tag to github') {
    //  steps {
    //    script {
    //      git.push("${nextGitTagVersion}-${params.BUILD_FOLDER}", "${BUILD_URL}")
    //    }
    //  }
    // } // end of Publish git tag to github
  } // end of stages
}  // end of pipeline


def testHttp() {
  def get = new URL("https://httpbin.org/get").openConnection();
  def getRC = get.getResponseCode();
  println(getRC);
  if(getRC.equals(200)) {
    println(get.getInputStream().getText());
 }
}

def testCurl() {

    tag123 = sh  (
            script: """
            curl -X GET https://api.github.com/repos/AudaxHealthInc/gizmo/tags -k \
            --header 'Authorization: Bearer 63c9e61cf9ef635338e7bebf41ed2cf0bc36c4ef'
            """,
            returnStdout: true
    ).trim()

    println tag123

}


// def getReleaseNote() {
//   def http = new HTTPBuilder()
//   url = "https://api.github.com"
//   http.request( url, GET, TEXT ) { req ->
//   uri.path = '/gizmo/releases/latest'
//   headers.'Authorization' = "Bearer 63c9e61cf9ef635338e7bebf41ed2cf0bc36c4ef"
//   response.success = { resp, reader ->
//     assert resp.statusLine.statusCode == 200
//     println "Got response: ${resp.statusLine}"
//     println "Content-Type: ${resp.headers.'Content-Type'}"
//     println reader.text
//   }
//   response.success = { resp, json ->
//     println("API response: ${json}")
//   }
//   response.'404' = {
//     println 'Not found'
//   }
//  } // end of req
// }


/*
Check the given git tag exist in the repo or not
if exist, return ture, else false

example: 

subfixValue = '-SNAPSHOT', it will search 'v[0-9].*subfixValue', so 
any of the values ('v1.0.0-SNAPSHOT', v1.0.1SNAPSHOT, v11.1.2-SNAPSHOT) will be true

subfixValue = '' , it will search 'v*[0-9]', so 
any of the value ('v1.0.1', 'v1', 'v0.0.1') will be true
*/
def isTagExist(String suffixValue) {

    String tagPattern = ""

    if (suffixValue == "") {
      tagPattern = "v*[0-9]"
    } else {
      tagPattern = "v[0-9]*${suffixValue}"
    }

    // compare the return status code == 0 and True/False
    rs = sh  (
            script: """
            git describe --first-parent --tags --abbrev=0 --match ${tagPattern}
            """, returnStatus: true
    ) == 0

    return rs
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