pipeline {
    environment {
        // Docker image name and tag to be used.
        // The :latest tag will also be applied.
        IMAGE_NAME = 'tornado-object-storage'
        IMAGE_TAG = 'v1'
        // DOCKER_IMAGE is used as a reference to the built image between stages
        DOCKER_IMAGE = ''
    }
    agent any
    stages {
        stage('Source') {
            steps {
                // Download the latest project source code
                // Use the 'main' (default) branch of the repository
                git branch: 'main',
                    url: 'https://github.com/kyoobit/python_tornado_object_storage.git'
            }
        }
        stage('Install Requirements') {
            // Use the Makefile to install dependencies of the project
            steps {
                sh 'make install'
            }
        }
        stage('Format Code') {
            // Use the Makefile to check the format of the project
            steps {
                sh 'make format'
            }
        }
        stage('Lint Code') {
            // Use the Makefile to lint the project
            steps {
                sh 'make lint'
            }
        }
        stage('Test Code') {
            // Use the Makefile to run tests on the project
            steps {
	            sh 'make test'
            }
        }
        stage('Check Dependencies') {
            // Use the Makefile to check for vulnerabilities in dependencies
            steps {
	            sh 'make depcheck'
            }
        }
        stage('Security Scan') {
            // Use the Makefile to run a static security scan on the project
            steps {
	            sh 'make secscan'
            }
        }
        stage('Build Image') {
            // Build an image of the project
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerHubAccount', 
                        passwordVariable: 'dockerHubPassword', 
                        usernameVariable: 'dockerHubUser'
                    )
                ]) {
                    sh "echo '${env.dockerHubUser}/${IMAGE_NAME}:${IMAGE_TAG}'"
                    script {
                        DOCKER_IMAGE = docker.build("${env.dockerHubUser}/${IMAGE_NAME}:${IMAGE_TAG}")
                    }
                }
            }
        }
        stage('Push Image') {
            // Push the image to Docker Hub
            steps {
                script {
                    docker.withRegistry('', 'dockerHubAccount') {
                        DOCKER_IMAGE.push("${IMAGE_TAG}")
                        DOCKER_IMAGE.push('latest')
                    }
                }
            }
        }
        stage('Run Image') {
            // Pull the image and run a container
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerHubAccount', 
                        passwordVariable: 'dockerHubPassword', 
                        usernameVariable: 'dockerHubUser'
                    )
                ]) {
                    sh "docker rm -f docker.io/${env.dockerHubUser}/${IMAGE_NAME}:${IMAGE_TAG}"
                    sh "docker pull docker.io/${env.dockerHubUser}/${IMAGE_NAME}:${IMAGE_TAG}"
                    sh "docker run --rm --detach docker.io/${env.dockerHubUser}/${IMAGE_NAME}:${IMAGE_TAG}"
                }
            }
        }
        // TODO: stage('Test Image')
        // Run tests against the running container
    }
}