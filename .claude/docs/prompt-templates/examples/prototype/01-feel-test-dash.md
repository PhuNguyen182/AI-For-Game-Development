# Ví dụ: Prototype cảm giác né đòn bằng Dash

Khung `prototype.md`, giữ `<feel_test>` — câu hỏi là về trải nghiệm ("có đã tay không"), không trả lời được bằng số nên không dùng `<measurement_spike>`.

```text
## Objective
Đây là PROTOTYPE VỨT ĐI ĐƯỢC, không phải code production.
Câu hỏi duy nhất nó tồn tại để trả lời: Dash né đòn có đủ đã tay và đúng nhịp để giữ lại làm cơ chế né chính không?

## Context
- Unity version / platform: Unity 2022.3 LTS, PC (bàn phím + chuột)
- Sandbox location: Assets/_Prototypes/DashFeel/
- Input scheme: giữ Shift + hướng di chuyển để dash
- Placeholder assets I can use: capsule primitive cho player, cube cho enemy tĩnh

<feel_test>
Những gì tôi phải tự tay làm được:
- Bấm Shift + W -> nhân vật lướt nhanh về phía trước, có khoảng bất tử ngắn
- Dash liên tiếp hai lần sát nhau -> phải thấy rõ có cooldown, không spam được vô hạn
- Dash xuyên qua một enemy tĩnh -> không va chạm, không bị chặn lại giữa chừng
Đủ để tôi phán được trong 5 phút chơi thử.

Được phép cắt — tôi cho phép trước:
- Hardcode giá trị. Không ScriptableObject, không đường ống config.
- Art placeholder: primitive, gizmo, debug text.
- Không test, không README, không lượt tối ưu nào.
- Không xử lý edge case nào ngoài các thao tác liệt kê ở trên.

Ưu tiên: thời gian ra được thứ chơi được, trên tất cả mọi thứ khác.
Đưa các giá trị tôi sẽ muốn tinh chỉnh ra Inspector: dash speed, dash duration, dash
cooldown, thời gian bất tử. Liệt kê chúng cho tôi.
Sau khi tôi chơi xong, nói cho tôi biết phần nào đáng giữ lại và phần nào chắc chắn
phải viết lại từ đầu.
</feel_test>

## Scope
- Không đụng vào code production.
- Không đặt file vào bên trong thư mục của một tính năng thật.
- Không dựng abstraction "để sau này dùng" — với đoạn code này không có sau này.

## Constraints
- Đặt tên vẫn theo `.claude/rules/client/naming-convention.md`, để tôi còn đọc được.
- Phần còn lại của `coding-principles.md` được tạm ngưng bên trong thư mục sandbox.
  Ghi một dòng ở đầu mỗi file nói rõ điều đó, để không ai nhầm đây là code production.

## Deliverable
Một scene chơi được kèm danh sách giá trị chỉnh được trong Inspector.
Kèm một dòng nói rõ prototype này KHÔNG trả lời được điều gì (ví dụ: không nói được
dash có cân bằng với các kỹ năng khác hay không).

## Done when
Tôi đã chơi thử và hình thành được phán đoán giữ hay bỏ cơ chế dash này.
```
