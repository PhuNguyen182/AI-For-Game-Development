# Ví dụ: Dựng nền tảng Status Effect dùng chung

Khung `multi-feature.md`, `Mode: build-shared-foundation`. Chỉ giữ `<shared_foundation>`. Ở mode này, dòng "Không bắt đầu triển khai..." trong Scope bị xoá — chính lượt này LÀ lượt triển khai phần nền.

```text
## Objective
Dựng nền tảng Status Effect dùng chung cho Poison Dagger và Fire Trap, thay vì mỗi kỹ năng tự viết một bộ đếm giờ riêng.

Mode: build-shared-foundation

## The batch
| # | Feature | One-line intent | Priority |
|---|---------|-----------------|----------|
| 1 | Hệ thống Status Effect (Poison/Burn) | Nền tảng hiệu ứng theo thời gian dùng chung | high |
| 2 | Kỹ năng Poison Dagger | Dao găm gây độc theo thời gian | high |
| 3 | Kỹ năng Fire Trap | Bẫy lửa gây bỏng theo thời gian | med |

## Context
- Already shipped and must keep working: hệ thống combat cơ bản, EnemyHealthComponent
- Platform / target: PC + mobile
- Milestone or deadline: demo nội bộ ngày 05/09/2026
- Roles available: C# Software Engineer

<shared_foundation>
Mode build-shared-foundation. Dựng hệ thống StatusEffect (Game.Core.Combat.StatusEffects)
để các tính năng ở trên đứng lên trên nó, thay vì mỗi cái tự mọc ra một phiên bản riêng.
Consumer có thật hôm nay — chỉ thiết kế cho những cái này, không cho cái nào khác:
- Poison Dagger cần: gây sát thương định kỳ theo thời gian, không stack thêm nếu đã có hiệu ứng
- Fire Trap cần: gây sát thương định kỳ theo thời gian, CÓ stack riêng biệt khi trúng nhiều bẫy
Quy tắc:
- Rút ra API nhỏ nhất phủ đúng các nhu cầu có thật ở trên. Không thiết kế cho
  consumer chưa tồn tại (ví dụ: chưa làm hiệu ứng hồi máu theo thời gian).
- Nói rõ cái gì thuộc phần nền (vòng lặp tick, quy tắc stack/refresh) và cái gì mỗi
  tính năng tự giữ (giá trị sát thương, thời lượng, icon). Ranh giới đó quan trọng
  hơn bản thân đoạn code.
- Consumer phụ thuộc vào interface IStatusEffect, không bao giờ phụ thuộc class cụ
  thể hay singleton.
- Nếu dự án đã có package hoặc skill giải quyết việc này, đề xuất dùng nó và nêu rõ
  đánh đổi, thay vì viết mới.
- Nói xem cái gì sẽ phải đổi nếu một hiệu ứng buff/debuff không gây sát thương (ví
  dụ Slow di chuyển) xuất hiện sau này, và việc đổi đó tốn bao nhiêu.
Chỉ tích hợp ĐÚNG MỘT consumer ở lượt này: Poison Dagger. Để yên Fire Trap.
</shared_foundation>

## Scope
- Không mở rộng lô. Thiếu gì thì nêu tên, đừng tự thêm vào.

## Constraints
- Tuân `.claude/rules/client/coding-principles.md` và `naming-convention.md`.
- Đưa ước lượng chi phí theo số lượt gọi agent, cho từng bước, trước khi bắt đầu.
- YAGNI đứng trên tính tổng quát: một API nhỏ mà đúng hơn một API tổng quát mà sai.

## Deliverable
API StatusEffect nhỏ nhất phủ đúng hai consumer trên, đã tích hợp với Poison Dagger,
kèm giải thích ranh giới nền/tính năng và chi phí nếu có consumer thứ ba.

## Done when
Poison Dagger dùng được StatusEffect và gây đúng sát thương định kỳ; Fire Trap chưa
đụng tới nhưng tôi biết rõ nó sẽ cắm vào đâu khi tới lượt.
```
