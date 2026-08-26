# Ví dụ: Enemy AI thỉnh thoảng đứng khựng tại chỗ

Khung `bugfix-debug.md`, giữ `<no_known_cause>` — tái hiện được nhưng chưa có giả thuyết nào đứng vững. Dòng "KHÔNG xảy ra khi" là dữ kiện mạnh nhất, không bỏ trống.

```text
## Objective
Sửa lỗi: enemy loại Goblin thỉnh thoảng đứng yên tại chỗ, không tấn công cũng không
tuần tra, dù người chơi ở trong tầm phát hiện.

## Evidence
- Expected: khi người chơi vào tầm phát hiện 8m, Goblin phải chuyển sang trạng thái
  Chase trong vòng 1 giây — source: GDD_EnemyAI.md, mục 5.1
- Actual:   Goblin đứng yên ở trạng thái Idle vô thời hạn dù người chơi đứng cách 2m
- Frequency: khoảng 1 trên 15 lần chạm trán (tái hiện được nhưng không ổn định)
- Environment: build nội bộ, Windows, Unity 2022.3 LTS, version 0.8.2
- First seen: không rõ — QA báo lại từ đợt playtest tuần trước

<no_known_cause>
Tôi tái hiện được, nhưng không biết vì sao.
- Xảy ra khi: nhiều Goblin cùng phát hiện người chơi gần như đồng thời (2-3 con cùng
  lúc)
- KHÔNG xảy ra khi: chỉ một Goblin duy nhất trong khu vực phát hiện người chơi
- Đã thử và loại trừ: không phải do NavMesh — Goblin bị kẹt vẫn đứng trên NavMesh
  hợp lệ, Gizmo NavMeshAgent không báo lỗi path

Đừng sửa gì ở lượt này. Làm theo thứ tự:
1. Liệt kê các giả thuyết giải thích trọn vẹn triệu chứng, xếp theo khả năng xảy ra.
   Giả thuyết nào không giải thích được dòng "KHÔNG xảy ra khi" thì bị loại — nói rõ
   và bỏ nó.
2. Với từng giả thuyết: phép kiểm rẻ nhất để loại nó, và kết quả nào sẽ chứng minh nó
   SAI.
3. Nêu tên dữ liệu bạn cần mà chưa có sẵn — log ở đâu, đo cái gì.
Rồi chờ tôi đồng ý, chạy các phép kiểm theo thứ tự, báo cáo từng kết quả, và DỪNG
ngay khi nguyên nhân đã được xác định.
Không bao giờ đổi hai thứ cùng lúc: nếu hai thay đổi cùng lúc làm lỗi biến mất, không
cái nào được chứng minh. Nêu mức độ chắc chắn cho mọi kết luận, và không bao giờ
trình bày một giả thuyết như một phát hiện.
</no_known_cause>

## Scope
- Fix the root cause, not the symptom. If only a symptomatic patch is possible, say
  so plainly and name where the real cause lives.
- Do not refactor the surrounding code. Note anything else you find, at the end.
- Tôi nghi ngờ EnemyStateMachine.cs, đoạn nhiều agent cùng giành quyền chuyển state
  trong cùng một frame — xác minh trước khi tin vào đó, và nói tôi biết nếu tôi sai.

## Constraints
- Follow `.claude/rules/client/coding-principles.md`.
- Do not weaken or delete an existing test to make this pass.
- Do not leave debug logging behind: remove it, or gate it behind an editor-only helper.

## Deliverable
1. Nguyên nhân gốc, trong một câu.
2. Diff.
3. Vì sao lỗi này lọt xa đến vậy — test hay phép kiểm nào lẽ ra đã bắt được nó.

## Done when
Làm theo các bước ở trên không còn tái hiện được lỗi, hành vi Idle/Patrol bình
thường vẫn hoạt động, và có một test phủ trường hợp nhiều enemy cùng phát hiện
người chơi trong cùng một frame.
```
