# Ví dụ: Slider độ nhạy chuột trong màn Settings

Khung `single-feature.md`. Minh hoạ trường hợp `<escalation_check>` dự đoán trả lời "không" cho cả bốn tiêu chí — không giữ `<game_rules>`, `<authority_and_sync>`, `<performance_budget>`, `<platform_matrix>`, `<process_gates>` vì không tiêu chí nào áp dụng.

```text
## Objective
Người chơi chỉnh được độ nhạy chuột trong màn Settings, giá trị được lưu lại và áp dụng ngay không cần khởi động lại game.

## Context
- Where it lives: Assets/Scripts/Client/UI/Settings/
- Existing systems it must work with: SettingsPanel.cs (panel Settings đã có), CameraLookController.cs (đọc độ nhạy hiện tại)
- Already available to reuse: SO_PlayerPrefsKeys (ScriptableObject chứa các key PlayerPrefs đã dùng)

<escalation_check>
Trả lời từng câu dưới đây bằng một dòng TRƯỚC KHI viết bất kỳ dòng code nào, và
dừng lại chờ tôi nếu có bất kỳ câu nào là "có":
- Việc này có chạm `Game.Core.*` — một luật chơi, kinh tế, state machine, cooldown?
- Nó có cần nhiều hơn một vai trò?
- Nó có liên quan multiplayer?
- Nó có dựa trên thứ tôi chưa quyết?
Không cho cả bốn: làm trực tiếp.
Có ở bất kỳ câu nào: nói rõ câu nào, nêu chi phí tính theo số lượt gọi agent, và
chờ tôi đồng ý.
</escalation_check>

## Behaviour
- Slider có khoảng giá trị từ 0.1 đến 3.0, bước nhảy 0.1
- Giá trị mặc định khi chưa từng đặt: 1.0
- Kéo slider cập nhật độ nhạy camera ngay trong cùng frame, không cần bấm Apply
- Edge case: khi giá trị lưu trong PlayerPrefs bị hỏng hoặc ngoài khoảng 0.1–3.0, dùng giá trị mặc định 1.0 thay vì crash
- Forbidden: độ nhạy không bao giờ được đọc là 0 hoặc âm

## Scope
- Chỉ dựng đúng những gì liệt kê ở mục Behaviour.
- Không thêm hook, tuỳ chọn config, hay điểm mở rộng nào tôi không yêu cầu.
- Không refactor code xung quanh. Liệt kê riêng những gì bạn muốn đổi.
- Out of scope this round: không làm slider cho volume hay độ sáng màn hình — đó là tính năng khác.

## Constraints
- Tuân `.claude/rules/client/coding-principles.md`, `naming-convention.md` và
  `performance-and-algorithms.md`.
- Không dùng API nào đã đánh dấu `[Obsolete]`.
- Undecided — hỏi tôi, đừng tự chốt: none

## Deliverable
- Code, kèm một Implementation Note theo `.claude/rules/implementation-note.md`:
  nó thoả những clause nào, file nào đã đổi, giả định, giới hạn đã biết, thứ bạn
  cố ý không đụng, và thứ bạn thật sự đã xác minh so với thứ chưa.

## Done when
Kéo slider xuống 0.3 trong Play Mode làm camera xoay chậm hẳn lại, quan sát được ngay; đóng và mở lại Settings panel vẫn hiện đúng 0.3; xoá PlayerPrefs rồi mở lại game thì slider hiện 1.0.
```
