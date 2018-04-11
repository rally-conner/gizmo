@Library("pipeline-scripts") _
import com.rally.Robot
import com.rally.Git
def semverScript = libraryResource 'semver.sh'
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
    choice(name: 'release', choices: 'rally-versioning\npatch\nminor\nmajor', description: 'Type of release to make.  Use rally-versions for a SNAPSHOT')
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
    }
    //stage('Create .pypirc') {
    //  steps{
    //    sh "rm ~/.pypirc"
    //    sh "echo '[distutils]' >> ~/.pypirc"
    //    sh "echo 'index-servers = rallyhealth' >> ~/.pypirc"
    //    sh "echo '[rallyhealth]' >> ~/.pypirc"
    //    sh "echo 'repository: https://artifacts.werally.in/artifactory/api/pypi/pypi-release-local' >> ~/.pypirc"
    //    sh "echo 'username: $ARTIFACTORY_USER' >> ~/.pypirc"
    //    sh "echo 'password: $ARTIFACTORY_PASSWORD' >> ~/.pypirc"
    //  }
    //}
    stage('Get tag version') {
      steps {
        script {
          version = 'v3.0'
          git_version = git.previousVersion()
        }
        echo "test me"
        echo "${version}"
        echo "${git_version}"
      }
    }
    //stage('Build: run setup.py and push AF'){
    //  steps {
    //    script {
    //      if ("${params.BUILD_TYPE}" == "SNAPSHOT"){
    //        repoNameToBuild = "${serviceName}_${params.BUILD_FOLDER}_${params.BUILD_TYPE}"
    //        } else {
    //        repoNameToBuild = "${serviceName}_${params.BUILD_TYPE}"
    //      }
    //    }
    //    sh """
    //      cd $BUILD_FOLDER
    //      sed -i -e \"1,/artifactory_repo_name.*/s/artifactory_repo_name.*/artifactory_repo_name = '${repoNameToBuild}'/\" setup.py
    //      sed -i -e \"1,/artifactory_version.*/s/artifactory_version.*/artifactory_version = '${version}'/\" setup.py
    //      python setup.py sdist upload -r rallyhealth
    //    """.trim()
    //  }
    //}
  }
}