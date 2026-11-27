# Workflow map

Snapshot of `.claude/` (rules, skills, hooks). The rules and skills are the source of truth; this file is a picture of them.

Legend: diamond = decision, `GD` = the main GD decides, `[agent]` = who does the step.

## 1. Project lifecycle

```mermaid
flowchart LR
    NP["/new-project"] --> PG["/plan-game"]
    PG --> BL[("Backlog")]
    BL --> FT["/feature per item"]
    FT -->|"next item"| BL
    FT -->|"milestone exit"| PR["/product-review"]
    PR -->|"accepted findings"| BL
    FT --> REL["/release"]
    DS["/design"] --> PG
    MN["/monet"] --> PG
    DS --> FT
    MN --> FT
    DC["/decide"] --> FT
    FX["/fix"] --> REL
    REL -->|"failed row"| FX
```

## 2. Input routing (first match wins)

```mermaid
flowchart TD
    IN(["Input from main GD"]) --> Q{"What work is asked?"}
    Q -->|"question"| A1["Answer or one read-only agent"]
    Q -->|"git task"| A2["git-expert"]
    Q -->|"CI/CD, failed run"| A3["ci-cd-engineer"]
    Q -->|"production crash or ANR"| A4["crash-anr-investigator"] --> FIX["/fix"]
    Q -->|"bug"| FIX
    Q -->|"audit existing code"| RV["/review"]
    Q -->|"tests or evidence"| QA["/qa"]
    Q -->|"technology or vendor"| DC["/decide"]
    Q -->|"new project, backlog, release"| A5["/new-project, /plan-game, /release"]
    Q -->|"design direction open"| DS["/design"]
    Q -->|"monetization direction open"| MN["/monet"]
    Q -->|"product health, milestone exit"| PR["/product-review"]
    Q -->|"change to open feature"| CR["/feature change request"]
    Q -->|"anything else"| SZ{"Size it"}
    SZ -->|"S: one role, no new contract"| S["Direct or one agent; reply closes it"]
    SZ -->|"M or L"| FT["/feature"]
    S -->|"turns out bigger"| FT
```

## 3. /feature

```mermaid
flowchart TD
    O["Step 0: Open: slug, record, feature file"] --> SZ["Step 1: Size and risk flag [technical-architect]"]
    SZ -->|"S"| DONE_S(["Do directly, close record"])
    SZ -->|"M or L"| CP1Q{"CP1 on for this profile and direction open?"}
    CP1Q -->|"yes"| CP1["Step 2: CP1: researcher options, GD picks, critic attacks, GD locks"]
    CP1Q -->|"no"| SPEC
    CP1 --> SPEC["Step 3: Spec or acceptance criteria [technical-architect]"]
    SPEC --> ADV["Adviser notes: product, design, monetization (non-blocking)"]
    ADV --> CP2{"CP2: GD approves?"}
    CP2 -->|"revise"| SPEC
    CP2 -->|"rethink direction"| CP1
    CP2 -->|"approve"| BR["Step 4: git-expert: branch feature/slug"]

    BR --> BUILD["Next implementer in the chain (code + tests)"]
    BUILD --> CHK{"Compile check and tests pass?"}
    CHK -->|"no: next attempt"| BUILD
    CHK -->|"yes"| COMMIT["Local commit, never push"]
    COMMIT -->|"more roles"| BUILD
    COMMIT -->|"all done"| GATE{"Step 5: GD: review? QA?"}

    GATE -->|"review yes"| REV["/review"]
    GATE -->|"review no"| L1["Limitation: not reviewed"]
    REV -->|"request changes"| BUILD
    REV -->|"pass"| CP3Q
    L1 --> CP3Q{"Size L?"}
    CP3Q -->|"yes"| CP3{"Step 6: CP3: built vs spec"}
    CP3 -->|"drift"| BUILD
    CP3 -->|"approve"| QAQ
    CP3Q -->|"no"| QAQ{"Step 7: QA chosen?"}
    QAQ -->|"yes"| QA["/qa"]
    QA -->|"defects"| FIX["/fix"]
    FIX --> QA
    QA --> CP4
    QAQ -->|"no: limitation not QA'd"| CP4{"Step 8: CP4: closure"}
    CP4 -->|"fix gaps"| BUILD
    CP4 -->|"close or accept gaps"| CLOSE["Closed: records, debt, closure commit"]
    CLOSE --> MERGE{"GD: merge into base?"}
    MERGE --> NEXT(["Offer next backlog item"])
```

