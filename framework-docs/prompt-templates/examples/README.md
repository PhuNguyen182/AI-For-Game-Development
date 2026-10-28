<!--
 HOW TO USE THIS FOLDER
 Mỗi file dưới đây là một ví dụ ĐÃ ĐIỀN ĐẦY ĐỦ cho một trong bảy khung ở ../.
 Không còn [bracket] nào — chỉ còn giá trị cụ thể cho một tình huống Unity giả định.
 Học CẤU TRÚC (khối nào giữ, khối nào xoá, vì sao), không copy nguyên giá trị: dự
 án thật của bạn có tên file, con số và ràng buộc khác.
-->

# Examples

20 ví dụ, chia theo 7 khung trong `../README.md`. Mỗi thư mục con ứng với một khung; tên file trong mỗi thư mục nói rõ khối tuỳ chọn nào ví dụ đó minh hoạ.

## Danh sách

| # | Khung | File | Tình huống | Khối tuỳ chọn minh hoạ |
|---|---|---|---|---|
| 1 | basic-request | [basic-request/01-understand-init-order.md](basic-request/01-understand-init-order.md) | Hiểu luồng khởi tạo GameManager | `Task kind: understand` |
| 2 | basic-request | [basic-request/02-tune-camera-zoom.md](basic-request/02-tune-camera-zoom.md) | Chỉnh tốc độ zoom camera | `Task kind: tune-a-visible-value`, `<existing_code>` |
| 3 | basic-request | [basic-request/03-write-cooldown-label.md](basic-request/03-write-cooldown-label.md) | Viết component hiển thị cooldown | `Task kind: write-something-small`, `<api_contract>` |
| 4 | single-feature | [single-feature/01-settings-sensitivity-slider.md](single-feature/01-settings-sensitivity-slider.md) | Slider độ nhạy chuột | Không khối nào ngoài `<escalation_check>` — lane trực tiếp |
| 5 | single-feature | [single-feature/02-fireball-ability.md](single-feature/02-fireball-ability.md) | Kỹ năng Fireball | `<game_rules>`, `<performance_budget>`, `<process_gates>` |
| 6 | single-feature | [single-feature/03-pvp-revive-mechanic.md](single-feature/03-pvp-revive-mechanic.md) | Hồi sinh đồng đội trong PvP | `<game_rules>`, `<authority_and_sync>`, `<platform_matrix>`, `<process_gates>` |
| 7 | multi-feature | [multi-feature/01-plan-sprint-batch.md](multi-feature/01-plan-sprint-batch.md) | Lập kế hoạch lô 4 tính năng | `Mode: plan-the-batch` |
| 8 | multi-feature | [multi-feature/02-shared-status-effect-foundation.md](multi-feature/02-shared-status-effect-foundation.md) | Dựng nền tảng Status Effect dùng chung | `Mode: build-shared-foundation` |
| 9 | multi-feature | [multi-feature/03-absorb-mana-cost-change.md](multi-feature/03-absorb-mana-cost-change.md) | Hấp thụ thay đổi chi phí mana | `Mode: absorb-a-change` |
| 10 | prototype | [prototype/01-feel-test-dash.md](prototype/01-feel-test-dash.md) | Cảm giác né đòn bằng Dash | `<feel_test>` |
| 11 | prototype | [prototype/02-measurement-spike-addressables.md](prototype/02-measurement-spike-addressables.md) | Đo thời gian load Addressables | `<measurement_spike>` |
| 12 | prototype | [prototype/03-feel-test-combo-buffer.md](prototype/03-feel-test-combo-buffer.md) | Cảm giác input buffer cho combo | `<feel_test>` |
| 13 | from-documents | [from-documents/01-map-crafting-gdd.md](from-documents/01-map-crafting-gdd.md) | Bản đồ yêu cầu Crafting từ GDD | `Mode: map-the-documents`, `<gap_register>` |
| 14 | from-documents | [from-documents/02-implement-crafting-from-map.md](from-documents/02-implement-crafting-from-map.md) | Triển khai Crafting từ bản đồ | `Mode: implement-from-the-map`, `<traceability_contract>` |
| 15 | from-documents | [from-documents/03-map-iap-sdk-doc.md](from-documents/03-map-iap-sdk-doc.md) | Bản đồ yêu cầu IAP từ tài liệu SDK | Nguồn hỗn hợp: Tech Spec nội bộ + tài liệu Google |
| 16 | bugfix-debug | [bugfix-debug/01-repro-input-buffer-bug.md](bugfix-debug/01-repro-input-buffer-bug.md) | Double jump không ghi nhận sau wall dash | `<repro_steps>` |
| 17 | bugfix-debug | [bugfix-debug/02-no-known-cause-ai-stuck.md](bugfix-debug/02-no-known-cause-ai-stuck.md) | Enemy AI thỉnh thoảng đứng khựng | `<no_known_cause>` |
| 18 | bugfix-debug | [bugfix-debug/03-regression-bisect-jump-height.md](bugfix-debug/03-regression-bisect-jump-height.md) | Độ cao nhảy giảm sau một commit | `<regression_bisect>`, `<git_status>` |
| 19 | rare-case | [rare-case/01-intermittent-multiplayer-desync.md](rare-case/01-intermittent-multiplayer-desync.md) | Desync hiếm gặp trong combat PvP | `<intermittent_evidence>` + `<determinism_audit>` |
| 20 | rare-case | [rare-case/02-production-crash-telemetry.md](rare-case/02-production-crash-telemetry.md) | Crash hiếm trên một dòng thiết bị | `<production_telemetry>` |

