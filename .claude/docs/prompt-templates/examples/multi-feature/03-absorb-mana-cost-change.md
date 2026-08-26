# Ví dụ: Hấp thụ thay đổi chi phí mana sau playtest

Khung `multi-feature.md`, `Mode: absorb-a-change`. Chỉ giữ `<in_flight_change>`. Câu hỏi số 4 trong khối này là chỗ đáng tiền nhất — buộc phân biệt "sửa chi tiết" với "thiết kế sai".

```text
## Objective
Sau buổi playtest tuần này, ba kỹ năng bị đổi chi phí mana — cần biết cái gì phải sửa theo trước khi tôi duyệt.

Mode: absorb-a-change

## The batch
| # | Feature | One-line intent | Priority |
|---|---------|-----------------|----------|
| 1 | Fireball | Đổi chi phí mana từ 25 xuống 20 | high |
| 2 | Ice Spike | Đổi chi phí mana từ 15 lên 20 | high |
| 3 | Chain Lightning | Đổi chi phí mana từ 35 xuống 30 | med |

## Context
- Already shipped and must keep working: Fireball (đã ship), Ice Spike (đang review), Chain Lightning (đang code dở)
- Platform / target: PC + mobile
- Milestone or deadline: bản build playtest tiếp theo, 31/08/2026
- Roles available: C# Software Engineer

<in_flight_change>
Mode absorb-a-change. Không đổi dòng code nào ở lượt này.
The change: đồng bộ lại chi phí mana của ba kỹ năng — Fireball 25→20, Ice Spike
15→20, Chain Lightning 35→30.
Reason: phản hồi playtest — Fireball rẻ quá so với sát thương, Ice Spike quá rẻ so
với hiệu ứng làm chậm, Chain Lightning quá đắt khiến người chơi không dùng.
Trạng thái từng tính năng bị ảnh hưởng: Fireball: đã ship | Ice Spike: đang review |
Chain Lightning: đang code dở
Trả lời bốn câu hỏi:
1. Blast radius — những file, hệ thống và tính năng nào phải đổi theo. Tách "bắt
   buộc phải đổi" khỏi "đổi thì tốt hơn".
2. Cái gì đang phụ thuộc vào hành vi cũ và sẽ vỡ — gồm cả save data của người chơi
   hiện tại nếu build cũ đã lưu combo kỹ năng theo chi phí mana cũ.
3. Tài liệu nào thành lỗi thời: Tech Spec, test, README, config balance.
4. Đây là một chi tiết cần sửa, hay là dấu hiệu thiết kế sai? Nói thẳng. Đừng gói
   một lỗi thiết kế thành một bug thường để giữ nó trong chu trình thông thường.
Trả về bảng: item | phải đổi gì | rủi ro | agent-id sở hữu. Rồi một khuyến nghị —
làm ngay, hoãn, hay thiết kế lại. Chờ tôi duyệt rồi mới hành động.
</in_flight_change>

## Scope
- Không bắt đầu triển khai bất kỳ tính năng nào trong lô ở lượt này.
- Không mở rộng lô. Thiếu gì thì nêu tên, đừng tự thêm vào.

## Constraints
- Tuân `.claude/rules/client/coding-principles.md` và `naming-convention.md`.
- Đưa ước lượng chi phí theo số lượt gọi agent, cho từng bước, trước khi bắt đầu.
- YAGNI đứng trên tính tổng quát: một API nhỏ mà đúng hơn một API tổng quát mà sai.

## Deliverable
Bảng blast radius mà khối `<in_flight_change>` yêu cầu, kèm khuyến nghị.

## Done when
Tôi biết chính xác file nào phải sửa cho cả ba kỹ năng, tài liệu nào cần cập nhật
theo, và liệu đây có phải dấu hiệu công thức cân bằng đang sai từ gốc hay không.
```
