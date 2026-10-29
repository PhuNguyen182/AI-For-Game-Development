# CI Keychain and Credentials

Sources: [ci] `best-practices/continuous-integration/`, [s] `actions/setup_ci/`, under the `Docs:` base.

An agent has no logged-in user, so no unlocked login keychain and no signing identity; most iOS CI failures are that one fact.

## `setup_ci` [s]

- Creates a temporary keychain, makes it the default, unlocks it with a long timeout (a keychain that re-locks mid-build fails the export with an unhelpful signing error).
- No-ops off CI, so the same lane runs on a laptop.
- The keychain dies with the workspace: no certificate stays on a shared agent.
- Put it first in any lane that signs.

## What the job binds

| Material | Kind | Reaches the lane as | Bound by |
|---|---|---|---|
| Android keystore | Secret file | Path in `KEYSTORE_PATH` | `file` binding |
| Keystore/key passwords, alias | Secret text | Env vars | `string` bindings |
| App Store Connect `.p8` | Secret file | Path in `ASC_KEY_PATH` | `file` binding |
| Key id, issuer id | Not secret, account-specific | Env vars | Job environment or `Appfile` |
| `MATCH_PASSWORD` | Secret text | Env var | `string` binding |
| Match store credentials | Secret text or SSH key | Env or SSH agent | `string` / `sshUserPrivateKey` |
| Firebase service account | Secret file | `GOOGLE_APPLICATION_CREDENTIALS` | `file` binding (`firebase-app-distribution`) |

Bindings are `jenkins-pipeline-authoring`'s. The lane reads `ENV[...]`, never a literal.

## Rules

- Fastlane loads `fastlane/.env`, `.env.default`, `.env.<environment>`: non-secret config only (bundle id, output dir, group name).
- No secret in `Fastfile`, `Appfile`, `.env` or a committed script; none echoed; `print_command` off on any action whose parameters carry one.
- No archived artifact may contain a keystore, `.p8`, `.mobileprovision` or decrypted match store.
- A missing credential fails the lane at once, naming the expected id; never fall back to a debug key, an unsigned build or a prompt.

## One lane for both machines

| Difference | Absorb with |
|---|---|
| No keychain on CI | `setup_ci` |
| No interactive prompts | API-key auth, never Apple ID |
| Different absolute paths | Workspace-relative paths or job-set env vars |
| Certificates local-only | `match(readonly: true)`; the store is the single source |
| Fastlane versions | `Gemfile.lock` + `bundle exec` |

`is_ci` only for a genuine remaining difference: each branch runs in one place and is untested in the other.
