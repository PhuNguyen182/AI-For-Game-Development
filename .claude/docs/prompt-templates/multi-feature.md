<!--
 HOW TO USE
 1. Copy the Skeleton block below into your message to Claude Code.
 2. Pick ONE value on the `Mode:` line and keep only that mode's block.
 3. Fill every [bracketed] slot; delete any line whose slot does not apply.
 4. Run the pre-send checklist at the bottom of this file.
 Shared rules for all templates: ./README.md
-->

# Multi-Feature

Khung cho **một lô** tính năng. Nhiều tính năng không phải là một tính năng nhân lên — cái mới xuất hiện là *thứ tự*, *phần dùng chung*, và *thứ vỡ khi một yêu cầu đổi giữa chừng*. Ba thứ đó ứng với ba mode.

Khung này **không triển khai tính năng**. Nó cho ra kế hoạch, hoặc cho ra phần nền dùng chung. Từng tính năng sau đó đi qua `single-feature.md`.

## Khi nào dùng khung này

| Dùng khi | Không dùng khi |
|---|---|
| Bạn có danh sách tính năng cho sprint/milestone | Chỉ một tính năng — dùng `single-feature.md` |
| Nhiều tính năng dường như cần chung một thứ | Chưa biết chúng có chung gì — chạy `Mode: plan-the-batch` trước |
| Một yêu cầu đổi trong lúc nhiều thứ đang dở | Yêu cầu đổi mà chưa có gì đang dở — sửa brief rồi dùng `single-feature.md` |

Đừng dán cả danh sách vào một prompt rồi bảo "làm hết". Đó là cách nhanh nhất để nhận về ba tính năng dựng theo ba kiểu khác nhau.

## Lane và chi phí

| Mode | Lane | Chi phí |
|---|---|---|
| `plan-the-batch` | lập kế hoạch, không code | 1–3 lượt |
| `build-shared-foundation` | trực tiếp hoặc `feature-intake.md` E1 tuỳ phần nền chạm gì | 1–3, hoặc 8+ |
| `absorb-a-change` | `.claude/workflows/change-request.md` | 1–3, rồi tuỳ phân loại |

Sau khi có kế hoạch, mỗi tính năng tốn thêm chi phí riêng của nó theo `single-feature.md`.

## Skeleton

```text
## Objective
[One sentence: what I need out of this round, across the whole batch.]

Mode: [plan-the-batch | build-shared-foundation | absorb-a-change]

## The batch
| # | Feature | One-line intent | Priority |
|---|---------|-----------------|----------|
| 1 | [name]  | [intent]        | [high / med / low] |
| 2 | [name]  | [intent]        | [ ] |
| 3 | [name]  | [intent]        | [ ] |

## Context
- Already shipped and must keep working: [systems]
- Platform / target: [ ]
- Milestone or deadline: [ ]
- Roles available: [ ]

<dependency_map_request>
Mode plan-the-batch. Write no code this round.
1. Triage each feature: tier, and whether it touches `Game.Core.*`, needs more
   than one role, is multiplayer-relevant, or rests on something undecided.
2. Build the dependency graph: what must finish before what, and WHY — a real
   technical dependency, not the order I typed them in.
3. Name anything shared. If several features would each grow their own version of
   the same thing, say so and propose it as separate work.
4. Name the conflicts: two features editing the same file, or two features making
   contradictory assumptions about the same system.
5. Propose an order, with the cost of each step in agent calls.
Return a table: feature | tier | depends on | risk | cost. Then the order and why.
</dependency_map_request>

<shared_foundation>
Mode build-shared-foundation. Build [the shared thing] so the features above stand
on it instead of each growing its own version.
Real consumers today — design for these and no others:
- [feature A] needs: [what]
- [feature B] needs: [what]
Rules:
- Derive the smallest API that covers the real needs above. Do not design for
  consumers that do not exist yet.
- State explicitly what belongs to the foundation and what each feature keeps.
  That boundary matters more than the code itself.
- Consumers depend on an interface, never on a concrete class or a singleton.
- If the project already has a package or skill that solves this, propose using it
  and state the trade-off, instead of writing a new one.
- Say what would have to change if [a plausible third consumer] appears, and what
  that change would cost.
Integrate exactly ONE consumer this round: [feature A]. Leave the others alone.
</shared_foundation>

<in_flight_change>
Mode absorb-a-change. Change no code this round.
The change: [what changes] — from [old behaviour / value] to [new].
Reason: [playtest / balance / feedback / new constraint]
State of each affected feature: [name: shipped | in review | mid-implementation]
Answer four questions:
1. Blast radius — which files, systems and features must change. Separate "must
   change" from "would be nice to change".
2. What depends on the old behaviour and will break — including existing player
   save data, if any.
3. Which documents go stale: Tech Spec, tests, README, config.
4. Is this a detail to fix, or a sign the design is wrong? Say it plainly. Do not
   repackage a design flaw as an ordinary bug to keep it in the routine cycle.
Return a table: item | what must change | risk | owning agent-id. Then one
recommendation — do it now, defer, or redesign. Wait for my approval before acting.
</in_flight_change>

## Scope
- Do not start implementing any feature from the batch this round.
  [Delete this line in build-shared-foundation mode.]
- Do not expand the batch. If something is missing, name it; do not add it.

## Constraints
- Follow `.claude/rules/client/coding-principles.md` and `naming-convention.md`.
- Give cost estimates in agent calls, per step, before anything starts.
- YAGNI outranks generality: a small correct API beats a general wrong one.

## Deliverable
[The table the block above asks for, plus its recommendation.]

## Done when
[I can pick what to do first without guessing, and I know which items still lack
 the information needed to start at all.]
```

