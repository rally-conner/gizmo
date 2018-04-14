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
            repoNameToBuild = "${serviceName}_${params.BUILD_FOLDER}"
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
          // set up email contents
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
          sendEmailNotification("${recipients}", "${emailSubject}","${emailBody}")
        }
      }
    } // end of Publish git tag to github
  } // end of stages
}  // end of pipeline


/*
This method will recreate three String parameters. Also
we hard code the email domain here, so it will not send
outsite Rally
*/
def sendEmailNotification(emailRecipients, emailSubject, emailBody) {
    emailBody = '''
    <!DOCTYPE html>
<head>
  <title>Build report</title>
  <style type="text/css">
    body
    {
      margin: 0px;
      padding: 15px;
    }
 
    body, td, th
    {
      font-family: "Lucida Grande", "Lucida Sans Unicode", Helvetica, Arial, Tahoma, sans-serif;
      font-size: 10pt;
    }
 
    th
    {
      text-align: left;
    }
 
    h1
    {
      margin-top: 0px;
    }
 
    li
    {
      line-height: 15pt;
    }
 
    .change-add
    {
      color: #272;
    }
 
    .change-delete
    {
      color: #722;
    }
 
    .change-edit
    {
      color: #247;
    }
 
    .grayed
    {
      color: #AAA;
    }
 
    .error
    {
      color: #A33;
    }
 
    pre.console
    {
      color: #333;
      font-family: "Lucida Console", "Courier New";
      padding: 5px;
      line-height: 15px;
      background-color: #EEE;
      border: 1px solid #DDD;
    }
  </style>
</head>
<body>
 
<h1>Build ${build.result}</h1>
<table>
  <tr><th>Build URL:</th><td><a href="${rooturl}${build.url}">${rooturl}${build.url}</a></td></tr>
  <tr><th>Project:</th><td>${project.name}</td></tr>
  <tr><th>Date of build:</th><td>${it.timestampString}</td></tr>
  <tr><th>Build duration:</th><td>${build.durationString}</td></tr>
</table>
 
<!-- CHANGE SET -->
<% changeSet = build.changeSet
if (changeSet != null) {
  hadChanges = false %>
  <h2>Changes</h2>
  <ul>
<%   changeSet.each { cs ->
    hadChanges = true
    aUser = cs.author %>
      <li>Commit <b>${cs.revision}</b> by <b><%= aUser != null ? aUser.displayName : it.author.displayName %>:</b> (${cs.msg})
        <ul>
<%        cs.affectedFiles.each { %>
          <li class="change-${it.editType.name}"><b>${it.editType.name}</b>: ${it.path}</li>
<%        } %>
        </ul>
      </li>
<%  }
 
  if (!hadChanges) { %> 
      <li>No Changes</li>
<%  } %>
  </ul>
<% } %>
 
<!-- ARTIFACTS -->
<% artifacts = build.artifacts
if (artifacts != null && artifacts.size() > 0) { %>
  <h2>Build artifacts</h2>
    <ul>
<%    artifacts.each() { f -> %>    
      <li><a href="${rooturl}${build.url}artifact/${f}">${f}</a></li>
<%    } %>
    </ul>
<% } %>
 
<% 
  testResult = build.testResultAction
 
  if (testResult) {
    jobName = build.parent.name
    rootUrl = hudson.model.Hudson.instance.rootUrl
    testResultsUrl = "${rootUrl}${build.url}testReport/"
 
    if (testResult.failCount){
      lastBuildSuccessRate = String.format("%.2f", (testResult.totalCount - testResult.failCount) * 100f / testResult.totalCount)
    }
    else{
      lastBuildSuccessRate = 100f;
    }
    
    startedPassing = []
    startedFailing = []
    failing = []
 
    previousFailedTestCases = new HashSet()
    currentFailedTestCase = new HashSet()
 
    if (build.previousBuild?.testResultAction) {
      build.previousBuild.testResultAction.failedTests.each {
        previousFailedTestCases << it.simpleName + "." + it.safeName
      }
    }
 
    testResult.failedTests.each { tr ->
        packageName = tr.packageName
        className = tr.simpleName
        testName = tr.safeName
        displayName = className + "." + testName
        
        currentFailedTestCase << displayName
        url = "${rootUrl}${build.url}testReport/$packageName/$className/$testName"
        if (tr.age == 1) {
          startedFailing << [displayName: displayName, url: url, age: 1]
        } else {
          failing << [displayName: displayName, url: url, age: tr.age]
        }
    }
 
    startedPassing = previousFailedTestCases - currentFailedTestCase
    startedFailing = startedFailing.sort {it.displayName}
    failing = failing.sort {it.displayName}
    startedPassing = startedPassing.sort()
%>
 
<% if (testResult) { %>
<h2>Test Results</h2>
<ul>
  <li>Total tests ran: <a href="${testResultsUrl}">${testResult.totalCount}</a></li>
  <%if (testResult.failCount){%>
    <li>Failure count and delta: ${testResult.failCount} ${testResult.failureDiffString}</li>
  <%}%>
  <li>Success rate: ${lastBuildSuccessRate}% </li>
</ul> 
<% } %>
 
<% if (startedPassing) { %>
<h3>Following tests started passing. Good work!</h3>
<ul>
  <% startedPassing.each { %>
    <li>${it}</li>
  <% } %>
</ul>
<% } %>
 
<% if (startedFailing) { %>
<h3>Following tests started FAILING. Have the last change caused it!!</h3>
<ul>
  <% startedFailing.each { %>
    <li><a href="${it.url}">${it.displayName}</a></li>
  <% } %>
</ul>
<% } %>
 
<% if (failing) { %>
<h3>Following tests are conitnuously failing. Someone should look into it!!!</h3>
<ul>
  <% failing.each { %>
    <li><a href="${it.url}">${it.displayName}</a> (Failing since ${it.age} runs)</li>
  <% } %>
</ul>
<% } %>
 
<% } %>
 
<!-- BUILD FAILURE REASONS -->
<% if (build.result == hudson.model.Result.FAILURE) {
  log = build.getLog(100).join("\n")
  warningsResultActions = build.actions.findAll { it.class.simpleName == "WarningsResultAction" }
 
  if (warningsResultActions.size() > 0) { %>
    <h2>Build errors</h2>
    <ul>
    <% warningsResultActions.each {
        newWarnings = it.result.newWarnings
        if (newWarnings.size() > 0) {
          newWarnings.each {
            if (it.priority.toString() == "HIGH") { %>
              <li class="error">In <b>${it.fileName}</b> at line ${it.primaryLineNumber}: ${it.message}</li>
          <% }} %>
    <% }} %>
    </ul>
  <% } %>
 
<h2>Console output</h2>
<pre class="console">${log}</pre>
 
<% } %>
 
</body>

    '''

    emailext (
      mimeType: 'text/html',
      to: "${emailRecipients}@rallyhealth.com",
      subject: "${emailSubject}",
      body: "${emailBody}"
      recipientProviders: [[$class: 'CulpritsRecipientProvider']]
    )
}

/*


*/
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
}

/*



*/
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