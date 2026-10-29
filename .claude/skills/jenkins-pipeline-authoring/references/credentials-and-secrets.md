# Credentials and Secrets

Sources: [a] book/using/using-credentials/, [b] pipeline/steps/credentials-binding/, [c] book/pipeline/syntax/ (environment) — below the SKILL.md `Docs:` base.

A binding controls who can read the value; masking only hides the literal value in console output.

## Bindings [b]

| Kind | `withCredentials` binding | Lands as |
|---|---|---|
| Secret text | `string(credentialsId: 'id', variable: 'TOKEN')` | value |
| Username/password | `usernamePassword(credentialsId: 'id', usernameVariable: 'USR', passwordVariable: 'PSW')` | two variables |
| Secret file | `file(credentialsId: 'id', variable: 'KEYSTORE')` | **path** to a temp file, deleted at block end |
| SSH key | `sshUserPrivateKey(credentialsId: 'id', keyFileVariable: 'KEY')` | key file path |
| Certificate | `certificate(credentialsId: 'id', keystoreVariable: 'P12')` | keystore path |

Use the file binding for an Android keystore, an App Store Connect `.p8` and a Firebase service-account JSON: contents stay out of the environment.

## Scope [c]

| Form | Scope | Use |
|---|---|---|
| `environment { KEY = credentials('id') }` at pipeline level | every step, including later additions | almost never |
| same at stage level | that stage | several steps share the value |
| `withCredentials([...]) { }` | the block only | default |

`environment { CRED = credentials('id') }` on a username/password also defines `CRED_USR` and `CRED_PSW`, easy to forget.

```groovy
withCredentials([
    file(credentialsId: 'android-release-keystore', variable: 'KEYSTORE_PATH'),
    string(credentialsId: 'android-keystore-password', variable: 'KEYSTORE_PASSWORD'),
    file(credentialsId: 'firebase-service-account', variable: 'GOOGLE_APPLICATION_CREDENTIALS')
]) {
    sh 'bundle exec fastlane android distribute_qa'
}
```

## Where masking fails

| Pattern | Why |
|---|---|
| `echo $TOKEN \| base64` | encoded form is not the literal value |
| `set -x` around an expanded command | the trace is not guaranteed to match |
| Secret written to a file later `cat`ed or archived | masking covers the console, not artifacts |
| A tool printing its own config on error | the tool decided to print |
| Groovy `"${env.SECRET}"` in `sh` | value baked into the command line, visible in process listings |

Use single-quoted `sh` bodies so the shell expands the variable, keep `set -x` off in secret blocks, never archive a file a secret was written to.

## Rules

- A secret in a `Jenkinsfile`, parameter default or committed script is in git history; removal needs a history rewrite (radius 3, `git-expert`).
- Name credential ids in the pipeline and handoff, never values. A missing id is reported as required, not invented.
- A leaked value is escalated: `security-reviewer` gives the verdict, `cto` owns rotation.
