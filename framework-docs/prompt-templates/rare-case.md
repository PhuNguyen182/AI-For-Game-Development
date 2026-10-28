<!--
 HOW TO USE
 1. Copy the Skeleton block below into your message to Claude Code.
 2. Keep <intermittent_evidence> OR <production_telemetry> depending on where the
    report came from. <determinism_audit> is an ADD-ON — keep it alongside either
    one when two runs disagree with each other.
 3. Fill every [bracketed] slot; delete any line whose slot does not apply.
 4. Run the pre-send checklist at the bottom of this file.
 Shared rules for all templates: ./README.md
-->

# Rare Case

Khung cho lỗi **không tái hiện theo ý muốn**: race condition, thứ tự khởi tạo, phụ thuộc frame rate, trạng thái tích luỹ sau nhiều giờ chơi, desync, hoặc crash đến từ máy người chơi.

Đặc điểm chung: bạn không bấm ra được lỗi, nên **kỷ luật về bằng chứng quan trọng hơn kỹ năng code**. Mọi kết luận phải đi kèm mức chắc chắn, và "chưa kết luận được" là một kết quả hợp lệ chứ không phải một thất bại.

## Khi nào dùng khung này

| Dùng khi | Không dùng khi |
|---|---|
| Lỗi thỉnh thoảng mới ra, tỉ lệ dưới 100% | Tái hiện ổn định — dùng `bugfix-debug.md` |
| Lỗi đến từ telemetry, bạn không có máy đó | Lỗi trên máy bạn — dùng `bugfix-debug.md` |
| Hai lần chạy cho hai kết quả khác nhau | Kết quả sai nhưng nhất quán — đó là logic sai, không phải lỗi hiếm |

Đừng đưa lỗi hiếm vào `bugfix-debug.md`: khối `<repro_steps>` ở đó giả định lỗi ra mỗi lần, và giả định sai đó làm hỏng toàn bộ phần còn lại.

## Lane và chi phí

Lane điều tra, 1–3 lượt. Khung này **không sửa code** — nó cho ra danh sách nghi phạm, cách ép tái hiện, và bộ log cần thêm. Việc sửa đi qua `bugfix-debug.md` sau, khi lỗi đã tái hiện được theo ý muốn.

## Skeleton

```text
## Objective
Investigate [symptom]. This is a RARE fault — do not assume it reproduces on demand.
Fix nothing this round.

## What is known
- Observed rate: [x out of y], on [Editor | build | device]
- Last seen: [when, doing what]
- Seems more likely when: [heavy load / just after scene load / many players /
  long sessions / poor network / low-end device]
- Never seen when: [ ]
- Scattered evidence: [logs, screenshots, player reports]

<intermittent_evidence>
Source: our own testing, or studio reports.
Work in this order:
1. Classify the suspicion: race condition, init/teardown ordering, frame-rate or
   timestep dependency, state accumulating over time, a leak, uninitialised data,
   or non-determinism. For each: which mechanism in THIS codebase could produce it.
2. Point at code that has the conditions for that class to occur — path:line, with
   the reason. This is reading, not fixing.
3. Propose how to make it MORE likely, so we can catch it: force an ordering, inject
   latency, run the path N times, pin a seed, raise the load.
4. Propose where to put logging or assertions so the NEXT occurrence carries evidence,
   even if we cannot catch it today.
</intermittent_evidence>

<production_telemetry>
Source: real players.
- Channel: [Play Console vitals | Crashlytics | App Store Connect]
- Rate: [% of sessions or users], app version [ ], since build [ ]
- Device or OS concentration: [ ]
- Correlates with: [low memory / a GPU family / a region / cold start]
- Symbol state: [symbolicated | not symbolicated | no symbol file]

<telemetry_excerpt>
[Paste the stack trace or report verbatim. Do not trim it.]
</telemetry_excerpt>

Three stages. Stop after each one and wait:
1. FAULT DOMAIN — our code, a third-party SDK, the engine, or the device/driver?
   State which evidence points there, and which evidence would refute it.
2. ROOT CAUSE — the concrete mechanism, with a confidence level. If the trace is not
   symbolicated, say what is needed to symbolicate it rather than guessing from
   obfuscated names.
3. HANDOFF — which agent-id owns the fix, the severity by impact if left alone, and
   which metric at which threshold confirms it is gone in the next build.
Correlation is not cause. Mark every place where you are inferring rather than observing.
</production_telemetry>

<determinism_audit>
Add-on: keep this when the symptom is a disagreement between two runs, two machines,
or client and server.
Audit `Game.Core.*` for every source of non-determinism:
- `UnityEngine.Random`, or any RNG whose seed is not injected
- wall-clock time or frame-time reads
- collection iteration whose order is not guaranteed
- float operations that can diverge across platforms or architectures
- anything read from Unity state instead of being passed in already resolved
Report each hit as path:line, and say whether it can actually affect the outcome
or is harmless in context.
</determinism_audit>

## Scope
- Investigate only. Change no production code this round.
- Do not widen this into a general audit of nearby systems.

## Constraints
- Do not claim it is fixed unless you reproduced it first and then made it stop.
  "I changed something and have not seen it since" is not evidence for a fault that
  was rare to begin with.
- Every conclusion carries a confidence level and the evidence behind it.
- "Not conclusive yet, here is the next step" is a valid and expected answer.
- Do not report the single run that supports the theory. Report what all runs showed.

## Deliverable
A ranked suspect list, how to force reproduction, the logging and assertions to add,
and a confidence level per item.
[In the telemetry case: plus fault domain, root cause, severity, and one owner.]

## Done when
The next time this occurs, I have enough data to conclude — even if we did not catch
it today.
```

