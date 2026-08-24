<!--
 HOW TO USE
 1. Copy the Skeleton block below into your message to Claude Code.
 2. Run Mode map-the-documents FIRST, answer the gaps it returns, and only then
    run Mode implement-from-the-map. Skipping the map means the gaps get filled
    by silent guesses instead.
 3. Fill every [bracketed] slot; delete any line whose slot does not apply.
 4. Run the pre-send checklist at the bottom of this file.
 Shared rules for all templates: ./README.md
-->

# From Documents

Khung cho việc triển khai từ **tài liệu có sẵn**: GDD, Tech Spec, bảng số liệu, tài liệu SDK, link thiết kế.

Khi đầu vào là tài liệu, vấn đề không còn là hiểu yêu cầu mà là **truy vết**: mỗi phần code phải chỉ ra được nó phục vụ yêu cầu số mấy, và mỗi yêu cầu phải chỉ ra được nó nằm ở đâu trong code. Thiếu truy vết, hai lỗi kinh điển đi lọt — code có hành vi không tài liệu nào yêu cầu, và yêu cầu có mục không code nào thực hiện.

## Khi nào dùng khung này

| Dùng khi | Không dùng khi |
|---|---|
| Yêu cầu nằm trong tài liệu, không nằm trong đầu bạn | Bạn tự mô tả được yêu cầu trong vài dòng — dùng `single-feature.md` |
| Có nhiều tài liệu và chúng có thể mâu thuẫn nhau | Một brief ngắn, một nguồn |
| Bạn cần chứng minh được đã phủ hết tài liệu | Không ai sẽ hỏi lại chuyện phủ hết |

## Lane và chi phí

Hai bước, chạy tuần tự:

| Mode | Lane | Chi phí |
|---|---|---|
| `map-the-documents` | lập bản đồ, không code | 1–3 lượt |
| `implement-from-the-map` | `.claude/workflows/feature-intake.md` E1 | 8+ lượt |

Đừng gộp hai mode vào một lượt. Bản đồ tồn tại để bạn trả lời các chỗ trống **trước khi** code được viết dựa trên phỏng đoán về chúng.

## Skeleton

```text
## Objective
[One sentence: what I need out of these documents this round.]

Mode: [map-the-documents | implement-from-the-map]

<source_documents>
Documents, in order of authority — when two disagree, the higher one wins:
1. [path or link] — [what it is, who wrote it, date] — authority: highest
2. [path or link] — [ ]
3. [path or link] — [ ]
Scope I want covered from them: [which part, or "all of it"]

<excerpt source="[document 1], section [x]">
[Paste verbatim. Do not summarise, do not trim. Delete this tag if the paths
 above are enough for you to read them yourself.]
</excerpt>
</source_documents>

## Context
- Existing code these must fit into: [paths]
- Platform / target: [ ]
- Track state: [client-only | backend active | multiplayer active]

<gap_register>
Mode map-the-documents. Write no code this round.
1. Extract a numbered requirement list. Each one cites its exact source — document
   name plus section, page, or line.
2. Mark each: clear | ambiguous | contradicts [source].
3. List the GAPS — what the code will certainly need and the documents never state:
   default values, error behaviour, limits, ordering, first-run behaviour.
4. For each gap, propose one assumption and the consequence if it is wrong. Do not
   settle it; leave it for me.
5. Map each requirement to a layer: `Game.Core.*` / `Game.Client.*` / `Game.Server.*`,
   and say which ones you are unsure about.
Do not invent a requirement that is not in the documents. Anything you consider
"obviously needed" belongs in the GAPS list, not in the requirement list.
Return: a table of ID | requirement | source citation | status | layer, then the gap
list, then the contradiction list.
</gap_register>

<traceability_contract>
Mode implement-from-the-map. Implement these IDs and no others: [R1-R7, R12]
My decisions on the gaps: [path to the answered gap list, or state them here]
Not implementing this round: [IDs] — because [reason]

Traceability is mandatory:
- Each main class or method can state which ID it serves. Where the mapping is not
  obvious, leave one comment naming the ID and the reason.
- Finish with a two-way table: ID -> where implemented, and file -> IDs it serves.
- Any ID you cannot place must be declared NOT DONE. Never let one disappear quietly.
- Do not implement behaviour no listed ID asks for. If the code seems to need it,
  that is a gap — report it, do not add it.
Do not change a number that appears in the documents. If a number looks wrong,
report it; do not correct it.
</traceability_contract>

## Scope
- Cover only the scope named in the source_documents block above.
- Do not implement anything from a document not listed there.

## Constraints
- Follow `.claude/rules/client/coding-principles.md` and `naming-convention.md`.
- Rules that decide an outcome live in `Game.Core.*` and are written once. The
  Client layer calls into them and never reimplements them.
- Stop after the Core layer for my approval, before starting the Client layer.
  [Delete this line in map-the-documents mode.]

## Deliverable
[The requirement table, the gap list and the contradiction list | code plus the
 two-way traceability table plus an Implementation Note per
 `.claude/rules/implementation-note.md`.]

## Done when
[Every question needing my decision sits in one list I can answer in a single pass
 | every listed ID either has an implementation I can point at, or appears in the
 NOT DONE list — nothing falls in between.]
```