Implementer chain (unused roles are skipped; `sdk-platform-engineer` takes any slot):

```mermaid
flowchart LR
    C["csharp-engineer"] --> N["netcode-engineer or backend-engineer"] --> TA["technical-artist"] --> G["gameplay-engineer"] --> U["ui-engineer"] --> P["unity-performance-engineer (budget at risk)"]
```

Lanes build mode (only when chosen at CP2):

```mermaid
flowchart LR
    ST["csharp-engineer: stubs, commit"] --> LA["Lane A: worktrees, no Editor, dotnet test"]
    ST --> LB["Lane B: main checkout, Editor"]
    LA --> M["git-expert merges once, Editor closed"]
    LB --> M
    M --> V["Reopen, compile, Edit Mode tests"]
```

## 4. /fix

```mermaid
flowchart TD
    R["Step 1: Record: search, then BUG-####"] --> RP{"Step 2: Reproduces?"}
    RP -->|"no"| ASK{"GD: more info, keep open, won't fix"}
    RP -->|"yes"| RC["Step 3: Root cause [owner agent]"]
    RC -->|"spec is wrong"| GD(["Design flaw: tell main GD"])
    RC --> RT["Step 4: Failing regression test [qa-automation-engineer]"]
    RT --> FX["Step 5: Fix [owner]"]
    FX --> CK{"Compile and regression test pass?"}
    CK -->|"no: next attempt"| FX
    CK -->|"yes"| RES["Step 6: Resolved (offer /review if risk flag or Core)"]
    RES --> VQ{"Verification run?"}
    VQ -->|"Repro: gone"| CMP(["Complete"])
    VQ -->|"Repro: reproduces"| RO["Reopen: +1 fix round"]
    RO --> RC
    VQ -->|"GD accepts unverified"| ACC(["Accepted, mirrored to debt"])
```

## 5. /review and /qa

```mermaid
flowchart TD
    SC["Scope: working tree vs base"] --> TP{"Third-party content?"}
    TP -->|"yes"| SR0["security-reviewer clears it first"] --> PAR
    TP -->|"no"| PAR["Parallel, read-only (large diff: review-gate workflow)"]
    PAR --> CR["code-reviewer"]
    PAR --> SR["security-reviewer"]
    CR --> MG{"Approve and Clear?"}
    SR --> MG
    MG -->|"yes"| OK(["Pass"])
    MG -->|"no: +1 round, cap 3"| AU["Back to author"] --> SC
```

```mermaid
flowchart TD
    PL["qa-lead: plan"] --> A["qa-automation-engineer"]
    A --> B["playtest-tester"]
    B --> C["performance-qa-engineer"]
    C --> D["build-release-engineer: device"]
    D --> DEF["File defects to /fix, record gaps"]
    DEF --> SO{"qa-lead: sign off?"}
    SO -->|"yes"| REP(["Report per acceptance criterion"])
    SO -->|"no: +1 round, cap 2"| GAP["Fix gaps, re-run affected cases"] --> SO
```

Only the agents named in the plan run, one at a time.

## 6. Direction workflows

### /design

```mermaid
flowchart LR
    F["game-designer: frame"] --> P["researcher: precedents"] --> K{"GD picks"}
    K --> D["game-designer: draft"] --> AT["critic (+ monetization-designer)"] --> L{"GD: lock?"}
    L -->|"revise"| D
    L -->|"pick again"| K
    L -->|"lock"| W["Write GDD"] --> H(["/plan-game or /feature"])
```

### /monet

