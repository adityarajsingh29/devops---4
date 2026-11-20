// Lab 4 CI/CD pipeline: tests are gates - a failing stage stops everything after it.
pipeline {
    agent any

    // VAULT_ADDR, KUBECONFIG, TEST_NETWORK and MINIKUBE_NODE are provided by the Jenkins controller environment
    environment {
        IMAGE     = "lab4-app:${BUILD_NUMBER}"
        NAMESPACE = 'lab4'
    }

    stages {
        stage('Unit Tests') {
            steps {
                sh '''
                    python3 -m venv .venv
                    .venv/bin/pip install -q -r requirements-test.txt
                    mkdir -p reports
                    .venv/bin/pytest tests/test_unit.py -v --junitxml=reports/unit.xml
                '''
            }
        }

        stage('Build Image') {
            steps {
                sh 'docker build -t $IMAGE --build-arg APP_VERSION=1.$BUILD_NUMBER .'
            }
        }

        stage('Integration Tests') {
            steps {
                sh '''
                    docker rm -f lab4-it 2>/dev/null || true
                    docker run -d --name lab4-it --network $TEST_NETWORK $IMAGE
                    for i in $(seq 1 20); do curl -fs http://lab4-it:5000/health && break; sleep 1; done
                    BASE_URL=http://lab4-it:5000 EXPECTED_VERSION=1.$BUILD_NUMBER \
                      .venv/bin/pytest tests/test_integration.py -v --junitxml=reports/integration.xml
                '''
            }
            post { always { sh 'docker rm -f lab4-it || true' } }
        }

        stage('Fetch Secrets (Vault)') {
            steps {
                withCredentials([string(credentialsId: 'vault-token', variable: 'VAULT_TOKEN')]) {
                    sh '''
                        set +x
                        DB_PASSWORD=$(curl -fs -H "X-Vault-Token: $VAULT_TOKEN" $VAULT_ADDR/v1/secret/data/lab4/app \
                          | python3 -c "import json,sys; print(json.load(sys.stdin)['data']['data']['db_password'])")
                        kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
                        kubectl -n $NAMESPACE create secret generic lab4-app-secrets \
                          --from-literal=DB_PASSWORD="$DB_PASSWORD" --dry-run=client -o yaml | kubectl apply -f -
                        echo "Secret lab4-app-secrets updated from Vault (value not printed)"
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    docker save $IMAGE | docker exec -i $MINIKUBE_NODE docker load
                    sed "s|image: lab4-app:.*|image: $IMAGE|" k8s/app/deployment.yaml | kubectl -n $NAMESPACE apply -f -
                    kubectl -n $NAMESPACE apply -f k8s/app/service.yaml
                    kubectl -n $NAMESPACE rollout status deployment/lab4-app --timeout=120s
                '''
            }
        }

        stage('Smoke Test') {
            steps {
                sh '''
                    kubectl -n $NAMESPACE run smoke-$BUILD_NUMBER --rm -i --quiet --restart=Never --image=busybox:1.36 -- \
                      wget -qO- http://lab4-app/secret-check
                '''
            }
        }
    }

    post {
        always  { junit allowEmptyResults: true, testResults: 'reports/*.xml' }
        success { echo 'Pipeline passed: all test gates green, deployed to Kubernetes.' }
        failure { echo 'Pipeline failed: a gate failed, nothing after it was deployed.' }
    }
}
