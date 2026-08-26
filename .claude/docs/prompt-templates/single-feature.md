<!--
 HOW TO USE
 1. Copy the Skeleton block below into your message to Claude Code.
 2. Fill every [bracketed] slot; delete any line whose slot does not apply.
 3. Keep or delete each <optional_block> WHOLE, tags included. <escalation_check>
    is the one block you never delete.
 4. Run the pre-send checklist at the bottom of this file.
 Shared rules for all templates: ./README.md
-->

# Single Feature

Khung cho **một** tính năng, ở mọi quy mô. Không có khung riêng cho "tính năng multiplayer" hay "tính năng có ngân sách hiệu năng" — những thứ đó là khối tuỳ chọn trong chính khung này. Tính năng vừa chạm luật chơi, vừa đồng bộ mạng, vừa có budget: giữ ba khối, vẫn một khung.

## Khi nào dùng khung này

| Dùng khi | Không dùng khi |
|---|---|
| Bạn thêm đúng một tính năng | Nhiều tính năng cùng lúc — dùng `multi-feature.md` |
| Bạn đã biết mình muốn hành vi gì | Còn đang thử xem có vui không — dùng `prototype.md` |
| Yêu cầu nằm trong đầu bạn hoặc trong một brief ngắn | Yêu cầu nằm trong GDD/spec dài — dùng `from-documents.md` |
| Tính năng chưa tồn tại | Tính năng đã có và đang sai — dùng `bugfix-debug.md` |

## Lane và chi phí

Khối `<escalation_check>` quyết định lane, không phải bạn đoán trước:

- **Không tiêu chí nào áp dụng** → lane trực tiếp, 0–1 lượt agent.
- **Có bất kỳ tiêu chí nào** → `.claude/workflows/feature-intake.md` E1, 8+ lượt, có Triage và checkpoint.

Đó là lý do khối này không bao giờ bị xoá: nó biến việc chọn lane thành một câu trả lời một dòng thay vì một giả định im lặng.

## Skeleton

```text
## Objective
[One sentence: what the player or developer can do that they could not before,
 and why the feature exists.]

## Context
- Where it lives: [scene / folder / namespace]
- Existing systems it must work with: [name them]
- Already available to reuse: [component, service, package, skill]

<escalation_check>
Answer each of these in one line BEFORE writing any code, then wait if any is yes:
- Does this touch `Game.Core.*` — a game rule, economy, state machine, cooldown?
- Does it need more than one role?
- Is it multiplayer-relevant?
- Does it rest on something I have not decided yet?
No to all four: build it directly.
Yes to any: say which, state the cost in agent calls, and wait for my go.
</escalation_check>

## Behaviour
- [Behaviour — with the number and unit, never an adjective]
- [Behaviour]
- Edge case: when [condition], the result is [outcome]
- Forbidden: [what must never happen]

<game_rules>
These decide an outcome, so they live in `Game.Core.*` and are written once:
- [rule — value, unit, condition]
- [rule]
Constraints on that code:
- No `UnityEngine` types. No `UnityEngine.Random` — inject a seeded RNG. No
  wall-clock time. No float operation that can diverge across platforms.
- The Client layer calls into it and never reimplements it.
- Unity-dependent data is resolved in the Client layer and passed in already resolved.
</game_rules>

<authority_and_sync>
- Client may predict: [what]
- Server must validate: [what]
- Client is never the source of truth for: [what]
- Must hold under: [latency ms], [packet loss %], tick rate [value | not decided]
- Rules are written once in `Game.Core.*`. The server WRAPS and validates them and
  never reimplements them. If you find yourself copying logic to the server side,
  stop and tell me.
- Agree the client-server contract with me FIRST — message shape, ordering, what is
  authoritative, what reconciles — before writing the implementation.
</authority_and_sync>

<performance_budget>
- Budget: [number + unit] on [device / platform], measured in [scene / scenario]
- Hot path: no per-frame allocation, no LINQ, no `GetComponent` inside `Update`,
  no `Find`/`FindObjectOfType` at runtime.
- Any performance claim ships with a before/after measurement and its run-to-run
  spread. An Editor measurement is labelled indicative and never stands in for a
  device measurement.
</performance_budget>

<platform_matrix>
- Must work on: [platform A], [platform B]
- Differs by platform: [input scheme, aspect ratio, quality tier — name it]
- Keep platform branches behind one abstraction, not `#if` scattered through gameplay.
</platform_matrix>

## Scope
- Build only what is listed under Behaviour.
- Do not add hooks, config options, or extension points I have not asked for.
- Do not refactor surrounding code. List what you would change, separately.
- Out of scope this round: [what I do NOT want built now]

