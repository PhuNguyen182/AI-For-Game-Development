# Ví dụ: Viết một component hiển thị cooldown nhỏ

Khung `basic-request.md`, `Task kind: write-something-small`. Giữ `<api_contract>` để chốt public API trước — component này CHỈ hiển thị giá trị được truyền vào, luật cooldown vẫn ở `Game.Core.*`.

```text
## Objective
Có một component UI nhỏ hiển thị số giây hồi chiêu còn lại trên icon skill, nhận giá trị đã tính sẵn từ Shared Core.

Task kind: write-something-small

## Context
- Entry point: Assets/Scripts/Client/UI/HUD/ (namespace Game.Client.UI, file chưa tồn tại)
- Platform / version: Unity 2022.3 LTS, mobile + PC

## Scope
- Touch only: một file mới SkillCooldownLabel.cs trong Assets/Scripts/Client/UI/HUD/
- Do not touch: SkillIconView.cs hiện có, logic tính cooldown trong Game.Core
- Find the same problem elsewhere: ghi ra cuối, không tự sửa.

## Constraints
- Tuân `.claude/rules/client/coding-principles.md` và `naming-convention.md`.
- Không dùng API nào đã đánh dấu `[Obsolete]`.
- Dừng lại và báo tôi TRƯỚC KHI làm tiếp, nếu việc này hoá ra chạm `Game.Core.*`,
  cần nhiều hơn một vai trò, ảnh hưởng multiplayer, hoặc dựa trên thứ tôi chưa
  quyết. Đừng tự lách qua trong im lặng.

<api_contract>
- void SetRemaining(float secondsRemaining, float totalCooldown) — cập nhật text và fill amount của icon
- event Action OnCooldownFinished — bắn đúng một lần khi secondsRemaining chạm 0
Không thêm bất cứ thứ gì ngoài danh sách này — component KHÔNG tự tính cooldown, chỉ hiển thị giá trị được truyền vào.
</api_contract>

## Deliverable
- Diff.
- Mỗi file một dòng nói vì sao nó bị đụng.
- Danh sách những gì bạn thấy và cố ý không đụng tới.

## Done when
Gọi SetRemaining(3f, 5f) trong Play Mode làm text hiện "3" và fill amount đọc 0.6; OnCooldownFinished bắn đúng một lần khi giá trị chạm 0.
```