## Optional blocks

| Khối | Giữ khi | Xoá khi |
|---|---|---|
| `<dependency_map_request>` | `Mode: plan-the-batch` | Hai mode kia |
| `<shared_foundation>` | `Mode: build-shared-foundation` | Hai mode kia |
| `<in_flight_change>` | `Mode: absorb-a-change` | Hai mode kia |

Đúng một khối được giữ. Giữ hai khối là ra hai câu hỏi trong một prompt và nhận về hai câu trả lời nửa vời.

## Cạm bẫy

- **Danh sách bạn gõ ra theo thứ tự bạn nghĩ ra, không theo thứ tự phụ thuộc.** Chữ "và WHY" ở mục 2 là thứ ép Claude phân biệt hai cái đó thay vì xác nhận lại thứ tự của bạn.
- **Tích hợp cả ba consumer cùng lúc vào phần nền chỉ nhân ba số chỗ phải sửa khi API hoá ra sai.** Consumer thứ nhất là thứ duy nhất chứng minh API dùng được.
- **Thiết kế phần nền cho consumer tưởng tượng là cách tạo ra abstraction không ai gỡ ra được.** Chỉ liệt kê consumer có thật hôm nay.
- **Câu hỏi số 4 trong `<in_flight_change>` là câu đáng tiền nhất.** Một lỗi thiết kế bị hạ cấp thành bug thường sẽ quay lại dưới tên khác, ở tính năng khác, sau vài tuần.
- **Sửa code ngay khi yêu cầu đổi là cách mất bản đồ blast radius.** Dòng "change no code this round" tồn tại để bạn thấy toàn cảnh trước khi trả tiền cho nó.

## Trước khi gửi

- [ ] `Mode:` chỉ còn một giá trị, và chỉ một khối tuỳ chọn còn lại.
- [ ] Bảng `The batch` có ít nhất hai dòng — một dòng thì dùng `single-feature.md`.
- [ ] Mỗi tính năng có `One-line intent`, không chỉ có tên.
- [ ] `Already shipped and must keep working` có nội dung — đây là nguồn xung đột hay bị bỏ sót nhất.
- [ ] Không còn `[` và không còn tag rỗng.

## Sau khi nhận trả lời

- [ ] Đọc cột "depends on" và kiểm tra lý do có phải phụ thuộc kỹ thuật thật không, hay chỉ là thứ tự bạn đã gõ.
- [ ] Nếu có phần dùng chung được đề xuất: quyết định làm nó **trước** hay chấp nhận nợ kỹ thuật, đừng để lửng.
- [ ] Với `absorb-a-change`: nếu câu trả lời số 4 là "thiết kế sai", đưa nó lên GD ngay, đừng gộp vào báo cáo sau.
- [ ] Chuyển từng tính năng đã chốt thứ tự sang `single-feature.md`. Đừng để lô này tự chạy tiếp.
