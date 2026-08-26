# Ví dụ: Lập bản đồ yêu cầu IAP từ Tech Spec nội bộ + tài liệu Google

Khung `from-documents.md`, `Mode: map-the-documents`. Minh hoạ nguồn tài liệu hỗn hợp — Tech Spec nội bộ và tài liệu SDK bên ngoài — với thứ tự thẩm quyền rõ ràng.

```text
## Objective
Cần bản đồ yêu cầu cho việc tích hợp gói vật phẩm IAP theo tài liệu Google Play
Billing, đối chiếu với Tech Spec nội bộ đã có, trước khi giao cho SDK/Platform.

Mode: map-the-documents

<source_documents>
Documents, in order of authority — when two disagree, the higher one wins:
1. docs/TechSpec/TechSpec_IAP_CurrencyPack.md, toàn bộ — Technical Architect viết, cập nhật 10/08/2026 — authority: highest
2. https://developer.android.com/google/play/billing/integrate — Google, truy cập 20/08/2026
Scope I want covered from them: luồng mua gói Currency Pack (không bao gồm subscription)

<excerpt source="TechSpec_IAP_CurrencyPack.md, mục 3">
Khi mua thành công, client phải xác nhận giao dịch (acknowledge) trong vòng 3 ngày
theo yêu cầu của Google, nếu không giao dịch sẽ tự hoàn tiền. Server ghi nhận số dư
currency sau khi verify receipt, client không tự cộng currency.
</excerpt>
</source_documents>

## Context
- Existing code these must fit into: Assets/Scripts/Client/IAP/ (chưa có, sẽ tạo mới)
- Platform / target: Android
- Track state: backend active

<gap_register>
Mode map-the-documents. Không viết dòng code nào ở lượt này.
1. Rút ra danh sách yêu cầu đánh số. Mỗi yêu cầu trích dẫn đúng nguồn — tên tài liệu
   cộng mục, trang, hoặc dòng.
2. Đánh dấu từng cái: clear | ambiguous | contradicts [nguồn].
3. Liệt kê các GAPS — thứ code chắc chắn cần mà tài liệu không bao giờ nói tới:
   giá trị mặc định, hành vi khi lỗi, giới hạn, thứ tự, hành vi lần chạy đầu. Đặc
   biệt: hành vi khi mất mạng giữa lúc mua và lúc acknowledge.
4. Với mỗi gap, đề xuất một giả định và hậu quả nếu nó sai. Đừng tự chốt; để tôi quyết.
5. Ánh xạ mỗi yêu cầu vào một tầng: `Game.Core.*` / `Game.Client.*` / `Game.Server.*`,
   và nói rõ cái nào bạn không chắc.
Đừng bịa ra một yêu cầu không có trong tài liệu. Bất cứ thứ gì bạn cho là "hiển nhiên
cần có" thuộc về danh sách GAPS, không thuộc danh sách yêu cầu.
Trả về: một bảng ID | requirement | source citation | status | layer, rồi danh sách
gap, rồi danh sách mâu thuẫn.
</gap_register>

## Scope
- Cover only the scope named in the source_documents block above.
- Do not implement anything from a document not listed there.

## Constraints
- Follow `.claude/rules/client/coding-principles.md` and `naming-convention.md`.
- Rules that decide an outcome live in `Game.Core.*` and are written once. The
  Client layer calls into them and never reimplements them.

## Deliverable
Bảng yêu cầu (ID | requirement | source citation | status | layer), danh sách gap,
và danh sách mâu thuẫn giữa Tech Spec nội bộ và tài liệu Google.

## Done when
Mọi câu hỏi cần tôi quyết định nằm trong một danh sách tôi trả lời được trong một
lượt.
```