## Constraints
- Follow `.claude/rules/client/coding-principles.md`, `naming-convention.md`,
  and `performance-and-algorithms.md`.
- Do not introduce any API marked `[Obsolete]`.
- Undecided — ask me, do not settle it yourself: [list | none]

<process_gates>
- Triage first. State the tier you assign and why.
- State the cost in agent calls before starting.
- Stop at each checkpoint for my approval. Do not run straight through to code.
- State every assumption you made where my brief was silent.
</process_gates>

## Deliverable
- Code, plus an Implementation Note per `.claude/rules/implementation-note.md`:
  which clauses it satisfies, files changed, assumptions, known limitations, what
  you deliberately left alone, and what you actually verified versus did not.

## Done when
[A concrete scenario: doing X produces Y, observed how.]
[Kept a performance_budget block? Add: and the budget still holds, measured the
 same way, on the same device.]
```

## Optional blocks

| Khối | Giữ khi | Xoá khi |
|---|---|---|
| `<escalation_check>` | **Luôn luôn** | Không bao giờ |
| `<game_rules>` | Tính năng có luật quyết định kết quả: sát thương, kinh tế, cooldown, state machine | Tính năng thuần hiển thị, tiện ích, hoặc tooling |
| `<authority_and_sync>` | Client và server đều phải đồng ý về kết quả | Game một người, hoặc phần này hoàn toàn cục bộ |
| `<performance_budget>` | Có ngân sách cụ thể, hoặc code chạy mỗi frame / theo số lượng entity | Chạy một lần, hoặc chỉ phản ứng theo sự kiện người dùng |
| `<platform_matrix>` | Hành vi khác nhau giữa các nền tảng | Một nền tảng, hoặc khác biệt không đáng kể |
| `<process_gates>` | `<escalation_check>` cho ra "yes" ở bất kỳ tiêu chí nào | Cả bốn tiêu chí đều "no" |

Giữ `<process_gates>` khi lane là trực tiếp là tự trả giá pipeline cho việc không cần. Xoá nó khi lane là pipeline là bỏ mất checkpoint — Claude sẽ chạy một mạch tới code.

## Cạm bẫy

- **Hành vi viết bằng tính từ thì không triển khai được.** "Đòn đánh nặng tay" không phải hành vi; "gây 40 sát thương, giật lùi 2m, hồi chiêu 1.5s" mới là. Chỗ bạn viết tính từ là chỗ Claude sẽ tự chọn con số.
- **Xoá `<authority_and_sync>` vì "sau này mới làm multiplayer" là cách luật chơi bị viết hai lần.** Nếu chế độ nhiều người có trong kế hoạch, giữ khối này ngay cả khi chưa nối mạng — nó ép luật nằm đúng chỗ ngay từ đầu.
- **Không có `Out of scope` thì mọi thứ đều trong phạm vi.** Đây là dòng ngăn một tính năng nở ra gấp đôi trong lúc đang code.
- **`Undecided` bỏ trống được đọc là "không có gì chưa quyết".** Viết ra thì Claude hỏi; bỏ trống thì Claude tự chốt và bạn phát hiện ở lượt review.
- **Ngân sách không có điều kiện đo thì không nghiệm thu được.** "60fps" là một con số; "60fps trên Redmi Note 11 ở scene Arena với 20 enemy" mới là một tiêu chí.

## Trước khi gửi

- [ ] `<escalation_check>` còn nguyên trong prompt.
- [ ] Mọi dòng `Behaviour` có con số và đơn vị, không có tính từ.
- [ ] Đúng những khối tuỳ chọn áp dụng được giữ, các khối khác đã xoá trọn tag.
- [ ] `<process_gates>` khớp với kết quả bạn dự đoán của `<escalation_check>`.
- [ ] `Out of scope` và `Undecided` đều có nội dung, hoặc ghi rõ "none".
- [ ] `Done when` là một kịch bản, không phải một trạng thái.

## Sau khi nhận trả lời

- [ ] Đọc trả lời của `<escalation_check>` **trước tiên**. Nếu nó nói "yes" mà bạn đã xoá `<process_gates>`, dừng lại và gửi lại có khối đó.
- [ ] Đối chiếu Implementation Note: mục `Assumptions` là chỗ giá trị nhất — mỗi giả định ở đó là một quyết định bạn chưa duyệt.
- [ ] Nếu có `<game_rules>`: kiểm tra luật thật sự nằm trong `Game.Core.*` và không tham chiếu `UnityEngine`.
- [ ] Nếu có `<performance_budget>`: đòi số đo trước/sau kèm độ dao động. Một khẳng định "đã tối ưu" không có số là chưa xác minh.
- [ ] Chạy đúng kịch bản `Done when`.
