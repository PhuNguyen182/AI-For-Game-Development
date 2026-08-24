<!--
 HOW TO USE THIS FOLDER
 1. Pick the template whose PURPOSE matches your request — see the picker
    table below. Purpose, not subject matter: a multiplayer feature and a
    settings screen both use single-feature.md.
 2. Copy that file's Skeleton block into your message to Claude Code.
 3. Fill every [bracketed] slot. Delete any line whose slot does not apply.
 4. Keep or delete each <optional_block> WHOLE — never leave an empty tag.
 5. Run that file's pre-send checklist before you press enter.
 Do not edit a Skeleton in place unless you mean to change the template for
 everyone. Copy it out, edit the copy.
-->

# Prompt Templates

Bảy khung để giao việc cho Claude Code, chia theo **mục đích** chứ không theo chủ đề. Một tính năng multiplayer và một màn hình settings dùng cùng một khung — khác nhau ở chỗ giữ hay xoá khối `<authority_and_sync>`.

Mỗi khung là một file. File này giữ phần dùng chung cho cả bảy: khung sáu phần, hợp đồng định dạng, và quy tắc điền. Bảy file kia trỏ về đây thay vì chép lại.

## Khung sáu phần

Mọi khung trong thư mục này đều là biến thể của sáu phần dưới đây. Prompt hỏng gần như luôn vì thiếu một phần, không phải vì viết chưa đủ dài.

| Phần | Trả lời câu hỏi | Thiếu nó thì hỏng ra sao |
|---|---|---|
| `Objective` | Xong việc này thì cái gì khác đi? | Claude tối ưu cho thứ nó đoán là bạn muốn, và nó đoán rất thuyết phục |
| `Context` | Việc này nằm ở đâu, trên nền gì, đã có sẵn gì? | Nó đi tìm lại thứ bạn đã biết chỗ, hoặc sửa nhầm file cùng tên |
| `Scope` | Được đụng gì, và dứt khoát cấm đụng gì? | Thay đổi lan sang code không liên quan, review phình ra gấp ba |
| `Constraints` | Rule nào, ngân sách nào, cấm dùng gì? | Code chạy được nhưng vi phạm convention, phải làm lại từ đầu |
| `Deliverable` | Trả về hình dạng gì? | Bạn nhận văn xuôi khi cần diff, hoặc nhận code khi mới cần đánh giá |
| `Done when` | Dựa vào đâu để nói việc này đã xong? | Không có cơ sở nói "chưa xong", mọi tranh luận thành cảm tính |

Hai phần hay bị bỏ nhất là `Scope` và `Done when` — và đó đúng là hai phần đắt nhất khi thiếu.

## Hợp đồng định dạng — Markdown cho chỉ thị, XML cho dữ liệu

| Dạng | Dùng cho | Vì sao |
|---|---|---|
| **Markdown** | Toàn bộ phần chỉ thị: heading, bullet, bảng | Đúng thứ Claude Code đọc mỗi ngày (`CLAUDE.md`, agent file, rule). Không tốn token cho cú pháp, sửa tay dễ |
| **XML tag** | Mọi thứ **dán nguyên văn**: log, trích spec, code hiện có, số liệu | Ranh giới giữa "đây là dữ liệu" và "đây là lệnh" bị nhoè khi dán khối dài. Tag đóng vai trò cặp ngoặc kép đó, và Claude phân định tag rất tốt |
| **JSON** | Chỉ khi phần đó **thật sự là dữ liệu bảng** — ví dụ 30 item × 4 thuộc tính | Ép escape xuống dòng và dấu nháy, một dấu phẩy thiếu hỏng cả khối, và biến văn xuôi thành chuỗi một dòng không đọc được |

Không bọc phần chỉ thị vào JSON. Đó là cách nhanh nhất biến một prompt dễ sửa thành một prompt phải debug.

Tên tag dùng `snake_case`, mở và đóng đầy đủ, và nội dung dán vào **không được sửa** — nếu cần chú thích thì viết ngoài tag.

## Chọn khung nào

Lane và chi phí ánh xạ sang `.claude/workflows/orchestrator.md` step 0.

