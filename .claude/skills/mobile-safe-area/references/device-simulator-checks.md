# Device Simulator checks

Sources, below the `Docs:` base: [a] `script-reference/unityengine/screen/safearea`, [b] `script-reference/unityengine/screen/cutouts`, [c] `script-reference/unityengine/device/screen`, [d] `manual/platform-specific/cross-platform-features/device-simulator/introduction`, [e] `.../device-simulator/view`, [f] `.../device-simulator/adding-a-device`, [g] `manual/upgrade-guides/upgrade-guide-unity65` (6000.5). Elsewhere: [h] https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/script-SafeArea.html, [i] https://docs.unity3d.com/Manual/UpgradeGuide20211.html.

## Screen API

| Subject | Fact that decides |
|---|---|
| `Screen.safeArea` | `Rect` in pixels, relative to the application window (not the physical screen), origin bottom-left; largest value is `Rect(0, 0, Screen.width, Screen.height)` [a] |
| Change notification | None: the property is read-only and has no event, so the fitter compares cached values [a] |
| `Screen.cutouts` | `Rect[]` in pixels of areas that display no content [b]; same bottom-left origin as `safeArea` (the 7000.0 `safeArea` page tells UI Toolkit users to invert both) |
| Android 14 (API 34) and earlier | With `PlayerSettings.Android.renderOutsideSafeArea` off, Unity shrinks the window to the safe area, so `safeArea` usually equals the full window [a] |
| Android 15 (API 35) and later | `renderOutsideSafeArea` has no effect: the app always renders into the cutout and `safeArea` excludes it [a] |
| Unity 6.5+ Android | `renderOutsideSafeArea` now controls only cutout rendering; status/navigation bar visibility moved to `AndroidApplication.currentWindowInsets.Show`/`Hide`; `Screen.fullScreen` no longer affects Android [g] |
| `UnityEngine.Device.Screen` | Same members as `Screen`, mimics the simulated device in the Editor; simulation is stripped from builds, no runtime cost. `safeArea`, `cutouts`, `orientation`, `width`, `height` are simulated; `brightness`, `sleepTimeout`, `mainWindow*` are not [c] |
| uGUI Safe Area component (uGUI 2.6.0+) | Sets `anchorMin`/`anchorMax` from the normalized safe area, zeroes offsets, updates when `safeArea`, resolution or orientation changes. Fields: Reference Orientation, Edges (Top/Right/Bottom/Left), Alignment (Center Horizontally/Vertically applies the larger inset to both sides). Conflicts with a Layout Group, Content Size Fitter or anchor animation on the same or a parent object [h] |

**Caveat:** the Manual's UI Toolkit snippet on [a] builds `Rect(x, Screen.height - y, w, h)`. In top-left space `Screen.height - y` is the bottom edge of the safe area, not its top. Use `Screen.height - safeArea.yMax` for the top.

## Simulator

| Subject | Fact that decides |
|---|---|
| Availability | Built into the Editor since 2021.1, opened from the Game view, no package [i] |
| Open | Game view drop-down (top left) → Simulator, or Window > General > Device Simulator [e] |
| Simulates | Auto-rotation, screen safe area, single-finger touch (Play mode only); reacts like a device to Player Settings Fullscreen Mode, Resolution Scaling, Default Orientation, Graphics API, Render outside safe area [d] |
| Does not simulate | Performance, memory, rendering capabilities, Editor-incompatible native plugins, platform defines such as `UNITY_IOS`, gyroscope, multitouch [d] |
| Safe Area toggle | Draws a line around the simulated device's safe area [e] |
| Rotate | Rotates the device; the screen follows only when auto-rotation is enabled and the device supports that orientation [e] |
| Control Panel | System Language sets `Device.Application.systemLanguage` (startup-locale check); On Low Memory fires `lowMemory` [e] |
| Custom device | `.device` JSON. Required: `friendlyName`, `version` (1), `screens[]` with `width`/`height`/`dpi`, `systemInfo.operatingSystem`. `safeArea` and `cutouts` sit per entry in `orientations`; omitting `orientations` means all orientations and a full-screen safe area. Overlay PNG needs Read/Write enabled or notch input masking fails [f] |

## Check matrix

| Check | Pass when |
|---|---|
| Each target device × each shipped orientation | Safe Area line on; no interactive or text element crosses it; backgrounds reach every screen edge |
| Landscape, rotate 180° | The inset moves to the other side; resolution is unchanged, so a fitter that compares only `width`/`height` fails here |
| Device without a notch (16:9) | Content root equals the full screen; no stray inset |
| Tablet (4:3), if tablets ship | Layout holds at the widest aspect; insets limited to the home indicator |
| Target device missing from the drop-down | Add a `.device` file with its per-orientation `safeArea` and `cutouts` from the vendor spec |

**Caveat:** a Simulator pass proves layout only. Gesture-bar taps, Android 14 vs 15 cutout behaviour and OEM inset quirks need the device (`device-test-walkthrough`).

Unverified: whether the uGUI Safe Area component reads `UnityEngine.Device.Screen` (reacts in the Simulator outside Play mode); whether the Simulator models the Android 15 always-render-into-cutout rule; which Editor release first bundles uGUI 2.6.0; the `cutouts` origin is stated only on the 7000.0 page.
