<!--
 HOW TO USE
 1. Copy the Skeleton block below into your message to Claude Code.
 2. Keep EXACTLY ONE of <repro_steps> / <no_known_cause> / <regression_bisect>.
    Which one depends on how much you know, not on how big the bug is.
 3. Fill every [bracketed] slot; delete any line whose slot does not apply.
 4. Run the pre-send checklist at the bottom of this file.
 Shared rules for all templates: ./README.md
-->

# Bugfix & Debug

Khung cho lỗi **tái hiện được**. Ba khối tuỳ chọn ứng với ba mức thông tin bạn đang có:

| Bạn biết | Khối |
|---|---|
| Bấm đúng chuỗi thao tác là lỗi ra, mọi lần | `<repro_steps>` |
| Tái hiện được nhưng không biết vì sao | `<no_known_cause>` |
| "Trước đây chạy tốt" | `<regression_bisect>` |

Chọn nhầm khối thì Claude sẽ đoán — và một giả thuyết trình bày tự tin tốn thời gian hơn cả việc không có giả thuyết nào.

## Khi nào dùng khung này

| Dùng khi | Không dùng khi |
|---|---|
| Lỗi tái hiện được, kể cả phải làm đúng chuỗi thao tác | Lỗi thỉnh thoảng mới ra — dùng `rare-case.md` |
| Lỗi đến từ máy bạn hoặc máy trong studio | Lỗi đến từ telemetry người chơi — dùng `rare-case.md` |
| Hành vi đúng đã được xác định | Chưa rõ hành vi đúng là gì — đó là câu hỏi thiết kế, không phải bug |

## Lane và chi phí

- Lỗi trong thứ **lane trực tiếp đã dựng** → sửa trực tiếp, 0–1 lượt. Không có spec để đối chiếu, nên không có gì để tính là "vi phạm spec".
- Lỗi trong thứ **pipeline đã dựng và spec vẫn còn hiệu lực** → `.claude/workflows/feature-development.md` E3, 3 lượt, có đếm strike.
- `<no_known_cause>` và `<regression_bisect>` thường tốn 1–3 lượt cho riêng phần điều tra.

## Skeleton

```text
## Objective
Fix [one-sentence description of the fault].

## Evidence
- Expected: [what should happen] — source: [spec clause | GDD scenario | my expectation]
- Actual:   [what happens — stated as observed behaviour, not as a diagnosis]
- Frequency: [x out of y attempts]
- Environment: [Editor | build | device], [platform], [version]
- First seen: [version / change / date — or "unknown"]

<error_log>
[Paste verbatim: console output, stack trace, assertion text. Do not trim it.
 Delete this whole block when there is no log.]
</error_log>

<repro_steps>
From a known starting state: [scene / save / screen]
1. [step]
2. [step]
3. [step]
Following these steps reproduces it every time.
</repro_steps>

<no_known_cause>
I can reproduce it, but I do not know why.
- It happens when: [conditions]
- It does NOT happen when: [conditions] — this line matters as much as the one above
- Already tried and ruled out: [ ]

Fix nothing this round. Work in this order:
1. List the hypotheses that fully explain the symptom, ranked by likelihood. Any
   hypothesis that cannot explain the "does NOT happen when" line is eliminated —
   say so and drop it.
2. For each one: the cheapest test that rules it out, and which result would prove
   it WRONG.
3. Name any data you need that does not exist yet — a log where, a measurement of what.
Then wait for my go, run the tests in order, report each result, and STOP the moment
the cause is isolated.
Never change two things at once: if two changes together make it go away, neither
one is proven. State a confidence level for every conclusion, and never present a
hypothesis as a finding.
</no_known_cause>

<regression_bisect>
This used to work.
- Last known good: [commit / tag / date / build version]
- Known bad: [commit / tag / HEAD]
- Branch: [ ]
The good/bad test — must be a yes-or-no check, not a judgement call:
[e.g. run test X; or: open scene Y, press Z, health must read 80]

<git_status>
[paste the output of `git status`]
</git_status>

- Create a safety anchor BEFORE touching anything.
- Do not push, do not force, do not rewrite published history.
- Ask me before any command that could lose work.
- This is a Unity repo: a .meta file or a YAML scene/prefab can be the culprit,
  not only a .cs file.
Return the culprit commit, the part of its diff that actually causes this, the
mechanism by which it does, and the exact commands you ran so I can repeat them.
</regression_bisect>

## Scope
- Fix the root cause, not the symptom. If only a symptomatic patch is possible, say
  so plainly and name where the real cause lives.
- Do not refactor the surrounding code. Note anything else you find, at the end.
- I suspect [file] — verify that before trusting it, and tell me if I am wrong.

## Constraints
- Follow `.claude/rules/client/coding-principles.md`.
- Do not weaken or delete an existing test to make this pass.
- Do not leave debug logging behind: remove it, or gate it behind an editor-only helper.

## Deliverable
1. The root cause, in one sentence.
2. The diff.
3. Why this got this far — which test or check would have caught it.

## Done when
Following the steps above no longer reproduces it, [related behaviour] still works,
and — where the fault sits in testable logic — a test now covers it.
```

