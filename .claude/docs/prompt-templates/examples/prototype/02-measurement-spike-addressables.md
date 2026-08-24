# Ví dụ: Đo thời gian load Addressables trên thiết bị yếu

Khung `prototype.md`, giữ `<measurement_spike>` — câu hỏi trả lời được bằng số so với một ngưỡng, không phải cảm nhận nên không dùng `<feel_test>`.

```text
## Objective
Đây là PROTOTYPE VỨT ĐI ĐƯỢC, không phải code production.
Câu hỏi duy nhất nó tồn tại để trả lời: Addressables load một scene level cỡ trung
bình (khoảng 150MB asset) mất bao lâu trên thiết bị Android cấu hình thấp?

## Context
- Unity version / platform: Unity 2022.3 LTS, Android
- Sandbox location: Assets/_Prototypes/AddressablesLoadSpike/
- Input scheme: không cần input, chỉ chạy một scenario cố định
- Placeholder assets I can use: dùng đúng bộ asset của scene Level01 hiện có (không cần placeholder)

<measurement_spike>
Ngưỡng quyết định, nêu TRƯỚC khi đo:
- Pass if:  thời gian load ≤ 4 giây trên Redmi Note 11
- Fail if:  thời gian load > 6 giây trên Redmi Note 11
- Nếu nó rơi vào khoảng giữa hai mức đó, thứ tôi cần biết để quyết định là: có cần
  thêm màn hình loading có progress bar hay chấp nhận loading trắng không

Cách đo:
- Scenario: gọi Addressables.LoadSceneAsync cho Level01 từ Main Menu, đo tới khi
  scene báo isDone
- Platform: thiết bị thật — Redmi Note 11
- Runs: ít nhất 5. Báo cáo dải giá trị giữa các lần chạy, không phải một con số.

Ràng buộc trung thực:
- Không báo cáo lần chạy đẹp nhất. Báo cáo dải giá trị.
- Kết quả trong Editor phải được ghi rõ là chỉ mang tính chỉ báo ở mọi chỗ nó được
  nhắc tới, và không bao giờ thay cho kết quả trên thiết bị thật.
- Nếu không đo được vì thiếu thiết bị Redmi Note 11, trả về Blocked và nói rõ thiếu
  gì. Đừng ước lượng rồi trình bày như đã đo.

Scope: chỉ đo. Không tối ưu, không dựng kiến trúc, không tích hợp.
</measurement_spike>

## Scope
- Không đụng vào code production.
- Không đặt file vào bên trong thư mục của một tính năng thật.
- Không dựng abstraction "để sau này dùng" — với đoạn code này không có sau này.

## Constraints
- Đặt tên vẫn theo `.claude/rules/client/naming-convention.md`, để tôi còn đọc được.
- Phần còn lại của `coding-principles.md` được tạm ngưng bên trong thư mục sandbox.
  Ghi một dòng ở đầu mỗi file nói rõ điều đó, để không ai nhầm đây là code production.

## Deliverable
Một bảng số đo (5 lần chạy trên Redmi Note 11) kèm kết luận Pass/Fail.
Kèm một dòng nói rõ prototype này KHÔNG trả lời được điều gì (ví dụ: không nói được
tốc độ load trên thiết bị iOS).

## Done when
Tôi ra được quyết định có cần màn hình loading có progress bar hay không, chỉ dựa
trên bảng này, không cần đo lại.
```
