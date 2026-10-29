# Third-Party and Engine Escalation

Sources: [a] distribute/sdk-index, [b] issuetracker.unity3d.com — from the SKILL.md `Docs:` roots. Acting on these belongs to `technical-architect` or `sdk-platform-engineer`.

## Unity engine ladder [b]

| Rung | Establishes |
|---|---|
| 1. Search forums and issue tracker | Whether known, and in which stream/version fixed |
| 2. Upgrade to the fixed version | Resolution in most engine cases; `technical-architect` decides, as an upgrade moves every subsystem |
| 3. Report a bug | Only if 1-2 produce nothing; attach symbolicated trace and smallest reproduction |

Before starting: confirm the frames below are not game code supplying bad state (see [fault-domain-signals.md](fault-domain-signals.md)); look for an interim path (different API, ordering change).

**Caveat:** an engine upgrade is a proposal to `technical-architect`, not a fix this pipeline applies.

## Third-party SDK [a]

| Step | Establishes |
|---|---|
| Update to current | Already fixed? Often immediate; the vendor asks first |
| Disable and observe | Signature gone = confirmed; matching frame alone = correlation |
| Check the store SDK index | Version flagged, or a policy deadline that raises priority |
| Contact vendor with all three results | A bare "it crashes" gets a request for exactly these |
| Decide whether to ship without it | Commercial decision: `sdk-platform-engineer` |

## Cost of each path

| Path | Time to fix | Report note |
|---|---|---|
| Engine version bump | A release cycle plus regression across systems | State the version; not a small change |
| Engine bug report | Indefinite; may land in a stream not in use | Pair with an interim recommendation |
| SDK update | Often immediate | Closes after verification on a new build |
| SDK vendor contact | Vendor-dependent, often slow | Say so, so routed is not read as resolved |
