# Ví dụ: Triển khai Crafting từ bản đồ đã chốt

Khung `from-documents.md`, `Mode: implement-from-the-map`. Tiếp nối ví dụ 01 — giữ `<source_documents>` và `<traceability_contract>`, xoá `<gap_register>` vì lượt map đã xong.

```text
## Objective
Triển khai hệ thống Crafting đúng theo bản đồ yêu cầu R1–R9 đã chốt ở lượt map trước,
với các chỗ trống tôi đã trả lời.

Mode: implement-from-the-map

<source_documents>
Documents, in order of authority — when two disagree, the higher one wins:
1. docs/GDD/GDD_Crafting.md, mục 4 "Crafting System" — GD viết, cập nhật 12/08/2026 — authority: highest
2. docs/Balance/Balance_CraftingCosts.xlsx, sheet "T1_Recipes" — Game Designer viết, cập nhật 15/08/2026
Scope I want covered from them: R1 tới R9, theo bảng gap đã trả lời bên dưới
</source_documents>

## Context
- Existing code these must fit into: Assets/Scripts/Client/UI/Inventory/, Assets/Scripts/Core/Inventory/
- Platform / target: PC + mobile
- Track state: client-only

<traceability_contract>
Mode implement-from-the-map. Triển khai đúng các ID này và không gì khác: R1, R2,
R3, R4, R5, R6, R7, R8, R9
Quyết định của tôi về các gap:
- Gap "túi đồ đầy khi craft xong" -> chặn craft NGAY TỪ ĐẦU nếu dự đoán trước túi sẽ
  đầy, không cho craft rồi mới báo lỗi.
- Gap "công thức đã unlock lưu ở đâu" -> dùng danh sách ID trong PlayerSaveData đã có,
  không tạo hệ thống lưu mới.
- Gap "có craft hàng loạt (x5, x10) không" -> KHÔNG làm ở bản này, chỉ craft từng cái một.
Không triển khai ở lượt này: R10 (craft hàng loạt) — vì đã quyết hoãn sang bản sau.

Truy vết là bắt buộc:
- Mỗi class hoặc method chính phải nói được nó phục vụ ID nào. Chỗ nào ánh xạ không
  hiển nhiên, để lại một comment nêu tên ID và lý do.
- Kết thúc bằng một bảng hai chiều: ID -> nơi được triển khai, và file -> các ID nó
  phục vụ.
- Bất kỳ ID nào bạn không đặt được vào đâu phải được khai báo NOT DONE. Không bao giờ
  để một ID biến mất trong im lặng.
- Không triển khai hành vi mà không ID nào yêu cầu. Nếu code có vẻ cần nó, đó là một
  gap — báo cáo lại, đừng tự thêm vào.
Không sửa một con số xuất hiện trong tài liệu. Nếu một con số trông có vẻ sai, báo
cáo lại; đừng tự sửa nó.
</traceability_contract>

## Scope
- Cover only the scope named in the source_documents block above.
- Do not implement anything from a document not listed there.

## Constraints
- Follow `.claude/rules/client/coding-principles.md` and `naming-convention.md`.
- Rules that decide an outcome live in `Game.Core.*` and are written once. The
  Client layer calls into them and never reimplements them.
- Dừng lại sau tầng Core để tôi duyệt, trước khi bắt đầu tầng Client.

## Deliverable
Code cộng bảng truy vết hai chiều cộng một Implementation Note theo
`.claude/rules/implementation-note.md`.

## Done when
Mỗi ID từ R1 tới R9 hoặc có một chỗ triển khai tôi chỉ ra được, hoặc nằm trong danh
sách NOT DONE — không có gì rơi vào khoảng giữa.
```
