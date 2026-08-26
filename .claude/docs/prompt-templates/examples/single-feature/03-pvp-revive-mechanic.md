# Ví dụ: Cơ chế hồi sinh đồng đội trong PvP 5v5

Khung `single-feature.md`. Minh hoạ tính năng chạm cả ba trục cùng lúc — giữ `<game_rules>`, `<authority_and_sync>`, `<platform_matrix>` và `<process_gates>` trong cùng một khung, đúng như README mô tả ("giữ ba khối, vẫn một khung").

```text
## Objective
Trong chế độ PvP 5v5, người chơi hồi sinh được đồng đội đã ngã gục bằng cách đứng cạnh và giữ nút tương tác trong một khoảng thời gian, đồng đội được hồi sinh với một phần HP tối đa.

## Context
- Where it lives: Assets/Scripts/Client/PvP/Revive/ (Client), Assets/Scripts/Core/PvP/Revive/ (Core), Assets/Scripts/Server/PvP/Revive/ (Server)
- Existing systems it must work with: DownedStateComponent (trạng thái ngã gục đã có), PlayerHealthComponent
- Already available to reuse: IInteractable interface, HoldToInteractController (đã dùng cho tính năng mở rương)

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
- Khoảng cách tương tác tối đa: 2m giữa hai người chơi
- Thời gian giữ nút để hồi sinh xong: 3 giây liên tục, không được ngắt quãng
- Đồng đội hồi sinh với 40% HP tối đa
- Edge case: khi người đang hồi sinh bị trúng đòn, tiến trình giữ nút reset về 0, không hồi sinh một phần
- Forbidden: không hồi sinh được chính mình; không hồi sinh được người chơi đội địch

<game_rules>
Những luật này quyết định kết quả, nên chúng nằm ở `Game.Core.*` và chỉ được viết
một lần:
- Khoảng cách tương tác: 2m
- Thời gian giữ nút: 3 giây liên tục
- % HP hồi lại: 40% HP tối đa
- Điều kiện huỷ: bị trúng đòn trong lúc giữ nút
Ràng buộc lên đoạn code đó:
- Không dùng type của `UnityEngine`. Không `UnityEngine.Random`. Không đọc giờ hệ
  thống. Không phép float nào có thể phân kỳ giữa các nền tảng.
- Tầng Client gọi vào nó và không bao giờ viết lại nó.
- Dữ liệu phụ thuộc Unity (khoảng cách giữa hai người chơi) được resolve ở tầng
  Client/Server rồi truyền vào dạng đã resolve.
</game_rules>

<authority_and_sync>
- Client may predict: hiệu ứng thanh tiến trình giữ nút hiển thị ngay khi bấm giữ
- Server must validate: khoảng cách 2m, thời gian giữ đủ 3 giây liên tục, và người bị hồi sinh thật sự đang ở trạng thái ngã gục
- Client is never the source of truth for: việc hồi sinh có thành công hay không, và % HP sau khi hồi sinh
- Must hold under: 150ms độ trễ, 3% tỉ lệ mất gói, tick rate 20Hz
- Luật được viết một lần ở `Game.Core.*`. Server BỌC và xác thực chúng, không bao
  giờ viết lại. Nếu bạn thấy mình đang copy logic sang phía server, dừng lại và
  báo tôi.
- Chốt hợp đồng client-server với tôi TRƯỚC — hình dạng message, thứ tự, cái gì là
  authoritative, cái gì reconcile — rồi mới viết phần triển khai.
</authority_and_sync>

<platform_matrix>
- Must work on: PC, mobile (Android/iOS)
- Differs by platform: PC giữ phím E, mobile giữ nút ảo trên màn hình — cả hai đi qua chung IInteractable
- Giữ nhánh riêng cho từng nền tảng sau một abstraction duy nhất, không rải `#if`
  khắp code gameplay.
</platform_matrix>

## Scope
- Chỉ dựng đúng những gì liệt kê ở mục Behaviour.
- Không thêm hook, tuỳ chọn config, hay điểm mở rộng nào tôi không yêu cầu.
- Không refactor code xung quanh. Liệt kê riêng những gì bạn muốn đổi.
- Out of scope this round: không làm hồi sinh hàng loạt (nhiều người cùng hồi sinh một người để rút ngắn thời gian) — để bản sau.

## Constraints
- Tuân `.claude/rules/client/coding-principles.md`, `naming-convention.md` và
  `performance-and-algorithms.md`.
- Không dùng API nào đã đánh dấu `[Obsolete]`.
- Undecided — hỏi tôi, đừng tự chốt: có cho phép hồi sinh bị ngắt bởi crowd-control (stun) không — chưa quyết.

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
Hai client kết nối tới cùng server, một bên giữ nút 3 giây cạnh đồng đội ngã gục trong khoảng cách 2m thì đồng đội hồi sinh với đúng 40% HP tối đa quan sát trên cả hai client; ngắt giữ giữa chừng thì tiến trình reset về 0; và hành vi vẫn đúng dưới 150ms độ trễ, 3% mất gói.
```
