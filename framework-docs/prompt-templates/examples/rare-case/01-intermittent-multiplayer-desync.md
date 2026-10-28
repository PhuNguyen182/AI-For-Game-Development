# Ví dụ: Desync hiếm gặp trong combat PvP

Khung `rare-case.md`, giữ `<intermittent_evidence>` (nguồn là QA nội bộ) cộng thêm `<determinism_audit>` như một add-on — vì triệu chứng là client và server bất đồng với nhau.

```text
## Objective
Điều tra hiện tượng lệch vị trí (desync) giữa client và server trong combat PvP 5v5.
Đây là một lỗi HIẾM — đừng giả định nó tái hiện theo ý muốn.
Đừng sửa gì ở lượt này.

## What is known
- Observed rate: khoảng 3 trên 40 trận đấu nội bộ, trên build QA
- Last seen: hôm qua, trận PvP 5v5 kéo dài hơn 8 phút
- Seems more likely when: trận đấu kéo dài (trên 6 phút), nhiều người chơi dùng kỹ
  năng dịch chuyển (blink/dash) gần như cùng lúc
- Never seen when: trận đấu ngắn (dưới 3 phút), hoặc chỉ có 1-2 người chơi trong khu
  vực nhỏ
- Scattered evidence: 2 video quay màn hình từ QA, log console không có exception

<intermittent_evidence>
Source: báo cáo từ QA nội bộ, playtest 5v5.
Làm theo thứ tự:
1. Phân loại nghi vấn: race condition, thứ tự init/teardown, phụ thuộc frame-rate
   hoặc timestep, trạng thái tích luỹ theo thời gian, một leak, dữ liệu chưa khởi
   tạo, hoặc non-determinism. Với từng loại: cơ chế nào trong CHÍNH codebase này có
   thể gây ra nó — đặc biệt nghi vấn tích luỹ sai số float qua nhiều tick vì trận
   càng dài càng dễ xảy ra.
2. Chỉ ra code có đủ điều kiện để loại đó xảy ra — path:line, kèm lý do. Đây là đọc,
   không phải sửa.
3. Đề xuất cách làm nó DỄ xảy ra hơn, để bắt được nó: ép nhiều người chơi dùng kỹ
   năng dịch chuyển cùng frame, kéo dài trận đấu giả lập, ghim seed cho RNG nếu có.
4. Đề xuất chỗ đặt logging hoặc assertion để lần xảy ra TIẾP THEO mang theo bằng
   chứng, kể cả khi hôm nay chưa bắt được.
</intermittent_evidence>

<determinism_audit>
Add-on: giữ khối này vì triệu chứng là client và server bất đồng với nhau.
Rà `Game.Core.*` để tìm mọi nguồn non-determinism:
- `UnityEngine.Random`, hoặc bất kỳ RNG nào không được tiêm seed
- đọc giờ hệ thống hoặc frame-time
- thứ tự duyệt collection không được đảm bảo
- phép toán float có thể phân kỳ giữa các nền tảng hoặc kiến trúc
- bất cứ thứ gì đọc từ trạng thái Unity thay vì được truyền vào dạng đã resolve
Báo cáo từng chỗ dạng path:line, và nói rõ nó có thực sự ảnh hưởng tới kết quả hay
vô hại trong ngữ cảnh đó.
</determinism_audit>

## Scope
- Chỉ điều tra. Không đổi code production ở lượt này.
- Không mở rộng thành một cuộc rà soát chung cho các hệ thống lân cận.

## Constraints
- Không khẳng định đã sửa xong trừ khi bạn tái hiện được trước rồi mới làm nó dừng
  lại. "Tôi đã đổi gì đó và không thấy lại nữa" không phải bằng chứng cho một lỗi vốn
  dĩ đã hiếm.
- Mọi kết luận đi kèm một mức độ chắc chắn và bằng chứng đứng sau nó.
- "Chưa kết luận được, đây là bước tiếp theo" là một câu trả lời hợp lệ và được mong
  đợi.
- Đừng chỉ báo cáo lần chạy duy nhất ủng hộ giả thuyết. Báo cáo những gì tất cả các
  lần chạy cho thấy.

## Deliverable
Một danh sách nghi phạm đã xếp hạng, cách ép tái hiện, logging và assertion cần thêm,
và một mức độ chắc chắn cho từng mục.

## Done when
Lần tới việc này xảy ra, tôi có đủ dữ liệu để kết luận — kể cả khi hôm nay chưa bắt
được nó.
```