```mermaid
flowchart LR
    B["monetization-designer: baseline, candidates"] --> S["simulate.py"] --> PE["game-designer: player effect"] --> LN{"GD leans"}
    LN -->|"reject all"| X(["Stop"])
    LN -->|"one candidate"| AT["critic"] --> L{"GD: lock?"}
    L -->|"pick again"| LN
    L -->|"stop"| X
    L -->|"lock"| W["docs/monetization-plan.md"] --> H(["/feature or remote config"])
```

### /decide

```mermaid
flowchart LR
    R["researcher"] --> SP{"Spike needed?"}
    SP -->|"yes"| RD["rd-engineer"] --> C
    SP -->|"no"| C["cto decides"]
    C -->|"product consequence"| GD{"GD chooses"}
    C --> REC["docs/tech-stack.md, decisions, ADR if standard"]
    GD --> REC
```

### /product-review

```mermaid
flowchart LR
    PREP["Prepare inputs, playtest evidence"] --> PO["product-owner"]
    PREP --> GD["game-designer"]
    PREP --> MD["monetization-designer"]
    PO --> M["Merge, conflicts kept"]
    GD --> M
    MD --> M
    M --> D{"GD: what enters backlog"}
    D --> BL(["technical-architect sizes, backlog rows"])
```

## 7. /plan-game and /new-project

```mermaid
flowchart LR
    subgraph NEW["/new-project"]
        direction LR
        N1["Identity questions"] --> N2["Project, packages, Shared asmdefs"] --> N3["git + LFS, perf budget, .workflow"] --> N4["CI if wanted, report, bootstrap commit"]
    end
    subgraph PLAN["/plan-game"]
        direction LR
        P1["Read GDD"] --> P2["Milestones"] --> P3["technical-architect: features, sizes"] --> P4["product-owner: order"] --> P5["Backlog"] --> P6{"GD approves"}
    end
    NEW --> PLAN
```

## 8. /release

```mermaid
flowchart TD
    P["Content committed, unchecked work listed, no High bugs"] --> V["Version bump"]
    V --> SER["Serial: build, smoke, performance, size, analytics + IAP, save migration"]
    V --> PAR["Parallel: store checklist, signing, secret scan"]
    SER --> CL["Changelog"]
    PAR --> CL
    CL --> F{"GD: tag and push?"}
    F -->|"fix failures: cap 2 rounds"| RE["Fix, re-run failed rows"] --> F
    F -->|"tag + push"| T(["Tagged; store upload is a separate order"])
    F -->|"stop"| S(["Stop"])
```

## 9. Stop rule

```mermaid
flowchart TD
    X["Attempt budget used up (S 2, M 3, L 4), same failure twice, or round cap hit"] --> TA["technical-architect root-causes once"]
    TA --> ONE["Owner gets one more dispatch"]
    ONE -->|"passes"| GO(["Continue"])
    ONE -->|"fails"| STOP(["Stop, report to main GD"])
    INF["Return says Infeasible"] --> CONF["technical-architect confirms"] --> CH{"GD: drop, waive or redirect"}
```

Round caps: review 3 · QA sign-off 2 · bug fix 2 · bug review 3 · feature rework M 6, L 8.

## 10. Hooks (run automatically)

```mermaid
flowchart LR
    subgraph START["SessionStart"]
        H1["session-start: memory, bugs, records"]
    end
    subgraph PRE["Before a tool call"]
        H2["secret-scan: file edits"]
        H3["editor-lock: Editor, Unity, project folders"]
        H4["pre-commit, pre-push, git-guard"]
        H5["search-guard: prefer XERJ"]
        H6["round-cap: Agent and Workflow dispatch"]
        H7["log-triage-scan: handback"]
    end
    subgraph POST["After a tool call"]
        H8["verify-on-edit: .claude changes"]
        H9["package-changed: supply-chain reminder"]
        H10["round-cap: records and bug edits"]
    end
    subgraph END_["Agent or session end"]
        H11["SubagentStop: lock release, round count, advisory capture, log-triage scan"]
        H12["Stop, SessionEnd: lock clear, memory capture"]
    end
    START --> PRE --> POST --> END_
```
