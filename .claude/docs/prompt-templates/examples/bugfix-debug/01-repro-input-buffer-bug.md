# Ví dụ: Lỗi double jump không ghi nhận sau wall dash

Khung `bugfix-debug.md`, giữ `<repro_steps>` — lỗi tái hiện ổn định theo đúng một chuỗi thao tác. Không giữ `<error_log>` vì đây là lỗi hành vi im lặng, không có log nào để dán.

```text
## Objective
Sửa lỗi: cú nhảy đôi (double jump) không được ghi nhận nếu bấm ngay sau khi kết
thúc một pha wall dash.

## Evidence
- Expected: sau khi wall dash kết thúc, người chơi bấm Space trong vòng 0.3s sau đó
  phải nhảy đôi được — source: GDD_Movement.md, mục 2.3 "Double Jump"
- Actual:   bấm Space trong khoảng 0.15s ngay sau khi wall dash kết thúc thì nhân
  vật không nhảy, animation Idle vẫn chạy tiếp
- Frequency: 8 trên 10 lần thử
- Environment: Editor, Windows, Unity 2022.3 LTS, build commit a3f9c21
- First seen: sau khi thêm wall dash tuần trước, ngày 18/08/2026

<repro_steps>
From a known starting state: scene Level02, đứng cạnh tường có thể wall dash
1. Chạy tới tường, bấm Shift để wall dash
2. Ngay khi animation wall dash kết thúc (khoảng 0.4s), bấm Space trong vòng 0.15s
3. Quan sát nhân vật không nhảy, input Space bị bỏ qua
Following these steps reproduces it every time.
</repro_steps>

## Scope
- Fix the root cause, not the symptom. If only a symptomatic patch is possible, say
  so plainly and name where the real cause lives.
- Do not refactor the surrounding code. Note anything else you find, at the end.
- Tôi nghi ngờ PlayerMovementController.cs, đoạn khoá input trong lúc chạy animation
  wall dash — xác minh trước khi tin vào đó, và nói tôi biết nếu tôi sai.

## Constraints
- Follow `.claude/rules/client/coding-principles.md`.
- Do not weaken or delete an existing test to make this pass.
- Do not leave debug logging behind: remove it, or gate it behind an editor-only helper.

## Deliverable
1. Nguyên nhân gốc, trong một câu.
2. Diff.
3. Vì sao lỗi này lọt xa đến vậy — test hay phép kiểm nào lẽ ra đã bắt được nó.

## Done when
Làm theo các bước ở trên không còn tái hiện được lỗi, nhảy đơn bình thường vẫn hoạt
động, và có một test Play Mode phủ trường hợp bấm Space ngay sau khi wall dash kết
thúc.
```
