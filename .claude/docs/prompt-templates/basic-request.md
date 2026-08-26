<!--
 HOW TO USE
 1. Copy the Skeleton block below into your message to Claude Code.
 2. Pick ONE value on the `Task kind:` line and delete the rest.
 3. Fill every [bracketed] slot; delete any line whose slot does not apply.
 4. Keep or delete each <optional_block> whole, tags included.
 5. Run the pre-send checklist at the bottom of this file.
 Shared rules for all templates: ./README.md
-->

# Basic Request

Khung cho việc mà **nhìn kết quả là biết đúng hay sai**: đọc hiểu code, đổi tên, format, sửa config, chỉnh một giá trị hiển thị, hoặc viết một đoạn nhỏ một vai trò.

Bốn loại việc đó khác nhau ở chi tiết nhưng chung một khung. Cái phân biệt chúng là dòng `Task kind:` và hai khối tuỳ chọn.

## Khi nào dùng khung này

| Dùng khi | Không dùng khi |
|---|---|
| Bạn phán được đúng/sai bằng cách nhìn kết quả | Phải chạy test hoặc đo mới biết đúng — dùng `single-feature.md` |
| Một vai trò làm hết, không cần phối hợp | Cần nhiều vai trò — dùng `single-feature.md` |
| Không có luật chơi nào bên trong | Chạm `Game.Core.*` — dùng `single-feature.md` |
| Bạn đã biết đại khái chỗ cần đụng | Không biết bắt đầu từ đâu — chạy `Task kind: understand` trước |

Việc sửa lỗi **không** thuộc khung này kể cả khi nhỏ — dùng `bugfix-debug.md`.

## Lane và chi phí

Lane trực tiếp trong `.claude/workflows/orchestrator.md` step 0. Chi phí 0–1 lượt agent. Không có checkpoint, không có Tech Spec — đó là lý do khung này rẻ.

## Skeleton

```text
## Objective
[One sentence: what is different once this is done.]

Task kind: [understand | rename-or-format | tune-a-visible-value | write-something-small]

## Context
- Entry point: [the one file, class, prefab, or scene I already know]
- What I do not know yet: [the actual question — or delete this line]
- Platform / version: [Unity version, target platform — or delete this line]

<existing_code>
[Paste verbatim the code, config, or asset the task is about.
 Delete this whole block when the entry point above is enough.]
</existing_code>

## Scope
- Touch only: [file, folder, or component]
- Do not touch: [what you expect me to be tempted by]
- Find the same problem elsewhere: list it at the end, do not fix it.

## Constraints
- Follow `.claude/rules/client/coding-principles.md` and `naming-convention.md`.
- Do not change observable behaviour. [Delete when the task IS the change.]
- Do not introduce any API marked `[Obsolete]`.
- Stop and tell me BEFORE proceeding if this turns out to touch `Game.Core.*`,
  need more than one role, affect multiplayer, or rest on something I have not
  decided yet. Do not route around it silently.

<api_contract>
[Task kind write-something-small only. The public surface I want:
 - Method(...) -> return  — purpose
 - property / event       — purpose
 Do not add anything beyond this list.
 Delete this whole block for the other three task kinds.]
</api_contract>

## Deliverable
- [Diff | file list as path:line | the answer in prose — pick one.]
- One line per file saying why it was touched.
- A list of what you noticed and deliberately left alone.

## Done when
[A check I can run myself: a grep that returns nothing, a value that reads X,
 a screen that looks like Y at aspect ratio Z, a clean compile.]
```

## Optional blocks

| Khối | Giữ khi | Xoá khi |
|---|---|---|
| `<existing_code>` | Đoạn code/config ngắn và bạn muốn chắc chắn Claude nhìn đúng chỗ đó | Điểm vào đã đủ rõ, hoặc nội dung quá dài — khi đó chỉ đưa `path:line` |
| `<api_contract>` | `Task kind: write-something-small` | Ba loại việc còn lại |

Dòng `Stop and tell me BEFORE proceeding` trong `Constraints` **không phải khối tuỳ chọn** — luôn giữ. Đó là bốn tiêu chí escalation ở `.claude/rules/orchestration.md`, viết dưới dạng một câu hỏi rẻ thay vì một giả định im lặng.

## Cạm bẫy

- **"Giải thích codebase cho tôi" là câu hỏi không có đáy.** Không có `Entry point`, bạn sẽ nhận một câu trả lời đúng và vô dụng. Luôn cho một điểm vào và một câu hỏi cụ thể.
- **Một con số cân bằng trông như chore nhưng thường là một luật chơi.** Dòng escalation là cái van đưa nó về đúng lane trước khi bạn sửa nhầm một thứ thuộc `Game.Core.*`.
- **Đừng gộp một chore với một fix.** Một commit làm hai việc là commit mà `git bisect` không chỉ mặt được và `git revert` không gỡ sạch được.
- **Bỏ `Do not touch` là mời một lần refactor không ai yêu cầu.** Boy Scout Rule chỉ áp dụng cho dòng bạn đang đụng, không cho cả file.
- **`Done when` viết bằng tính từ thì không nghiệm thu được.** "Nhìn ổn hơn" không phải tiêu chí; "canh giữa ở cả 16:9 và 19.5:9" mới là.

## Trước khi gửi

- [ ] Dòng `Task kind:` chỉ còn đúng một giá trị.
- [ ] `Entry point` là đường dẫn có thật, không phải mô tả.
- [ ] `Do not touch` có nội dung, không phải "không có gì".
- [ ] `Done when` là thứ bạn tự chạy được, không cần hỏi lại Claude.
- [ ] Không còn `[` và không còn tag rỗng.

## Sau khi nhận trả lời

- [ ] Nếu Claude báo một trong bốn tiêu chí escalation áp dụng — **dừng lại**, chuyển sang `single-feature.md`, đừng bảo nó cứ làm tiếp.
- [ ] Chạy đúng câu `Done when` bạn đã viết. Đừng nghiệm thu bằng cách đọc diff.
- [ ] Đọc mục "deliberately left alone" — nó thường chứa việc tiếp theo của bạn.
- [ ] Nếu diff chạm file ngoài `Touch only`, hỏi vì sao trước khi nhận.