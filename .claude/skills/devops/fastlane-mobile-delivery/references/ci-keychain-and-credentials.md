# CI Keychain and Credentials — running a lane with nobody logged in

Source: [Continuous integration best practices](https://docs.fastlane.tools/best-practices/continuous-integration/), [setup_ci](https://docs.fastlane.tools/actions/setup_ci/), [Environment variables](https://docs.fastlane.tools/advanced/#environment-variables).
Covers: SKILL.md §4 — **"Keep every lane in `fastlane/Fastfile` and make it run identically on a laptop and on CI"**, **"Take signing material from the job's credential store and stage it in a throwaway keychain"**.

Every difference between a developer's machine and a CI agent that a signing step can trip over, and how a
lane absorbs those differences without becoming two lanes. Most iOS CI failures are one fact: the agent has
no logged-in user, therefore no unlocked login keychain, therefore no signing identity.

## `setup_ci`

| Behaviour | Why it matters |
|---|---|
| Creates a temporary keychain and makes it the default for the run | Signing needs *a* keychain; the agent's login keychain is locked or absent |
| Unlocks it and sets a long timeout | A keychain that re-locks mid-build fails the export with a signing error naming nothing useful |
| No-ops when not running on CI | The same lane still works on a laptop, which is what makes it testable before the job runs |

```ruby
lane :qa do
  setup_ci            # first line of any lane that will sign something
  # …
end
```

The keychain it creates dies with the workspace. That is the property worth having: no certificate is left
installed on a shared agent, and no run inherits state from the one before it.

## What the job binds, and what the lane reads

| Material | Kind | Reaches the lane as | Bound by |
|---|---|---|---|
| Android keystore | Secret **file** | A path in `KEYSTORE_PATH` | `jenkins-pipeline-authoring`'s `file` binding |
| Keystore and key passwords, alias | Secret text | Environment variables | `string` bindings |
| App Store Connect `.p8` key | Secret **file** | A path in `ASC_KEY_PATH` | `file` binding |
| Key id, issuer id | Not secret, but account-specific | Environment variables | Job environment or `Appfile` |
| `MATCH_PASSWORD` | Secret text | Environment variable | `string` binding |
| Match store credentials (git or bucket) | Secret text or SSH key | Environment or an SSH agent | `string` / `sshUserPrivateKey` |
| Firebase service account | Secret **file** | `GOOGLE_APPLICATION_CREDENTIALS` | `file` binding, per `firebase-app-distribution` |

The lane reads `ENV[...]` and never a literal. A lane that hardcodes any of the above works exactly once and
then lives in git history permanently.

## `.env` files

Fastlane loads `fastlane/.env`, `.env.default` and `.env.<environment>`. They are convenient for
**non-secret** configuration — a bundle id, an output directory, a distribution group name. A `.env`
containing a password is a committed secret with extra steps; keep values in the CI credential store and let
the job put them in the environment.

## Making one lane serve both machines

| Difference | Absorb it with |
|---|---|
| No keychain on CI | `setup_ci` |
| No interactive prompts possible | API-key authentication, never Apple ID and password |
| Different absolute paths | Paths relative to the workspace, or environment variables the job sets |
| Certificates present locally, absent on CI | `match(readonly: true)` — the shared store is the single source both read from |
| Different Fastlane versions | `Gemfile.lock` plus `bundle exec`, per [root-links.md](root-links.md) |

`is_ci` exists for the rare genuine difference. Reach for it only after the four rows above are exhausted:
every `if is_ci` branch is a code path that runs in exactly one place and is therefore never tested in the
other.

## Guardrails this file enforces

- No secret is ever written into `Fastfile`, `Appfile`, `.env`, or a script committed beside them.
- No secret is echoed, and `print_command` is disabled on any action whose parameters carry one.
- No artifact archived by the job may contain a keystore, a `.p8`, a `.mobileprovision`, or a decrypted match
  store — the archive is readable by everyone with access to the run.
- A missing credential fails the lane immediately with the id it expected named; it never falls back to a
  debug key, an unsigned build, or an interactive prompt.
