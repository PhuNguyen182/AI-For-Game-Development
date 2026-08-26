# Ví dụ: Chỉnh tốc độ zoom camera

Khung `basic-request.md`, `Task kind: tune-a-visible-value`. Giữ `<existing_code>` vì đoạn liên quan rất ngắn; xoá dòng "Không đổi hành vi quan sát được" vì việc CHÍNH LÀ đổi hành vi.

```text
## Objective
Camera zoom bằng cuộn chuột không còn giật hình khi cuộn nhanh liên tục.

Task kind: tune-a-visible-value

## Context
- Entry point: Assets/Scripts/Client/Camera/CameraZoomController.cs
- Platform / version: Unity 2022.3 LTS, PC

<existing_code>
[SerializeField] private float zoomSpeed = 10f;
[SerializeField] private float zoomSmoothTime = 0.05f;
</existing_code>

## Scope
- Touch only: CameraZoomController.cs — hai field zoomSpeed và zoomSmoothTime
- Do not touch: logic raycast hoặc logic input của camera
- Find the same problem elsewhere: ghi ra cuối, không tự sửa.

## Constraints
- Tuân `.claude/rules/client/coding-principles.md` và `naming-convention.md`.
- Không dùng API nào đã đánh dấu `[Obsolete]`.
- Dừng lại và báo tôi TRƯỚC KHI làm tiếp, nếu việc này hoá ra chạm `Game.Core.*`,
  cần nhiều hơn một vai trò, ảnh hưởng multiplayer, hoặc dựa trên thứ tôi chưa
  quyết. Đừng tự lách qua trong im lặng.

## Deliverable
- Diff.
- Mỗi file một dòng nói vì sao nó bị đụng.
- Danh sách những gì bạn thấy và cố ý không đụng tới.

## Done when
Cuộn chuột nhanh liên tục trong Play Mode ở scene MainLevel không còn giật hình khi quan sát qua Scene view trong 10 giây liên tục.
```
