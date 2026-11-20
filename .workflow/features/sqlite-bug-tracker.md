# SQLite bug tracker

- State: records.py feature show sqlite-bug-tracker

## Request (verbatim)
> tôi có ý tưởng như sau về quy trình log bug của QA. Thay vì ghi bug vào file markdown, rất cồng kềnh và khó truy xuất, thi tôi muốn tận dụng luôn sqlite, ghi các bug thành database, với mỗi 1 bug là 1 bản ghi có thể thao tác CRUD như database bình thường. Bug sẽ có các trạng thái như sau:
> - Request: QA tìm ra bug, ghi vào bảng, yêu cầu sửa
> - Processing: agent nhận bug và xử lý
> - Resolved: bug đã xử lý xong, chờ QA review
> - Review: QA sẽ review lại các bug sau khi các agent sửa
> - Complete: bug đã sửa xong
> - Reopen: bug chưa sửa triệt để, bị mở lại
> - Backlog: tạm thời cho bug vào backlog
> Độ ưu tiên có các mức sau:
> - Low
> - Medium
> - High
> - Highest
> Các bug sẽ tồn tại trong window 90 ngày, sau 90 ngày thì xóa bug cũ ngoài vùng window đi

> (on the first plan) các bug có title và mô tả ngắn gọn nhưng đủ nội dung cần thiết, không văn xuôi dài dòng. Toàn bộ database viết bằng tiếng Anh

## GD decisions

- Rows: records.py csv render decisions --feature sqlite-bug-tracker

## Spec
Full spec: `.workflow/features/sqlite-bug-tracker.spec.md`.

Acceptance criteria:
1. Every bug is one record with create, read, update and delete through `bugs.py`.
2. The 11 statuses and the spec's transition table are enforced on write; GD-only moves refuse without a GD attribution.
3. Priority is one of Low, Medium, High, Highest; bugs carry no Severity.
4. Terminal bugs older than 90 days since reaching terminal are purged; open and Backlog bugs never are; IDs are never reused.
5. `bugs.jsonl` alone rebuilds the DB; branch switch, pull, union merge, crash and a torn line all converge; purged bugs do not come back through a merge.
6. Field limits, required fields and the Vietnamese-diacritics refusal hold on every write; secrets refused, PII redacted.
7. `round-cap.ps1` caps, extra rounds, Stop rule and settled handling behave as before against the DB; no Python on a bug dispatch blocks.
8. `/fix`, `/qa`, `/feature`, `/release`, `/review`, `/new-project`, `qa-lead`, `routing.md`, `core.md` use the new contract; no live `bugs.md` reference remains.
9. BUG-0001..0005 are migrated and `.workflow/bugs.md` is gone.
10. `framework-sync.ps1` installs the `.gitattributes` line in a target project.

## Log

- Rows: records.py csv render log --feature sqlite-bug-tracker

## Tests

- Rows: records.py csv render tests --feature sqlite-bug-tracker

## Bugs

- Bugs: bugs.py list --feature sqlite-bug-tracker

QA findings at `b6deca7`, not filed in the DB: no journal exists before the merge, and the CLI refuses writes from the worktree. Full records in the reports under `.workflow/evidence/sqlite-bug-tracker/attempt-1/`.

## Known limitations

- Rows: records.py csv render limitations --feature sqlite-bug-tracker
