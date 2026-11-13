# Quote Card 组件规范与 Chrome CDP 捕获

本文档详述在不使用 Remotion 的前提下，如何用纯 HTML/CSS/GSAP 构建并录制广播级引言卡片。

---

## 一、 为什么使用 HTML + Chrome CDP 捕获？

1. **排版质感**：原生支持现代排版特性（Subpixel 抗锯齿、Kerning 字距、Web Font、CSS Backdrop Filter 高斯模糊）。
2. **确定性时间轴**：通过页面上的 `?t=1.5` 参数，或者通过 CDP `Page.captureScreenshot` / `Emulation.setVirtualTimeBudget` 进行逐帧离线捕获，杜绝掉帧、抖动与不同步。
3. **零框架污染**：不需要 React、Webpack、Babel 或 Remotion 依赖，单文件 HTML 即开即录。

---

## 二、 关键帧时间戳与编排

以 9:16（1080×1920，30fps，8秒）为例：

```text
时间 (s)    帧 (Frame)   动效事件
0.00~0.20   0~6         大引号 motif 放大淡入
0.25~1.10   7~33        引言正文按行错峰滑入 (stagger: 0.22s, y: 24->0)
1.10~1.35   33~40       核心结果高亮色刷亮 (highlight sweep)
1.35~1.60   40~48       星级由左至右点亮，半星精准渐变呈现
1.60~1.90   48~57       作者署名栏（头像、姓名、职位）上浮固定
1.90~8.00   57~240      全体静止定格！给读者从容阅读与截屏时间
```

---

## 三、 使用 clone-any-video 捕获命令

```bash
# 无头 Chrome 逐帧录制透明图层
./scripts/cav-runner.sh capture record \
  --input templates/quote-card/index.html \
  --to out/quote_layer.mov --total-frames 240 \
  --width 1080 \
  --height 1920 \
  --fps 30 \
  --transparent
```