| Bạn đang muốn | Khung | Lane | Chi phí |
|---|---|---|---|
| Hiểu code, đổi tên, chỉnh một giá trị, viết một đoạn nhỏ | `basic-request.md` | trực tiếp | 0–1 |
| Thêm **một** tính năng, quy mô bất kỳ | `single-feature.md` | trực tiếp **hoặc** `feature-intake.md` E1 — khối `<escalation_check>` quyết định | 0–1 hoặc 8+ |
| Thêm **một lô** tính năng | `multi-feature.md` | lập kế hoạch trước, rồi lặp `single-feature` cho từng cái | 1–3, rồi n lần |
| Dựng bản thử để vứt đi, hoặc đo tính khả thi | `prototype.md` | trực tiếp | 1–3 |
| Triển khai từ GDD / spec / tài liệu có sẵn | `from-documents.md` | lập bản đồ trước, rồi `feature-intake.md` E1 | 1–3, rồi 8+ |
| Sửa một lỗi tái hiện được | `bugfix-debug.md` | trực tiếp, hoặc `feature-development.md` E3 nếu pipeline đã dựng nó | 0–3 |
| Điều tra lỗi hiếm, không tái hiện ổn định | `rare-case.md` | điều tra trước, không sửa ngay | 1–3 |

Chọn nhầm về phía **rẻ hơn** thì sửa được: escalate lên khi phát hiện tiêu chí áp dụng, lúc đó chưa mất gì. Chọn nhầm về phía **đắt hơn** thì trả tám lượt agent cho một việc một lượt.

## Quy tắc điền

- Mọi `[slot]` phải được điền, hoặc **xoá cả dòng**. Một slot còn nguyên ngoặc là một chỗ Claude sẽ tự điền hộ bạn.
- Khối `<optional_block>` giữ hoặc xoá **trọn khối**, kể cả tag. Đừng để lại tag rỗng — nó báo hiệu "phần này có, nhưng tôi không biết" và Claude sẽ hỏi lại hoặc đoán.
- Nội dung dán vào giữ nguyên văn. Đừng rút gọn stack trace hay cắt bớt trích dẫn spec cho gọn — chỗ bạn cắt thường là chỗ chứa manh mối.
- Chỗ nào bạn **chưa quyết**, viết ra là chưa quyết thay vì bỏ trống. Bỏ trống được đọc là "không quan trọng"; viết ra được đọc là "hỏi tôi".
- Giữ nguyên tên mục tiếng Anh trong Skeleton. Nội dung bạn điền viết tiếng Việt hay tiếng Anh đều được.

## Checklist chung — chạy trước khi gửi, cho mọi khung

- [ ] Không còn `[` nào trong phần bạn sắp gửi.
- [ ] Không còn tag mở mà thiếu tag đóng, và không còn tag rỗng.
- [ ] `Scope` nói rõ cả cái được đụng lẫn cái cấm đụng.
- [ ] `Done when` là thứ kiểm chứng được, không phải tính từ ("mượt", "ổn", "hợp lý").
- [ ] Mọi đường dẫn bạn nhắc tới đều tồn tại thật — đường dẫn sai làm Claude đi tìm mất một lượt.
- [ ] Con số đi kèm đơn vị và điều kiện đo ("60fps trên thiết bị X ở scene Y", không phải "60fps").

## Kiểm tra bộ template này

Chạy khi bạn vừa sửa một file trong thư mục.

```bash
D=.claude/docs/prompt-templates

# Mọi file dưới 200 dòng
wc -l $D/*.md

# Bảy khung phải có đúng 7 mục ngoài code fence (README có 6, đúng thiết kế)
for f in $D/*.md; do
  echo "$(basename $f) -> $(awk '/^```/{b=!b;next} !b && /^## /{c++} END{print c+0}' $f)"
done

# Trong mỗi Skeleton, mọi tag phải có đúng một cặp mở/đóng
for f in $D/*.md; do echo "--- $(basename $f)"
  awk '/^```/{b=!b;next} b{while(match($0,/<\/?[a-z_]+[ >]/)){t=substr($0,RSTART,RLENGTH);print t;$0=substr($0,RSTART+RLENGTH)}}' $f \
   | sed 's/[ >]$//' | sort | uniq -c
done

# Bảy khung phải có đúng một khối Skeleton
for f in $D/*.md; do
  [ "$(grep -c '^```text$' $f)" = 1 ] || echo "THIẾU/THỪA Skeleton: $f"
done

# Mọi đường dẫn rule/workflow được trích dẫn phải tồn tại thật
grep -oh '\.claude/[a-zA-Z0-9/._-]*\.md' $D/*.md | sort -u | while read -r p; do
  [ -f "$p" ] || echo "BROKEN REF: $p"
done
```
