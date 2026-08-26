# Ví dụ: Lập bản đồ yêu cầu cho hệ thống Crafting từ GDD

Khung `from-documents.md`, `Mode: map-the-documents`. Giữ `<source_documents>` (luôn giữ) và `<gap_register>`; chưa giữ `<traceability_contract>` vì đó là việc của lượt implement sau.

```text
## Objective
Cần một danh sách yêu cầu có trích dẫn nguồn cho hệ thống Crafting, và danh sách
chỗ trống tôi phải quyết trước khi ai đó bắt đầu viết code.

Mode: map-the-documents

<source_documents>
Documents, in order of authority — when two disagree, the higher one wins:
1. docs/GDD/GDD_Crafting.md, mục 4 "Crafting System" — GD viết, cập nhật 12/08/2026 — authority: highest
2. docs/Balance/Balance_CraftingCosts.xlsx, sheet "T1_Recipes" — Game Designer viết, cập nhật 15/08/2026
Scope I want covered from them: toàn bộ mục 4 của GDD và sheet T1_Recipes

<excerpt source="GDD_Crafting.md, mục 4.2">
Người chơi mở màn Crafting từ Inventory. Chọn một công thức đã unlock, hệ thống
kiểm tra đủ nguyên liệu thì cho phép craft. Craft xong trừ nguyên liệu, cộng thành
phẩm vào túi đồ. Nếu túi đồ đầy, chặn craft và báo lỗi cho người chơi.
</excerpt>
</source_documents>

## Context
- Existing code these must fit into: Assets/Scripts/Client/UI/Inventory/, Assets/Scripts/Core/Inventory/
- Platform / target: PC + mobile
- Track state: client-only

<gap_register>
Mode map-the-documents. Không viết dòng code nào ở lượt này.
1. Rút ra danh sách yêu cầu đánh số. Mỗi yêu cầu trích dẫn đúng nguồn — tên tài liệu
   cộng mục, trang, hoặc dòng.
2. Đánh dấu từng cái: clear | ambiguous | contradicts [nguồn].
3. Liệt kê các GAPS — thứ code chắc chắn cần mà tài liệu không bao giờ nói tới:
   giá trị mặc định, hành vi khi lỗi, giới hạn, thứ tự, hành vi lần chạy đầu.
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
và danh sách mâu thuẫn giữa GDD và bảng balance.

## Done when
Mọi câu hỏi cần tôi quyết định nằm trong một danh sách tôi trả lời được trong một
lượt.
```
