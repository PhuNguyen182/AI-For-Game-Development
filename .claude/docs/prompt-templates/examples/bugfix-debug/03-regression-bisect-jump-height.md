# Ví dụ: Độ cao nhảy giảm bất thường sau một commit

Khung `bugfix-debug.md`, giữ `<regression_bisect>` — có mốc "trước đây đúng" và mốc "giờ sai". Khối `<git_status>` bên trong luôn giữ khi dùng khối này.

```text
## Objective
Sửa lỗi: độ cao nhảy của nhân vật thấp hơn hẳn so với trước, ảnh hưởng tới các đoạn
platforming đã thiết kế sẵn.

## Evidence
- Expected: nhảy đơn đạt độ cao 2.2m như config JumpHeight trong PlayerMovementConfig
  — source: SO_PlayerMovementConfig.asset, field jumpHeight
- Actual:   nhảy đơn chỉ đạt khoảng 1.5m, đo bằng thước debug trong Scene view
- Frequency: 10 trên 10 lần thử — luôn thấp hơn
- Environment: build nội bộ, Windows, Unity 2022.3 LTS
- First seen: build hôm nay (23/08/2026); build hôm qua (22/08/2026) vẫn đúng 2.2m

<regression_bisect>
Trước đây cái này chạy tốt.
- Last known good: tag build-0822
- Known bad: HEAD (nhánh develop)
- Branch: develop
Phép kiểm tốt/xấu — phải là phép kiểm có/không, không phải phán đoán chủ quan:
mở scene TestJump, bấm Play, bấm Space một lần, đọc giá trị "Max height reached"
trên debug text — PASS nếu đọc ≥ 2.15m, FAIL nếu dưới 2.15m

<git_status>
On branch develop
Your branch is up to date with 'origin/develop'.
nothing to commit, working tree clean
</git_status>

- Tạo một mốc an toàn TRƯỚC KHI đụng vào bất cứ thứ gì.
- Không push, không force, không viết lại lịch sử đã publish.
- Hỏi tôi trước bất kỳ lệnh nào có thể làm mất việc.
- Đây là repo Unity: thủ phạm có thể là một file .meta hoặc một scene/prefab YAML,
  không chỉ file .cs — ví dụ giá trị Rigidbody Mass hoặc Gravity Scale trong prefab
  Player.prefab.
Trả về commit thủ phạm, phần diff của nó thật sự gây ra lỗi này, cơ chế nó gây ra
như thế nào, và các lệnh chính xác bạn đã chạy để tôi lặp lại được.
</regression_bisect>

## Scope
- Fix the root cause, not the symptom. If only a symptomatic patch is possible, say
  so plainly and name where the real cause lives.
- Do not refactor the surrounding code. Note anything else you find, at the end.
- Tôi nghi ngờ commit đổi Physics settings hoặc Player.prefab trong hai ngày qua —
  xác minh trước khi tin vào đó, và nói tôi biết nếu tôi sai.

## Constraints
- Follow `.claude/rules/client/coding-principles.md`.
- Do not weaken or delete an existing test to make this pass.
- Do not leave debug logging behind: remove it, or gate it behind an editor-only helper.

## Deliverable
1. Nguyên nhân gốc, trong một câu.
2. Diff.
3. Vì sao lỗi này lọt xa đến vậy — test hay phép kiểm nào lẽ ra đã bắt được nó.

## Done when
Phép kiểm có/không ở trên trả về PASS (≥ 2.15m) trên HEAD, di chuyển ngang vẫn hoạt
động bình thường, và có một test phủ chiều cao nhảy tối thiểu.
```
