# Credentials and Secrets — bindings, scope, and where masking stops

Source: [Using credentials](https://www.jenkins.io/doc/book/using/using-credentials/), [Credentials Binding plugin](https://www.jenkins.io/doc/pipeline/steps/credentials-binding/), [Pipeline syntax — environment](https://www.jenkins.io/doc/book/pipeline/syntax/).
Covers: SKILL.md §4 — **"Bind every secret at the narrowest scope that works"**.

Which binding to use for each credential a Unity delivery pipeline needs, and the exact point where Jenkins'
log masking stops protecting you. The distinction that matters: a binding controls *who can read the value*,
masking only controls *whether the literal value is printed*, and neither survives a script that transforms
the secret before echoing it.

## Credential kinds and their bindings

| Kind | `withCredentials` binding | What lands in the build | Source |
|---|---|---|---|
| Secret text | `string(credentialsId: 'id', variable: 'TOKEN')` | The value in `$TOKEN` | [Credentials Binding](https://www.jenkins.io/doc/pipeline/steps/credentials-binding/) |
| Username / password | `usernamePassword(credentialsId: 'id', usernameVariable: 'USR', passwordVariable: 'PSW')` | Two variables | same |
| Secret file | `file(credentialsId: 'id', variable: 'KEYSTORE')` | A **path** to a temporary file, deleted when the block ends | same |
| SSH key | `sshUserPrivateKey(credentialsId: 'id', keyFileVariable: 'KEY')` | A path to the key file | same |
| Certificate | `certificate(credentialsId: 'id', keystoreVariable: 'P12')` | A path to the keystore | same |

The secret-file binding is the right kind for an Android keystore, an App Store Connect `.p8` key, and a
Firebase service-account JSON — all three are files, and a file binding keeps their contents out of the
environment entirely.

## `environment { credentials() }` against `withCredentials`

| Form | Scope | Use it when |
|---|---|---|
| `environment { KEY = credentials('id') }` at **pipeline** level | Every step in the file, including ones added later | Almost never. It is the form that turns one stage's secret into every stage's secret |
| `environment { KEY = credentials('id') }` at **stage** level | That stage only | A stage where several steps need the same value and a block would add nothing |
| `withCredentials([...]) { }` | The block, and nothing outside it | The default. The binding is visible at its point of use, and the reviewer can see the boundary |

For a username/password credential, `environment { CRED = credentials('id') }` also defines `CRED_USR` and
`CRED_PSW`. This is convenient and easy to forget, which is precisely the argument for the explicit block.

```groovy
stage('Sign and distribute') {
    steps {
        withCredentials([
            file(credentialsId: 'android-release-keystore', variable: 'KEYSTORE_PATH'),
            string(credentialsId: 'android-keystore-password', variable: 'KEYSTORE_PASSWORD'),
            file(credentialsId: 'firebase-service-account', variable: 'GOOGLE_APPLICATION_CREDENTIALS')
        ]) {
            sh 'bundle exec fastlane android distribute_qa'   // reads the variables from the environment
        }
    }
}
```

## Where masking fails

Jenkins replaces occurrences of a bound secret's **literal value** in the console output. It cannot recognise
anything derived from it. Each of these prints a readable secret:

| Pattern | Why masking misses it |
|---|---|
| `sh 'echo $TOKEN \| base64'` | The encoded form is not the literal value |
| `sh "curl -H 'Authorization: Bearer ${TOKEN}' …"` with `set -x` | The shell traces the expanded command line, and the trace is a different string than the value in some encodings |
| Writing the secret into a file the job later `cat`s or archives | Masking applies to the console, not to an archived artifact |
| A tool that prints its own configuration on error | The tool, not Jenkins, decided to print it |
| Groovy string interpolation `"${env.SECRET}"` inside a `sh` step | The value is baked into the command line before the shell runs, and appears in process listings on the agent |

Use single-quoted `sh` bodies so the **shell** expands the variable rather than Groovy, keep `set -x` off in
any block holding a secret, and never archive a file a secret was written into.

## Rules this pipeline holds to

| Rule | Consequence of breaking it |
|---|---|
| No secret value in the `Jenkinsfile`, a parameter default, or a script committed beside it | It is in git history, and removing it needs a history rewrite — a radius-3 operation, per `git-expert` |
| Credential **ids** are named in the pipeline and in the handoff; values never are | The id is the contract; the value is the CI host's business |
| A credential the controller does not have yet is reported as required, never invented | A pipeline referencing a non-existent id fails at the step that matters, on the first real run |
| A leaked value is escalated, not quietly rotated | `security-reviewer` owns the verdict, `cto` owns rotation |