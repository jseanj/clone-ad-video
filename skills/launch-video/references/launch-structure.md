# Launch Video 镜头结构指南与音频对齐规范

用于指导在 `clone-any-video` 下完成 15s / 30s / 60s 新品发布 Sizzle 视频的视听工程。

---

## 一、 音频瞬态与剪辑点对齐流程

1. **原曲物理特征分析**：
   使用 `scripts/cav-runner.sh probe <bgm.mp3> --json` 获取音频长度与声道信息。
2. **标定 Drop 物理时间戳**：
   定位音频中能量最高爆发帧（例如 `00:09.12`）。
3. **分配蒙太奇节奏（Montage Pacing）**：
   - 15s 视频：4 个核心镜头，每镜头 ~0.75s。
   - 30s 视频：8~10 个核心镜头，每镜头 ~0.8s~1.1s。
   - 60s 视频：14~18 个核心镜头，分成两波递进高潮。

---

## 二、 Reveal 瞬间的视觉与动效参数

在 GSAP 或 HTML 模板中，Reveal 镜头需要呈现“瞬间砸下”的物理质感：

```javascript
// 配合 clone-any-video 的 Chrome CDP 捕获
const DROP = 9.0; // 秒
const tl = gsap.timeline({ paused: true });

// 预热阶段：逐渐放大，拉升期待感
tl.to(".tease-silhouette", { scale: 1.08, opacity: 1, duration: DROP, ease: "power1.in" }, 0)
// Drop 点瞬间：微过冲放大后砸下收缩
  .set(".product-master", { opacity: 1 }, DROP)
  .fromTo(".product-master", { scale: 1.18 }, { scale: 1.0, duration: 0.18, ease: "power3.out" }, DROP)
  .fromTo(".flash-hit", { opacity: 0.95 }, { opacity: 0, duration: 0.28, ease: "power2.out" }, DROP);
```

---

## 三、 压制与自检

```bash
# 1. 编译工程
./scripts/cav-runner.sh dynamic-timeline script.svml --fps 30 --to timeline.json
./scripts/cav-runner.sh project script.svml --timeline timeline.json --to project.json

# 2. 合成母带与成片
./scripts/cav-runner.sh compose render --project project.json --output out/launch_master.mp4

# 3. 抽查首中尾关键帧
./scripts/contact-sheet.sh out/preview.png \
  out/frames/frame_hook.png \
  out/frames/frame_reveal.png \
  out/frames/frame_end.png
```
