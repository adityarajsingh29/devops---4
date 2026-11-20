# Jenkins with the tools the pipeline needs (python for tests, docker CLI for builds)
FROM jenkins/jenkins:lts-jdk17

USER root
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-venv docker-cli curl \
    && rm -rf /var/lib/apt/lists/*
USER jenkins

RUN jenkins-plugin-cli --plugins workflow-aggregator git pipeline-stage-view credentials-binding junit

# No setup wizard; allow checkout of the local repository mounted at /repo
ENV JAVA_OPTS="-Djenkins.install.runSetupWizard=false -Dhudson.plugins.git.GitSCM.ALLOW_LOCAL_CHECKOUT=true"
COPY init.groovy /usr/share/jenkins/ref/init.groovy.d/init.groovy
