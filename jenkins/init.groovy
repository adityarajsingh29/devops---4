// Jenkins configuration as code: admin user, Vault token credential and the pipeline job.
// Secrets come from environment variables at container start - nothing secret is stored in Git.
import jenkins.model.Jenkins
import hudson.security.HudsonPrivateSecurityRealm
import hudson.security.FullControlOnceLoggedInAuthorizationStrategy
import hudson.util.Secret
import hudson.model.ParametersDefinitionProperty
import hudson.model.StringParameterDefinition
import hudson.plugins.git.BranchSpec
import hudson.plugins.git.GitSCM
import com.cloudbees.plugins.credentials.CredentialsScope
import com.cloudbees.plugins.credentials.SystemCredentialsProvider
import com.cloudbees.plugins.credentials.domains.Domain
import org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl
import org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition
import org.jenkinsci.plugins.workflow.job.WorkflowJob

def j = Jenkins.get()

def realm = new HudsonPrivateSecurityRealm(false)
realm.createAccount('admin', System.getenv('JENKINS_ADMIN_PASSWORD'))
j.setSecurityRealm(realm)
def auth = new FullControlOnceLoggedInAuthorizationStrategy()
auth.setAllowAnonymousRead(false)
j.setAuthorizationStrategy(auth)

def store = SystemCredentialsProvider.getInstance().getStore()
store.addCredentials(Domain.global(), new StringCredentialsImpl(
    CredentialsScope.GLOBAL, 'vault-token', 'Read-only Vault token (policy lab4-read)',
    Secret.fromString(System.getenv('VAULT_TOKEN'))))

def scm = new GitSCM(GitSCM.createRepoList('file:///repo', null), [new BranchSpec('*/${BRANCH}')], null, null, [])
def flow = new CpsScmFlowDefinition(scm, 'Jenkinsfile')
flow.setLightweight(false)
def job = j.getItem('lab4-pipeline') ?: j.createProject(WorkflowJob, 'lab4-pipeline')
job.addProperty(new ParametersDefinitionProperty(new StringParameterDefinition('BRANCH', 'main', 'Git branch to build')))
job.setDefinition(flow)
job.save()
j.save()
