def call(dockerRepoName, imageName, portNum) {
	pipeline {
		agent any

		parameters {
			booleanParam(defaultValue: false, description: 'Deploy the App', name: 'DEPLOY')
		}


		stages {
			stage('Build') {
				steps {
                    dir('../') {
                        sh 'pip install -r requirements.txt --break-system-packages'
                        sh 'pip install --upgrade flask --break-system-packages'
                    }
                }
			}
			stage('Python Lint') {
				steps {
                    sh 'pylint --fail-under 5.0 *.py'
				}
			}
			stage('Test and Coverage') {
				steps {
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
				post {
					always {
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
			stage ('Zip Archive') {
				steps {
					sh 'zip app.zip *.py'
				}
				post {
					always {
						archiveArtifacts artifacts: 'app.zip', fingerprint: true
					}
				}
			}
			stage('Package') {
				when {
					expression { env.GIT_BRANCH == 'origin/main' }
				}
				steps {
					withCredentials([usernamePassword(credentialsId: 'b394d855-0512-4dc6-b554-e738752982c5', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
						sh 'echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin docker.io'
						sh "docker build -t ${dockerRepoName}:latest --tag amanbinepal/${dockerRepoName}:${imageName} ."
						sh "docker push amanbinepal/${dockerRepoName}:${imageName}"
					}
				}
			}
			stage('Deliver') {
				when {
					expression { params.DEPLOY }
				}
				steps {
					sh "docker stop ${dockerRepoName} || true && docker rm ${dockerRepoName} || true"
					sh "docker run -d -p ${portNum}:${portNum} --name ${dockerRepoName} ${dockerRepoName}:latest"
				}
			}
		}
	}
}

