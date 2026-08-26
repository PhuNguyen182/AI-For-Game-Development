<!--
 HOW TO USE
 1. Copy the Skeleton block below into your message to Claude Code.
 2. Keep EXACTLY ONE of <feel_test> / <measurement_spike>. Never both.
 3. Fill every [bracketed] slot; delete any line whose slot does not apply.
 4. Run the pre-send checklist at the bottom of this file.
 Shared rules for all templates: ./README.md
-->

# Prototype

Khung cho bản dựng **để vứt đi**. Prototype có đúng một nhiệm vụ: trả lời một câu hỏi rồi biến mất.

Hai loại câu hỏi rất khác nhau, và trộn chúng vào một bản dựng thì không câu nào được trả lời tử tế:

- *"Chơi có sướng không?"* → `<feel_test>`, đầu ra là cảm nhận của bạn.
- *"Cái này có gánh nổi không?"* → `<measurement_spike>`, đầu ra là một con số so với ngưỡng.

## Khi nào dùng khung này

| Dùng khi | Không dùng khi |
|---|---|
| Bạn chưa chắc cơ chế có hoạt động/có vui không | Đã chắc, chỉ cần dựng — dùng `single-feature.md` |
| Cần bằng chứng trước một quyết định khó đảo ngược | Quyết định đã chốt — dùng `single-feature.md` |
| Bạn chấp nhận vứt toàn bộ code này đi | Bạn định giữ lại code — thì đây không phải prototype, đừng gọi nó là prototype |

Câu cuối là câu quan trọng nhất. Nói "prototype" rồi giữ lại code là cách nợ kỹ thuật đi vào dự án mà không ai ký nhận.

## Lane và chi phí

Lane trực tiếp, 1–3 lượt agent. Không Tech Spec, không review gate, không README — đó là điều kiện làm nó rẻ và nhanh, và cũng là lý do code này không được đi vào production.

## Skeleton

```text
## Objective
This is a THROWAWAY PROTOTYPE, not production code.
The one question it exists to answer: [question]

## Context
- Unity version / platform: [ ]
- Sandbox location: [a folder kept separate from production code]
- Input scheme: [ ]
- Placeholder assets I can use: [ ]

<feel_test>
What I must be able to do by hand:
- [action] -> [expected response]
- [action] -> [expected response]
Enough for me to judge it within [N] minutes of play.

Explicitly allowed to cut — I am authorising these in advance:
- Hardcoded values. No ScriptableObject, no config plumbing.
- Placeholder art: primitives, gizmos, debug text.
- No tests, no README, no optimization pass.
- No edge case beyond the actions listed above.

Priority: time to something playable, above everything else.
Expose the values I will want to tune in the Inspector, and list them for me.
After I play it, tell me which parts are worth keeping and which must be rewritten.
</feel_test>

<measurement_spike>
The threshold, stated BEFORE measuring:
- Pass if:  [metric] [operator] [value] on [device / platform]
- Fail if:  [ ]
- If it lands between the two, what I need to know in order to decide is: [ ]

How to measure:
- Scenario: [exactly what is being measured]
- Platform: [real device | Editor — say which, explicitly]
- Runs: at least [N]. Report the spread across runs, not a single number.

Honesty constraints:
- Do not report the best run. Report the range.
- An Editor result is labelled indicative every time it is reported, and never
  stands in for a device result.
- If you cannot measure because [device / asset / access] is missing, return
  Blocked and say what is missing. Do not estimate and present it as measured.

Scope: measure only. No optimization, no architecture, no integration.
</measurement_spike>

## Scope
- Do not touch production code.
- Do not put files inside a real feature folder.
- Do not build abstraction "for later" — there is no later for this code.

## Constraints
- Naming still follows `.claude/rules/client/naming-convention.md`, so I can read it.
- The rest of `coding-principles.md` is suspended inside the sandbox folder. Put one
  line at the top of each file saying so, so nobody mistakes this for production code.

## Deliverable
[A playable scene plus the list of tunable values | a measurement table plus a verdict.]
Plus one line stating what this prototype does NOT answer.

## Done when
[I have played it and formed a judgement | I can make decision X from this table
 alone, without having to measure again.]
```

## Optional blocks

| Khối | Giữ khi | Xoá khi |
|---|---|---|
| `<feel_test>` | Câu hỏi là về trải nghiệm: có vui không, có đã tay không, có đọc được không | Câu hỏi trả lời được bằng số |
| `<measurement_spike>` | Câu hỏi là về giới hạn: có đủ nhanh không, có tải nổi không, có vừa bộ nhớ không | Câu hỏi trả lời bằng cảm nhận |

Đúng một khối. Nếu bạn thật sự cần cả hai câu trả lời, chạy hai lượt riêng — bản dựng để cảm nhận và bản dựng để đo có yêu cầu trái ngược nhau về độ hoàn thiện.

## Cạm bẫy

- **Không nói rõ "throwaway" thì bạn nhận về code production chậm gấp năm lần** cho một thứ có thể bị bỏ ngày mai. Dòng đầu tiên của Skeleton tồn tại vì lý do đó.
- **Prototype thành công là lúc nguy hiểm nhất.** Áp lực "nó chạy rồi, ship luôn đi" rất lớn. Câu hỏi cuối `<feel_test>` cho bạn sẵn câu trả lời cho áp lực đó.
- **Một con số không có ngưỡng đi kèm chỉ là một con số.** Nêu ngưỡng sau khi thấy kết quả thì mọi kết quả đều "có vẻ ổn" — đó là lý do `<measurement_spike>` bắt viết ngưỡng lên trước.
- **Đo trong Editor rồi báo cáo như đo trên máy thật là sai lệch nghiêm trọng nhất trong nhóm này.** Editor không có IL2CPP, không có giới hạn nhiệt, không có GPU của thiết bị.
- **"Blocked vì thiếu thiết bị" là kết quả đúng.** Một con số ước lượng trình bày như đã đo tốn nhiều hơn hẳn một lượt hỏi lại.

## Trước khi gửi

- [ ] Dòng "THROWAWAY PROTOTYPE" còn nguyên.
- [ ] Chỉ còn một trong hai khối.
- [ ] `Sandbox location` là thư mục tách biệt, không nằm trong thư mục tính năng thật.
- [ ] Với `<measurement_spike>`: ngưỡng Pass/Fail đã viết, kèm thiết bị và kịch bản.
- [ ] Với `<feel_test>`: đã ghi rõ những thứ được phép cắt — nếu không, nó sẽ không cắt.
- [ ] `Done when` nói rõ bạn sẽ quyết định gì sau khi có kết quả.

## Sau khi nhận trả lời

- [ ] Đọc dòng "what this prototype does NOT answer" trước khi kết luận bất cứ điều gì.
- [ ] Với `<measurement_spike>`: kiểm tra có dải giá trị không, hay chỉ một con số. Một con số đơn lẻ chưa phải kết quả.
- [ ] Kiểm tra nhãn Editor/thiết bị có được ghi rõ ở mọi chỗ báo cáo số không.
- [ ] Quyết định ngay số phận của code: xoá, hay chuyển thành nợ kỹ thuật có ghi nhận. Đừng để nó nằm im trong repo.
- [ ] Nếu quyết định làm thật: mở `single-feature.md`, đừng nâng cấp prototype tại chỗ.
