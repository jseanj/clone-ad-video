# Kinetic Report 母版：从卡片演示到连续广告

本母版使用 `clone-any-video` 的原生生产图、Chrome 捕获、mix、media prepare-audio、compose、review。完全基于纯原生 Web-as-Video 技术，不依赖外部前端构建框架或第三方 CDN。

视觉结构采用专业海报大字、交错入场、色带转场、产品揭示和尾卡收束。REPORT/FLOW 为演示品牌，仪表盘为示意 UI，不冒充真实产品界面。

## 五段视觉职责

1. Hook：巨型 2H、描边 GONE、旋转时间环和 WORKDAY 印章。
2. Context：三张错层表格、COPY / PASTE / REPEAT 分步入场。
3. Payoff：ONE CLICK 字体切换、点击波纹、完整仪表盘揭示、柱图生长和任务完成通知。
4. Proof：数字计数、印章爆点、十一条节拍标记；数据读取 CSV proof 的第一个数字。
5. CTA：TAKE IT BACK 三行大字、14天试用印章与独立 CTA；尾段保持至配音结束。

示例为报表工具专用设计，2H、14天试用等视觉母题需要与 campaign 文案一致；其他行业应新建母版，不能直接套用。

## 生产命令

```sh
python3 scripts/build-motion-ad.py examples/ad-creative-batch/variants.csv ./motion_runs/hook_problem \
  --id hook_problem --voice 冰糖 \
  --workspace-image /absolute/path/accepted-workspace.png \
  --output /absolute/path/report-flow.mp4
```

workspace-image 需要引擎认可的真实来源；可使用之前 Flow 生成并验收的图，连同 `.provenance.json` 保留。字体用系统字体，无网络依赖。

`--prepare-only` 先生成真实配音、实测时间轴与 HTML，供截图审查；随后用 `--reuse-preparation /absolute/path/to/result.json` 继续，显式复用本次配音，避免重复调用。`--voice-result` 只接受真实 Result，逐段核对发音文本和音色后选用旧配音，任何不一致立即拒绝。

输出的 HTML 使用 frame / fps 唯一决定每一帧，不使用墙钟、随机动画或 autoplay。动画覆盖整条广告，不再把一秒卡片保持到整段结束。长段落会保留阅读空间，背景与细节继续运动。

## 声音

附带原创程序合成配乐与转场设计音，不是 Mock 音频，也不是第三方歌曲。120 BPM，按实测段落边界重置节奏，切换处配有短上升音和冲击声。原生 mix 根据真实人声活动避让音乐；随后使用原生 media prepare-audio 以 -16 LUFS / -1 dBTP 目标处理母带，再由 compose 输出。

## 审片要求

必须先看各段关键帧和转场，再编码成片。检查文字未裁切、产品/数字与画面一致、尾卡保持时间、人声清楚、音乐不盖人声。Review 的 passed 仅为技术指标，不代表品牌/事实主张和逐词配音已经获得人工批准。

当前没有真实词级声学对齐时，只做已测量的段落对齐，不标注为词级同步。该母版的900×1000设计区域以竖屏为主；其他画幅必须单独截图检查。

## 引擎协议注意事项

`<HOST>` 是当前原生 SVML 的角色标记，不是 XML 容器，不能加 `</HOST>`。闭合标签会污染 spoken_text。编译器会拒绝保留的 SVML 语法字符，并通过真实引擎 AST 测试保证各段 spoken_text 与 CSV 一致。
