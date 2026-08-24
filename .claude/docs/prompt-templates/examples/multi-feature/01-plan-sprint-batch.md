# Ví dụ: Lập kế hoạch cho lô 4 tính năng trong sprint

Khung `multi-feature.md`, `Mode: plan-the-batch`. Chỉ giữ `<dependency_map_request>`, xoá hai khối `<shared_foundation>` và `<in_flight_change>`.

```text
## Objective
Tôi có 4 tính năng cho sprint tuần tới, cần biết thứ tự làm và cái nào phụ thuộc cái nào trước khi giao việc.

Mode: plan-the-batch

## The batch
| # | Feature | One-line intent | Priority |
|---|---------|-----------------|----------|
| 1 | Hệ thống Status Effect (Poison/Burn) | Nền tảng hiệu ứng theo thời gian dùng chung cho nhiều kỹ năng | high |
| 2 | Kỹ năng Poison Dagger | Dao găm gây độc theo thời gian | high |
| 3 | Kỹ năng Fire Trap | Bẫy lửa gây bỏng theo thời gian | med |
| 4 | HUD hiển thị icon hiệu ứng đang active | Hiển thị icon Poison/Burn trên đầu nhân vật | med |

## Context
- Already shipped and must keep working: hệ thống combat cơ bản (đánh thường, HP, cooldown kỹ năng)
- Platform / target: PC + mobile
- Milestone or deadline: demo nội bộ ngày 05/09/2026
- Roles available: C# Software Engineer, Unity Engineer, UI/UX Programmer

<dependency_map_request>
Mode plan-the-batch. Không viết dòng code nào ở lượt này.
1. Triage từng tính năng: tier, và nó có chạm `Game.Core.*`, có cần nhiều hơn một
   vai trò, có liên quan multiplayer, hay có dựa trên thứ chưa quyết.
2. Dựng đồ thị phụ thuộc: cái nào phải xong trước cái nào, và VÌ SAO — một phụ
   thuộc kỹ thuật thật, không phải thứ tự tôi gõ ra.
3. Chỉ ra phần dùng chung. Nếu nhiều tính năng sẽ mỗi cái tự dựng một phiên bản của
   cùng một thứ, nói ra và đề xuất tách nó thành việc riêng.
4. Chỉ ra xung đột: hai tính năng cùng sửa một file, hoặc hai tính năng đưa ra hai
   giả định trái nhau về cùng một hệ thống.
5. Đề xuất thứ tự thực hiện, kèm chi phí từng bước tính theo số lượt gọi agent.
Trả về bảng: feature | tier | depends on | risk | cost. Rồi tới thứ tự và lý do.
</dependency_map_request>

## Scope
- Không bắt đầu triển khai bất kỳ tính năng nào trong lô ở lượt này.
- Không mở rộng lô. Thiếu gì thì nêu tên, đừng tự thêm vào.

## Constraints
- Tuân `.claude/rules/client/coding-principles.md` và `naming-convention.md`.
- Đưa ước lượng chi phí theo số lượt gọi agent, cho từng bước, trước khi bắt đầu.
- YAGNI đứng trên tính tổng quát: một API nhỏ mà đúng hơn một API tổng quát mà sai.

## Deliverable
Bảng mà khối `<dependency_map_request>` yêu cầu, kèm khuyến nghị thứ tự thực hiện.

## Done when
Tôi chọn được cái làm đầu tiên mà không phải đoán, và biết cái nào còn thiếu thông
tin đến mức chưa thể bắt đầu.
```