## Optional blocks

| Khối | Giữ khi | Xoá khi |
|---|---|---|
| `<error_log>` | Có log, stack trace, hoặc assertion | Lỗi im lặng, không sinh output nào |
| `<repro_steps>` | Bạn tái hiện được ổn định và biết đủ để nghi ngờ chỗ nào | Hai khối kia áp dụng |
| `<no_known_cause>` | Tái hiện được nhưng không có giả thuyết nào đứng vững | Hai khối kia áp dụng |
| `<regression_bisect>` | Có một mốc còn đúng và một mốc đã sai | Chưa bao giờ chạy đúng |
| `<git_status>` (bên trong) | Luôn giữ khi dùng `<regression_bisect>` | — |

## Cạm bẫy

- **Thiếu `Expected` thì Claude phải tự suy ra ý bạn — và nó sẽ sửa cho khớp với suy đoán đó.** Ba dòng Expected / Actual / Evidence là mức tối thiểu để một phát hiện được coi là báo cáo được, theo `.claude/rules/qa/defect-reporting.md`.
- **Viết `Actual` dưới dạng chẩn đoán là đóng khung câu trả lời từ đầu.** "Cache bị sai" là chẩn đoán; "HP hiển thị 100 trong khi log ghi 80" là quan sát.
- **"Không tái hiện khi…" là dữ kiện mạnh nhất bạn có.** Nó loại được nhiều giả thuyết hơn cả điều kiện tái hiện, nhưng hầu như không ai nghĩ tới việc viết ra.
- **Không có phép kiểm dạng có‑không thì không bisect được**, và mọi thứ tụt về đọc diff bằng mắt. Mười phút viết ra bước kiểm là phần đáng giá nhất của `<regression_bisect>`.
- **Sửa hai chỗ cùng lúc rồi hết lỗi nghĩa là bạn không biết chỗ nào là nguyên nhân.** Lỗi sẽ quay lại khi một trong hai chỗ bị đụng lần sau.

## Trước khi gửi

- [ ] Đúng một trong ba khối chẩn đoán còn lại.
- [ ] `Expected` có ghi nguồn, không chỉ là ý bạn muốn.
- [ ] `Actual` mô tả quan sát, không mô tả nguyên nhân.
- [ ] `Frequency` có con số, kể cả khi là "10/10".
- [ ] Với `<no_known_cause>`: dòng "does NOT happen when" đã điền, không bỏ trống.
- [ ] Với `<regression_bisect>`: phép kiểm trả lời được bằng có/không, và đã dán `git status`.

## Sau khi nhận trả lời

- [ ] Chạy lại **đúng** các bước bạn đã viết. Đừng nghiệm thu bằng cách đọc diff.
- [ ] Đọc mục "why this got this far" — đó là chỗ bịt lỗ hổng, không chỉ sửa một lỗi.
- [ ] Nếu Claude nói chỉ vá được triệu chứng: ghi nhận nguyên nhân thật thành việc riêng ngay, đừng để nó trôi.
- [ ] Với `<no_known_cause>`: kiểm tra nó có nêu mức chắc chắn không. Kết luận không có mức chắc chắn là giả thuyết đội lốt.
- [ ] Kiểm tra không còn `Debug.Log` tạm nào sót lại trong diff.
