# Ví dụ: Prototype cảm giác input buffer cho combo đánh thường

Khung `prototype.md`, giữ `<feel_test>`. Ví dụ thứ hai dùng khối này để cho thấy hai câu hỏi cảm nhận khác nhau (né đòn vs. combo) đều đi qua cùng khối, chỉ khác nội dung thao tác.

```text
## Objective
Đây là PROTOTYPE VỨT ĐI ĐƯỢC, không phải code production.
Câu hỏi duy nhất nó tồn tại để trả lời: Input buffer cho combo đánh thường (3 đòn
liên tiếp) có làm combo cảm giác mượt và đã tay hơn không, hay chỉ gây rối?

## Context
- Unity version / platform: Unity 2022.3 LTS, PC
- Sandbox location: Assets/_Prototypes/ComboBufferFeel/
- Input scheme: bấm chuột trái liên tiếp để đánh combo
- Placeholder assets I can use: capsule primitive cho player, debug text hiển thị buffer window

<feel_test>
Những gì tôi phải tự tay làm được:
- Bấm chuột trái 3 lần đúng nhịp -> combo 3 đòn chạy trọn vẹn, có debug text báo mỗi đòn trúng buffer
- Bấm chuột trái quá sớm (trước khi đòn trước kết thúc animation) -> đòn tiếp theo vẫn được ghi nhận vào buffer, không bị rớt input
- Bấm chuột trái quá trễ (sau buffer window) -> combo reset về đòn 1, không nối tiếp
Đủ để tôi phán được trong 5 phút chơi thử.

Được phép cắt — tôi cho phép trước:
- Hardcode giá trị. Không ScriptableObject, không đường ống config.
- Art placeholder: primitive, gizmo, debug text.
- Không test, không README, không lượt tối ưu nào.
- Không xử lý edge case nào ngoài các thao tác liệt kê ở trên.

Ưu tiên: thời gian ra được thứ chơi được, trên tất cả mọi thứ khác.
Đưa các giá trị tôi sẽ muốn tinh chỉnh ra Inspector: độ dài buffer window (ms), thời
điểm trong animation mà buffer window mở ra. Liệt kê chúng cho tôi.
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
buffer window này có cân bằng với tốc độ animation thật, chưa phải placeholder, hay
không).

## Done when
Tôi đã chơi thử và hình thành được phán đoán giữ hay bỏ cơ chế input buffer này.
```
