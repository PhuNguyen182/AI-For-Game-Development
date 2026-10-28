# Tech stack — `<Project Name>`

Every package, SDK, service and tool the project depends on. One row each. Update in the same commit that adds, removes or upgrades one. `CLAUDE.md` keeps only the headline.

| Area | Choice | Version | Configured in | Decision | Notes |
|---|---|---|---|---|---|
| Engine | Unity | | `ProjectSettings/ProjectVersion.txt` | | |
| Render pipeline | | | `Assets/Settings/*RPAsset.asset` | | |
| Language | C# | | Unity compiler | | C# 9 on Unity 6.0 |
| Input | | | | | |
| UI | | | | | |
| Tweening | | | | | |
| DI / architecture | | | | | |
| Async | | | | | |
| Serialization / save | | | | | |
| Asset delivery | | | | | |
| Localization | | | | | |
| Networking | | | | | |
| Backend / cloud save | | | | | |
| Remote config / live-ops | | | | | |
| Auth / accounts | | | | | |
| Ads / mediation | | | | | |
| IAP | | | | | |
| Analytics | | | | | |
| Crash reporting | | | | | |
| Push notifications | | | | | |
| Testing | Unity Test Framework | | `Packages/manifest.json` | | |
| CI/CD | | | | | |
| Distribution | | | | | |
| Version control | git + LFS | | `.gitattributes` | | |
| Paid / Asset Store assets | | | | | Licence, seat count |

- **Decision:** ADR path, or the `/decide` / feature file that chose it. Empty = inherited, never decided.
- Delete rows that do not apply; add rows for anything not listed. Never put keys or secrets here — reference where they are stored.
