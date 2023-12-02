def call(dockerRepoName, imageName, portNum) {
	pipeline {
		agent any

		parameters {
			booleanParam(defaultValue: false, description: 'Deploy the App', name: 'DEPLOY')
		}


		stages {
			stage('Build') {
				steps {
					dir("${dockerRepoName}") {
						echo "Current Directory: ${pwd()}"
						sh 'pip install -r requirements.txt --break-system-packages'
						sh 'pip install --upgrade flask --break-system-packages'
					}
                    
                }
			}
			stage('Python Lint') {
				steps {
					dir("${dockerRepoName}") {
                		sh 'pylint --fail-under 5.0 *.py'
					}
				}
			}
			stage('Test and Coverage') {
				steps {
					dir("${dockerRepoName}") {
						script {
							def test_reports_exist = fileExists 'test-reports'
							if (test_reports_exist) {
								sh 'rm test-reports/*.xml || true'
							}
							def api_test_reports_exist = fileExists 'api-test-reports'
							if (api_test_reports_exist) {
								sh 'rm api-test-reports/*.xml || true'
							}
						}
						script {
							def testFiles = findFiles(glob: '**/test*.py')
							
							if (testFiles) {
								for (def file in testFiles) {
									// Run each test file using the 'sh' step (assuming you're running Python tests)
									sh "coverage run --omit */site-packages/*,*/dist-packages/* ${file}"
								}
								sh "coverage report"
							} else {
								echo "No test files found in the workspace."
							}
						}
					}
				}
				post {
					always {
						dir("${dockerRepoName}") {
							script {
								def test_reports_exist = fileExists 'test-reports'
								if (test_reports_exist) {
									junit 'test-reports/*.xml'
								}
								def api_test_reports_exist = fileExists 'api-test-reports'
								if (api_test_reports_exist) {
									junit 'api-test-reports/*.xml'
								}
							}
						}
					}

				}
			}
/*
			stage ('Zip Archive') {
				steps {
					dir("${dockerRepoName}") {
						sh 'zip app.zip *.py'
					}
				}
				post {
					always {
						archiveArtifacts artifacts: 'app.zip', fingerprint: true
					}
				}
			}
*/
			stage('Package') {
				when {
					expression { env.GIT_BRANCH == 'origin/main' }
				}
				steps {
					withCredentials([string(credentialsId: 'AmanDocker', variable: 'TOKEN')]) {
						sh 'echo $TOKEN | docker login -u amanbinepal --password-stdin docker.io'
						dir("${dockerRepoName}") {
							sh "docker build -t ${dockerRepoName}:latest --tag amanbinepal/${dockerRepoName}:${imageName} ."
							sh "docker push amanbinepal/${dockerRepoName}:${imageName}"
						}
					}
				}
			}
			stage('Deliver') {
				when {
					expression { params.DEPLOY }
				}
				steps {
					dir('deployment') {
						sh "docker stop ${dockerRepoName} || true && docker rm ${dockerRepoName} || true"
						sh "docker run -d -p ${portNum}:${portNum} --name ${dockerRepoName} ${dockerRepoName}:latest"
						//sh "docker-compose up -d"
					}
				}
			}
		}
	}
}

