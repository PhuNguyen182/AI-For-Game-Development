# Ví dụ: Hiểu luồng khởi tạo GameManager

Khung `basic-request.md`, `Task kind: understand`. Không đụng code, chỉ cần câu trả lời — không giữ `<existing_code>` vì Entry point đã đủ rõ, không giữ `<api_contract>` vì đây không phải `write-something-small`.

```text
## Objective
Hiểu GameManager khởi tạo các manager con theo thứ tự nào, trước khi tôi thêm hệ thống save/load.

Task kind: understand

## Context
- Entry point: Assets/Scripts/Core/GameManager.cs
- What I do not know yet: InventoryManager, QuestManager và AudioManager được khởi tạo theo thứ tự nào, và có manager nào đọc dữ liệu của manager khác ngay trong Awake() không.
- Platform / version: Unity 2022.3 LTS, PC

## Scope
- Touch only: (không đụng code — đây là câu hỏi tìm hiểu, chỉ cần đọc)
- Do not touch: mọi file trong dự án
- Find the same problem elsewhere: ghi ra cuối, không tự sửa.

## Constraints
- Tuân `.claude/rules/client/coding-principles.md` và `naming-convention.md`.
- Không đổi hành vi quan sát được.
- Không dùng API nào đã đánh dấu `[Obsolete]`.
- Dừng lại và báo tôi TRƯỚC KHI làm tiếp, nếu việc này hoá ra chạm `Game.Core.*`,
  cần nhiều hơn một vai trò, ảnh hưởng multiplayer, hoặc dựa trên thứ tôi chưa
  quyết. Đừng tự lách qua trong im lặng.

## Deliverable
- Câu trả lời bằng văn xuôi, kèm path:line cho từng bước khởi tạo.
- Mỗi bước một dòng nói vì sao nó đứng ở vị trí đó (phụ thuộc tường minh hay ngầm).
- Danh sách những gì bạn thấy và cố ý không đụng tới.

## Done when
Tôi vẽ lại đúng thứ tự khởi tạo và tên các phụ thuộc ngầm (nếu có) mà không cần mở lại code.
```
