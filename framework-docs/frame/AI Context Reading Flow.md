# AI Context Reading Flow

Tài liệu này quy định cách AI/agent/session mới đọc context của một feature trước khi sửa code.

Mục tiêu là giúp AI hiểu đủ để làm việc nhưng không phải đọc toàn bộ tài liệu hoặc toàn bộ source code.

---

## 1. Vai trò của từng file

### `README.md`

Tổng quan feature.

Chứa:
- Feature làm gì.
- Entry point chính.
- Các file/class chính.
- Feature/module nào sử dụng nó.

Dùng để AI xác định nhanh phạm vi công việc.

---

### `ARCHITECTURE.md`

Mô tả cấu trúc bên trong feature.

Chứa:
- Component chính.
- Data flow.
- Dependency.
- Ownership của từng phần.
- Luồng xử lý chính.

Đọc khi cần hiểu feature hoạt động như thế nào bên trong.

---

### `CONTRACTS.md`

Quy định những interface và behavior mà code khác có thể dựa vào.

Chứa:
- Public API.
- Interface.
- Event.
- Data schema.
- Invariant.
- Những behavior không được phá.

Đây là tài liệu ưu tiên cao khi sửa code.

---

### `INTEGRATION.md`

Hướng dẫn feature khác tương tác với feature này.

Chứa:
- Integration point.
- Extension point.
- API/event nên sử dụng.
- Nơi được phép thêm logic.
- Những class/API không nên gọi trực tiếp.

Đọc khi task cần kết nối hoặc sửa hành vi giữa nhiều feature.

---

### `LEDGER.md`

Lịch sử các quyết định kỹ thuật quan trọng.

Chứa:
- Decision đã được đưa ra.
- Lý do.
- Những thay đổi kiến trúc đáng chú ý.
- Những quyết định ảnh hưởng đến code tương lai.

Không cần đọc mặc định. Chỉ đọc khi cần biết vì sao code hiện tại được thiết kế như vậy.

---

### `DEBT.md`

Danh sách technical debt và limitation đã biết.

Chứa:
- Workaround hiện tại.
- Limitation.
- Code cần refactor.
- Những vùng có rủi ro.
- Hướng xử lý mong muốn trong tương lai.

Đọc khi task đụng vào code legacy, workaround hoặc khu vực có vấn đề.

---

### `NOTES.md`

Thông tin bổ sung chưa đủ quan trọng để trở thành contract hoặc architecture.

Chứa:
- Observation.
- Edge case.
- Discovery.
- Ý tưởng chưa quyết định.
- Thông tin tham khảo.

Đọc khi cần thêm context hoặc gặp trường hợp chưa được mô tả ở các file chính.

---

# 2. Luồng đọc mặc định

Khi một AI/session mới nhận task liên quan đến một feature:

```text
Task
  ↓
README
  ↓
INTEGRATION
  ↓
CONTRACTS
  ↓
Source code liên quan
```

Đây là luồng mặc định cho phần lớn task.

Không cần đọc toàn bộ tài liệu ngay từ đầu.

---

# 3. Khi nào đọc `ARCHITECTURE`

Đọc `ARCHITECTURE.md` nếu:

- Task thay đổi logic bên trong feature.
- Task ảnh hưởng nhiều component.
- Không rõ ownership của logic.
- Cần thêm component mới.
- Cần refactor.
- Cần thay đổi data flow.

Luồng lúc này:

```text
README
  ↓
INTEGRATION
  ↓
CONTRACTS
  ↓
ARCHITECTURE
  ↓
Source code
```

---

# 4. Khi nào đọc `LEDGER`

Đọc `LEDGER.md` nếu:

- Gặp một thiết kế có vẻ bất thường.
- Muốn thay đổi một decision cũ.
- Không hiểu tại sao hệ thống lại làm theo cách hiện tại.
- Có nguy cơ undo một quyết định đã được chủ ý đưa ra trước đó.

```text
Current code/problem
        ↓
     LEDGER
        ↓
Hiểu decision cũ
        ↓
Quyết định giữ hoặc thay đổi
```

---

# 5. Khi nào đọc `DEBT`

Đọc `DEBT.md` nếu:

- Task chạm code legacy.
- Gặp workaround.
- Gặp TODO lớn.
- Phát hiện kiến trúc không sạch.
- Muốn refactor.
- Có dấu hiệu bug liên quan limitation đã biết.

```text
Task
 ↓
Code có vấn đề
 ↓
DEBT
 ↓
Kiểm tra đây là bug hay technical debt đã biết
```

---

# 6. Khi nào đọc `NOTES`

Đọc `NOTES.md` khi:

- Các tài liệu khác chưa giải thích đủ.
- Cần tìm edge case.
- Cần xem observation từ các session trước.
- Có behavior lạ chưa được chính thức hóa.

`NOTES.md` là context bổ sung, không phải source of truth.

Nếu `NOTES.md` mâu thuẫn với `CONTRACTS.md`, ưu tiên `CONTRACTS.md`.

---

# 7. Thứ tự ưu tiên thông tin

Khi tài liệu có thông tin mâu thuẫn, ưu tiên:

```text
CONTRACTS
    ↓
ARCHITECTURE
    ↓
INTEGRATION
    ↓
README
    ↓
LEDGER
    ↓
DEBT
    ↓
NOTES
```

Source code hiện tại vẫn phải được kiểm tra để xác nhận implementation thực tế.

---

# 8. Luồng khi task chỉ sử dụng feature

Nếu task chỉ cần gọi hoặc sử dụng feature mà không thay đổi implementation:

```text
README
  ↓
INTEGRATION
  ↓
CONTRACTS
  ↓
Implement
```

Không cần đọc `ARCHITECTURE`, `LEDGER`, `DEBT`, `NOTES` nếu không cần.

---

# 9. Luồng khi task sửa feature

Nếu task sửa logic bên trong feature:

```text
README
  ↓
CONTRACTS
  ↓
ARCHITECTURE
  ↓
INTEGRATION
  ↓
Source code
  ↓
DEBT / LEDGER nếu cần
```

---

# 10. Luồng khi task kết nối nhiều feature

Với mỗi feature liên quan:

```text
README
  ↓
INTEGRATION
  ↓
CONTRACTS
```

Sau đó xác định:

```text
Feature A
   ↓
Integration Point
   ↓
Contract
   ↓
Integration Point
   ↓
Feature B
```

Chỉ đọc `ARCHITECTURE` của feature nào thực sự cần thay đổi bên trong.

---

# 11. Luồng khi debug

```text
README
  ↓
CONTRACTS
  ↓
Reproduce / Trace source
  ↓
ARCHITECTURE
  ↓
DEBT
  ↓
LEDGER
  ↓
NOTES nếu vẫn thiếu context
```

---

# 12. Nguyên tắc cho AI/agent/session mới

Không đọc toàn bộ documentation mặc định.

Bắt đầu từ:

```text
README
→ INTEGRATION
→ CONTRACTS
```

Sau đó chỉ mở thêm tài liệu khi task yêu cầu.

Nguyên tắc:

```text
Need overview
→ README

Need to interact
→ INTEGRATION

Need to know what must not break
→ CONTRACTS

Need internal understanding
→ ARCHITECTURE

Need historical reason
→ LEDGER

Need known problems
→ DEBT

Need extra context
→ NOTES
```

Mục tiêu là:

> Read the minimum context necessary to safely perform the task.

Không phải:

> Read every document before touching the code.