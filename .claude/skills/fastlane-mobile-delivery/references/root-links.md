# Root Links — Fastlane documentation, files and plugins

Source: [fastlane docs](https://docs.fastlane.tools/), [Actions reference](https://docs.fastlane.tools/actions/), [Continuous integration](https://docs.fastlane.tools/best-practices/continuous-integration/).
Covers: SKILL.md §4 — **"Pin the toolchain with `Gemfile` and invoke through `bundle exec fastlane`"**.

Fastlane documents the current release only; there is no version segment in the URLs, and actions gain,
rename and deprecate options between releases. That is precisely why the version is pinned in the project
rather than left to whatever the agent resolves — the documentation describes the newest Fastlane, and the
pinned one is the one that runs.

| Root | Holds | Source |
|---|---|---|
| Documentation home | Setup, lanes, environment variables, best practices | [docs.fastlane.tools](https://docs.fastlane.tools/) |
| Actions reference | Every built-in action and its parameters | [Actions](https://docs.fastlane.tools/actions/) |
| Lanes and advanced usage | `lane`, `platform`, `before_all`, `error`, lane composition | [Advanced](https://docs.fastlane.tools/advanced/lanes/) |
| Continuous integration | Running on CI, keychains, and the common CI failures | [CI best practices](https://docs.fastlane.tools/best-practices/continuous-integration/) |
| App Store Connect API | Key-based authentication for a headless agent | [App Store Connect API](https://docs.fastlane.tools/app-store-connect-api/) |
| Plugins | Installing and pinning third-party actions | [Available plugins](https://docs.fastlane.tools/plugins/available-plugins/) |

## The files a Fastlane setup owns

| File | Holds | Committed |
|---|---|---|
| `fastlane/Fastfile` | Every lane. The reviewable definition of what packaging actually does | Yes |
| `fastlane/Appfile` | `app_identifier`, `apple_id`, `team_id`, `package_name` — identifiers, not secrets | Yes |
| `fastlane/Pluginfile` | Plugin gems, created by `fastlane add_plugin <name>` | Yes |
| `Gemfile` / `Gemfile.lock` | The pinned Fastlane and plugin versions | Yes — the lock file especially |
| `fastlane/report.xml`, `fastlane/README.md` | Generated output | No; ignore them |
| Any keystore, `.p12`, `.p8`, `.mobileprovision`, `.env` with values | Credentials | **Never** — bound by the job, per [ci-keychain-and-credentials.md](ci-keychain-and-credentials.md) |

## Invocation

```bash
bundle install --deployment          # resolves exactly what Gemfile.lock pins
bundle exec fastlane android qa      # platform, then lane
bundle exec fastlane lanes           # lists what this Fastfile defines
bundle exec fastlane env             # versions and environment, for a bug report
```

`bundle exec` is what makes the pinned version the one that runs; a bare `fastlane` call resolves whatever
the agent has installed globally, which is how a pipeline changes behaviour on a week nobody touched it.

## The plugin this project's delivery depends on

| Plugin | Provides | Installed by |
|---|---|---|
| `fastlane-plugin-firebase_app_distribution` | The `firebase_app_distribution` action, used by `firebase-app-distribution` | `fastlane add_plugin firebase_app_distribution`, which writes `fastlane/Pluginfile` |

Plugins are gems and are pinned by `Gemfile.lock` like anything else. A plugin added on one machine and not
committed is a lane that runs there and nowhere else.