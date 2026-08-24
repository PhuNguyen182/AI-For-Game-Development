# Ví dụ: Kỹ năng Fireball

Khung `single-feature.md`. Minh hoạ trường hợp `<escalation_check>` áp dụng vì chạm `Game.Core.*` và cần nhiều vai trò — giữ `<game_rules>`, `<performance_budget>` (AOE trúng nhiều enemy) và `<process_gates>`. Không giữ `<authority_and_sync>` (chơi đơn) hay `<platform_matrix>` (hành vi không khác theo nền tảng).

```text
## Objective
Người chơi dùng được kỹ năng Fireball: bắn một quả cầu lửa gây sát thương diện rộng lên quái vật trong bán kính nổ, có thời gian hồi chiêu và tốn mana.

## Context
- Where it lives: Assets/Scripts/Client/Abilities/ (Client), Assets/Scripts/Core/Abilities/ (Core)
- Existing systems it must work with: PlayerManaComponent (đã có), EnemyHealthComponent (đã có, implement IDamageable)
- Already available to reuse: IAbility interface, AbilityCooldownService (hiển thị cooldown phía Client)

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
- Gây 60 sát thương vật lý cho mọi enemy trong bán kính 3m quanh điểm va chạm
- Tốn 25 mana mỗi lần dùng, không dùng được nếu mana hiện tại dưới 25
- Cooldown 4 giây, tính từ lúc phóng thành công
- Edge case: khi mana đủ nhưng đang trong cooldown thì input bị bỏ qua, không trừ mana
- Forbidden: không bao giờ gây sát thương lên chính người chơi hoặc đồng minh

<game_rules>
Những luật này quyết định kết quả, nên chúng nằm ở `Game.Core.*` và chỉ được viết
một lần:
- Sát thương: 60 (cố định, chưa scale theo level ở bản này)
- Bán kính nổ: 3m
- Chi phí mana: 25
- Cooldown: 4 giây
Ràng buộc lên đoạn code đó:
- Không dùng type của `UnityEngine`. Không `UnityEngine.Random` — bơm vào một RNG
  có seed. Không đọc giờ hệ thống. Không phép float nào có thể phân kỳ giữa các
  nền tảng.
- Tầng Client gọi vào nó và không bao giờ viết lại nó.
- Dữ liệu phụ thuộc Unity được resolve ở tầng Client rồi truyền vào dạng đã resolve.
</game_rules>

<performance_budget>
- Budget: dưới 2ms trên Redmi Note 11, đo trong scene Arena với 20 enemy trong tầm nổ
- Hot path: không cấp phát mỗi frame, không LINQ, không `GetComponent` trong
  `Update`, không `Find`/`FindObjectOfType` lúc runtime.
- Mọi khẳng định về hiệu năng phải kèm số đo trước/sau và độ dao động giữa các lần
  chạy. Số đo trong Editor phải được ghi rõ là chỉ mang tính chỉ báo và không bao
  giờ thay cho số đo trên thiết bị thật.
</performance_budget>

## Scope
- Chỉ dựng đúng những gì liệt kê ở mục Behaviour.
- Không thêm hook, tuỳ chọn config, hay điểm mở rộng nào tôi không yêu cầu.
- Không refactor code xung quanh. Liệt kê riêng những gì bạn muốn đổi.
- Out of scope this round: không làm scaling sát thương theo level, không làm crit — để bản sau.

## Constraints
- Tuân `.claude/rules/client/coding-principles.md`, `naming-convention.md` và
  `performance-and-algorithms.md`.
- Không dùng API nào đã đánh dấu `[Obsolete]`.
- Undecided — hỏi tôi, đừng tự chốt: VFX cụ thể (particle nào) chưa chốt, dùng placeholder trước.

<process_gates>
- Triage trước. Nêu rõ bạn xếp tier nào và vì sao.
- Nêu chi phí tính theo số lượt gọi agent trước khi bắt đầu.
- Dừng ở từng checkpoint để tôi duyệt. Đừng chạy một mạch tới code.
- Nêu ra mọi giả định bạn đã tự đặt ở chỗ brief của tôi im lặng.
</process_gates>

## Deliverable
- Code, kèm một Implementation Note theo `.claude/rules/implementation-note.md`:
  nó thoả những clause nào, file nào đã đổi, giả định, giới hạn đã biết, thứ bạn
  cố ý không đụng, và thứ bạn thật sự đã xác minh so với thứ chưa.

## Done when
Dùng Fireball trúng 3 enemy đứng trong bán kính 3m thì cả ba mất đúng 60 HP trong Play Mode; dùng lại trong vòng 4 giây bị chặn và mana không bị trừ; và budget hiệu năng ở trên vẫn đạt, đo cùng một cách, trên cùng một thiết bị.
```