## Cách đọc một ví dụ

Mỗi file có một câu giải thích ở đầu (khung nào, khối nào được giữ/xoá và vì sao), rồi tới khối ` ```text ` chứa prompt đã điền đầy đủ — copy nguyên khối đó là gửi được, nhưng giá trị bên trong là của tình huống giả định, không phải của dự án bạn.

Ba nguyên tắc xuyên suốt cả 20 ví dụ, đúng như `../README.md` đã nêu:

- Không còn `[bracket]` nào sót lại — mọi chỗ trống đã có giá trị cụ thể hoặc bị xoá cả dòng.
- Khối tuỳ chọn giữ hay xoá TRỌN khối, không để tag rỗng.
- Phần hướng dẫn quy trình bên trong mỗi khối (các bước đánh số, câu "Không cho cả bốn: làm trực tiếp"...) giữ nguyên văn boilerplate — đó là chỉ thị cho Claude, không phải chỗ bạn viết lại; chỉ các dòng dữ liệu (Source, Observed rate, batch table, Behaviour...) là chỗ bạn điền.

## Kiểm tra thư mục này

Chạy khi bạn vừa thêm hoặc sửa một ví dụ.

```bash
D=.claude/docs/prompt-templates/examples

# Không còn bracket nào sót trong bất kỳ ví dụ nào
grep -rn '\[' $D --include='*.md' | grep -v '\.md](' && echo "CÒN BRACKET SÓT" || echo "OK"

# Mỗi ví dụ có đúng một khối ```text
for f in $D/*/*.md; do
  [ "$(grep -c '^```text$' "$f")" = 1 ] || echo "THIẾU/THỪA khối text: $f"
done

# Mọi tag trong mỗi ví dụ có đúng một cặp mở/đóng
for f in $D/*/*.md; do
  awk '/^```/{b=!b;next} b{while(match($0,/<\/?[a-z_]+/)){t=substr($0,RSTART,RLENGTH);print t;$0=substr($0,RSTART+RLENGTH)}}' "$f" \
   | sort | uniq -c | awk -v file="$f" '{if($1%2!=0) print "LỆCH TAG " file ": " $0}'
done
```