## Optional blocks

| Khối | Giữ khi | Xoá khi |
|---|---|---|
| `<source_documents>` | **Luôn luôn** | Không bao giờ |
| `<excerpt>` (bên trong) | Tài liệu ở ngoài repo, hoặc bạn muốn chắc chắn Claude đọc đúng đoạn | Claude tự mở được đường dẫn |
| `<gap_register>` | `Mode: map-the-documents` | Mode implement |
| `<traceability_contract>` | `Mode: implement-from-the-map` | Mode map |

## Cạm bẫy

- **Tài liệu game gần như luôn mâu thuẫn với chính nó ở phần con số** — GDD nói một đằng, bảng balance nói một nẻo. Dòng "in order of authority" giải quyết trước cả chục tranh cãi về sau.
- **Rút gọn đoạn dán vào là cắt mất chỗ chứa manh mối.** Nếu đã mở `<excerpt>` thì dán nguyên văn.
- **Yêu cầu "hiển nhiên phải có" là loại nguy hiểm nhất.** Nó không có trong tài liệu, không ai duyệt, và không ai nhớ ai đã quyết. Mục 3 của `<gap_register>` tồn tại để lôi chúng ra ánh sáng.
- **Bảng đối chiếu một chiều là bảng vô dụng.** ID → code bắt được yêu cầu bị bỏ sót; code → ID bắt được hành vi thừa. Cần cả hai.
- **Sửa con số trong tài liệu thay vì báo lại là cách tài liệu và code trôi khỏi nhau.** Code sửa đúng, tài liệu vẫn sai, và người tiếp theo tin tài liệu.

## Trước khi gửi

- [ ] `Mode:` chỉ còn một giá trị, và chỉ khối tương ứng còn lại.
- [ ] Thứ tự thẩm quyền tài liệu đã ghi rõ, không phải chỉ liệt kê.
- [ ] Mọi đường dẫn/link tài liệu mở được thật.
- [ ] Với mode implement: danh sách ID cụ thể, không phải "tất cả".
- [ ] Với mode implement: bạn đã trả lời xong danh sách chỗ trống từ lượt map.
- [ ] Không còn `[` và không còn tag rỗng.

## Sau khi nhận trả lời

- [ ] Với mode map: trả lời **hết** danh sách chỗ trống trong một lượt. Bỏ sót một mục là để nó thành phỏng đoán.
- [ ] Kiểm tra mục "contradicts" — mỗi mâu thuẫn cần bạn chốt tài liệu nào thắng, không để Claude chọn.
- [ ] Với mode implement: đọc bảng hai chiều theo **cả hai hướng**. Cột "file → IDs" là chỗ lộ hành vi thừa.
- [ ] Kiểm tra danh sách NOT DONE có thật sự rỗng không, hay chỉ là không được in ra.
- [ ] Không nghiệm thu bằng cách đọc code. Nghiệm thu bằng cách đối chiếu ID.
