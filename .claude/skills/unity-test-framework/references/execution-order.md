# Execution order and domain reloads

Order around one test (manual page `reference-actions-outside-tests.html`):
1. NUnit context-applying attributes
2. Outer Unity test action, before
3. Unity setup (`UnitySetUp`)
4. NUnit setup/teardown wrappers
5. NUnit `SetUp`
6. NUnit action attributes, before
7. NUnit test-method wrappers
8. Test method
9. NUnit action attributes, after
10. NUnit `TearDown`
11. Unity teardown
12. Outer Unity test action, after

- Unity setup runs before NUnit setup: NUnit setup cannot depend on state Unity setup establishes after it.
- NUnit setup runs base to derived, teardown derived to base.
- Outer actions are outermost: put entering/leaving Play Mode around a whole test there.

## Domain reload
| Hook | After a reload |
|---|---|
| NUnit setup / one-time setup | Re-runs before the triggering code continues |
| Unity setup | Does not re-run; if it triggered the reload, only code after its yield continues |

State set before the yield in a Unity setup is lost and not rebuilt, while the NUnit setup beside it runs again. A half-initialised fixture is this, not a race.

## Build-time hooks
- `PrebuildSetup`: runs before the test Player is built — the only place to stage assets/files a Player run needs.
- `PostBuildCleanup`: runs after the build; removes staged assets so they are not committed or shipped.
- Both attach per test or per fixture; limit expensive staging to tests that need it.