## Optional blocks

| Khối | Giữ khi | Xoá khi |
|---|---|---|
| `<intermittent_evidence>` | Lỗi phát hiện trong studio: QA, playtest, máy dev | Nguồn là telemetry người chơi |
| `<production_telemetry>` | Lỗi đến từ Play Console / Crashlytics / App Store Connect | Nguồn là máy trong studio |
| `<telemetry_excerpt>` (bên trong) | Có stack trace hoặc báo cáo để dán | Chỉ có số liệu tổng hợp |
| `<determinism_audit>` | Hai lần chạy khác nhau, hoặc client và server bất đồng | Lỗi xảy ra nhất quán trên một máy |

`<determinism_audit>` là **add-on**, không loại trừ hai khối kia. Desync multiplayer thường giữ cả `<intermittent_evidence>` lẫn `<determinism_audit>`.

## Cạm bẫy

- **"Sửa xong không thấy nữa" không phải bằng chứng cho một lỗi vốn dĩ hiếm.** Với tỉ lệ 1/50, không thấy trong 20 lần chạy là điều bình thường kể cả khi chưa sửa gì.
- **Stack trace chưa symbolicate mà vẫn suy ra nguyên nhân từ tên hàm còn sót là cách nhanh nhất để cả đội đi sai hướng một tuần.** Bắt nó nói cần gì để symbolicate, thay vì để nó đoán.
- **Tương quan không phải nguyên nhân.** "Toàn xảy ra trên máy RAM thấp" có thể là nguyên nhân, cũng có thể chỉ là nơi một lỗi có sẵn lộ ra sớm hơn.
- **Dòng "Never seen when" bị bỏ trống là bỏ mất công cụ loại trừ mạnh nhất.** Giả thuyết nào không giải thích được nó thì bị loại ngay, miễn phí.
- **Sửa ngay khi mới có nghi ngờ là cách mất luôn cơ hội xác nhận.** Nếu chưa ép tái hiện được, việc cần làm là thêm log — không phải thêm fix.

## Trước khi gửi

- [ ] Đúng một trong hai khối nguồn còn lại; `<determinism_audit>` giữ hay xoá là quyết định riêng.
- [ ] `Observed rate` có con số, không phải "thỉnh thoảng".
- [ ] `Never seen when` đã điền.
- [ ] Với telemetry: đã ghi rõ trạng thái symbol, và đã dán nguyên văn stack trace.
- [ ] Dòng "Fix nothing this round" còn nguyên.
- [ ] Không còn `[` và không còn tag rỗng.

## Sau khi nhận trả lời

- [ ] Kiểm tra mỗi kết luận có mức chắc chắn không. Kết luận không có mức chắc chắn là giả thuyết đội lốt.
- [ ] Thực hiện phần "logging và assertions" **ngay cả khi** lần này chưa bắt được lỗi — đó là thứ trả tiền ở lần xảy ra sau.
- [ ] Với telemetry: xác nhận có đúng một chủ sở hữu, và có một chỉ số để biết bản sau đã hết chưa.
- [ ] Nếu `<determinism_audit>` trả về hit trong `Game.Core.*`: đó là lỗi kiến trúc, không phải lỗi cục bộ — đưa lên đúng cấp.
- [ ] Khi lỗi đã ép tái hiện được ổn định, chuyển sang `bugfix-debug.md`. Đừng sửa từ trong khung này.
