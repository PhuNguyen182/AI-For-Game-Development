# Ví dụ: Crash hiếm trên một dòng thiết bị Android cụ thể

Khung `rare-case.md`, giữ `<production_telemetry>` — nguồn là Play Console, không phải máy trong studio. Trace chưa symbolicate nên bước ROOT CAUSE yêu cầu nói rõ cần gì để symbolicate thay vì đoán.

```text
## Objective
Điều tra một pattern crash native hiếm gặp, chỉ xuất hiện trên một số thiết bị
Android cụ thể, theo báo cáo Play Console.
Đây là một lỗi HIẾM — đừng giả định nó tái hiện theo ý muốn.
Đừng sửa gì ở lượt này.

## What is known
- Observed rate: 0.4% session, trên device thật (production)
- Last seen: 3 giờ trước, theo Play Console Android vitals
- Seems more likely when: thiết bị dùng GPU Mali-G52, RAM 3GB trở xuống
- Never seen when: chưa ghi nhận trên thiết bị RAM 6GB trở lên
- Scattered evidence: 47 báo cáo crash trong 7 ngày qua, tập trung ở app version 1.4.0

<production_telemetry>
Source: người chơi thật.
- Channel: Play Console vitals
- Rate: 0.4% session, phiên bản app 1.4.0, từ build 140
- Device or OS concentration: tập trung ở thiết bị GPU Mali-G52, Android 11-12
- Correlates with: bộ nhớ thấp (RAM 3GB), scene có nhiều particle VFX (Arena map)
- Symbol state: chưa symbolicate — chưa upload native debug symbols cho build 140

<telemetry_excerpt>
#00 pc 0002a3f0  libunity.so (BuildRenderPipeline+124)
#01 pc 0001f8b2  libunity.so (offset 0x1f8b2)
#02 pc 000dc410  libc.so (abort+64)
signal 6 (SIGABRT), code -6, fault addr --------
Backtrace:
  #00 pc 0002a3f0  libunity.so
  #01 pc 0001f8b2  libunity.so
</telemetry_excerpt>

Ba giai đoạn. Dừng sau mỗi giai đoạn và chờ:
1. FAULT DOMAIN — code của mình, một SDK bên thứ ba, engine, hay thiết bị/driver?
   Nêu bằng chứng nào chỉ về hướng đó, và bằng chứng nào sẽ bác bỏ nó.
2. ROOT CAUSE — cơ chế cụ thể, kèm mức độ chắc chắn. Trace chưa symbolicate, nên nói
   rõ cần gì để symbolicate (upload debug symbols cho build 140 lên Play Console)
   thay vì đoán từ tên hàm đã bị obfuscate.
3. HANDOFF — agent-id nào sở hữu việc sửa, mức độ nghiêm trọng theo tác động nếu bỏ
   mặc, và chỉ số nào ở ngưỡng nào xác nhận nó đã hết ở bản build tiếp theo.
Tương quan không phải nguyên nhân. Đánh dấu mọi chỗ bạn đang suy luận thay vì quan sát.
</production_telemetry>

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
Fault domain, root cause với mức độ chắc chắn, mức độ nghiêm trọng, và một chủ sở
hữu (agent-id) cho việc sửa.

## Done when
Lần tới việc này xảy ra, tôi có đủ dữ liệu để kết luận — kể cả khi hôm nay chưa bắt
được nó.
```
