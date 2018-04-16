// def runPythonSetup(repoNameToBuild, nextGitTagVersion, artifactoryFolderName, runtimeTimeStemp) {
//   sh (
//     script: """
//       cd '${env.BUILD_FOLDER}'
//       sed -i -e \"1,/artifactory_repo_name.*/s/artifactory_repo_name.*/artifactory_repo_name = '${repoNameToBuild}'/\" setup.py
//       sed -i -e \"1,/artifactory_version.*/s/artifactory_version.*/artifactory_version = '${nextGitTagVersion}-${artifactoryFolderName}-${runtimeTimeStemp}'/\" setup.py
//       python setup.py sdist upload -r rallyhealth
//     """, returnStatus: true
//     ) == 0
// }


// /*
// This method will recreate three String parameters. Also
// we hard code the email domain here, so it will not send
// outsite Rally
// */
// def sendEmailNotification(emailRecipients, emailSubject, emailBody) {
//     emailext (
//       to: "${emailRecipients}@rallyhealth.com",
//       subject: "${emailSubject}",
//       body: "${emailBody}",
//       recipientProviders: [[$class: 'CulpritsRecipientProvider']]
//     )
// }

// /*


// */
// def createPypirc() {
//   rs = sh (
//     script: """
//       rm ~/.pypirc
//       echo '[distutils]' >> ~/.pypirc
//       echo 'index-servers = rallyhealth' >> ~/.pypirc
//       echo '[rallyhealth]' >> ~/.pypirc
//       echo 'repository: https://artifacts.werally.in/artifactory/api/pypi/pypi-release-local' >> ~/.pypirc
//       echo 'username: $ARTIFACTORY_USER' >> ~/.pypirc
//       echo 'password: $ARTIFACTORY_PASSWORD' >> ~/.pypirc
//     """, returnStatus: true
//     ) == 0
// }

// /*

def getName(name)
  rs = 'Hello ${name}'
  return rs



// */
// def getNextTagNumber(String releaseType, String releaseFolder) {
//     tag = sh  (
//             script: 'git describe --first-parent --tags --abbrev=0 --match "v[0-9]*"',
//             returnStdout: true
//     ).trim()
//     tag = tag.replaceAll("[^.0-9]","")
//     def versions = []
//     versions = tag.tokenize(".").collect {it as int}
//     snapshot = false

//     switch(releaseType) {
//         case "major":
//             versions[0] = versions[0] + 1
//             versions[1] = 0
//             versions[2] = 0
//             break
//         case "minor":
//             versions[1] = versions[1] + 1
//             versions[2] = 0
//             break
//         case "patch":
//             versions[2] = versions[2] + 1
//             break
//         default:
//             println("Invalid release value set.  Valid values are: major/minor/patch.  Releasing SNAPSHOT")
//             snapshot = true
//     }

//     version = "${versions.collect {it.toString()}.join(".")}"

//     return "v${version}"
// }
