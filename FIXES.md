# ad-creative-batch 修复与验证

日期：2026-11-13。已直接修改 `/Users/stoic/code/skills/clone-ad-video`，未修改 clone-any-video 引擎。

## 对应原问题的修复

1. **输出类型**：`final.video → compose.video`，`final.review → review.report`，支持 `build --output file.mp4`。
2. **完整链路**：CSV 编译出五段配音、实测时长对齐、混音、五张动态卡片、合成与审查，共 14 个任务。HTML 为显式依赖。合法闭合 HOST 标签并转义 XML/HTML 文本。
3. **命令兼容**：文档改用 `capture record --input --to --total-frames`；批量循环遍历真实 Run 文件；修正 compose 参数。runner 使用安全参数传递并支持 CAV_WORKSPACE 覆盖引擎目录。
4. **动态视觉**：五个段落分别展示文案，使用确定性 renderFrame 入场动画；前 20 帧入场，录制 30 帧后保持至实测语音结束。原样 Hook 单卡已替换为完整五卡结构。最终时长随实际配音变化。
5. **单变量示例**：CSV 固定 Context、Payoff、Proof、CTA 和颜色，五组 Hook 均对应“省下两小时”；新增 `--test-field hook` 拒绝其他字段变化。新增空字段、危险/重复 id 和颜色输入校验。

已同步更新 README、主技能、效果广告技能、批量管线说明及关联捕获命令。`examples/ad-creative-batch/run.json` 和配套资源已更新，可直接运行。

## 验证结果

- 六项 unittest 通过：端口类型与依赖、文本转义、单变量约束、输入错误、四画幅布局、仓库示例与生成器一致性。
- 九份原生 Mock plan 无阻断：五组变体、仓库直接示例、额外三种画幅；每份均为 14 个任务。
- 一条完整 Mock build 成功，覆盖所有任务：21.20 秒、636 帧、H.264、1080×1920、恒定 30fps、48kHz 双声道。probe 和完整 FFmpeg 解码通过。
- 原生 review `passed: true`，`mode: mock`；`ready_for_delivery: false` 符合测试产物身份。详见 `fixed-review.json`。
- 真实 Chrome 截图第 0/29 帧成功且画面不同；真实 Chrome 连续录制 30 帧成功，原生 CLI 输出为透明 PNG 编码 MP4，完整解码通过；另行转码为 1 秒通用 H.264 动画，规格检查通过。

## 保留的边界与新观察

- 完整成片本次使用 Mock 画面和测试音频。它用于证明任务链可执行，不呈现真实广告文案，也不是可投放成片。
- `fixed-hook-animation-h264.mp4` 是真实 HTML 的入场动画，无声音；实际广告卡片样式见 `fixed-frame-29.png`。
- 未调用收费 TTS，正式 TTS 凭据、可用音色与端到端正式成片仍需在生产运行时验证。正式模式去掉 `--mock`。
- Mock review 给出响度警告：-20.4 LUFS、true peak -7.5 dBFS，建议区间 -18..-14 LUFS。没有将其隐藏，也未因此更改引擎的混音实现。
- 新观察：独立 capture record CLI 默认透明，MP4 使用 PNG 编码，不能假设为 H.264；已在文档说明。批量 DAG 显式关闭透明，不受影响。
- 本示例无音乐、音效或词级字幕；收益数字为演示文案。平台安全区需人工检查，probe 不做视觉判断。
- 不同 Hook 的实测语音时长可能不同，当前单变量约束校验文案和样式字段，不保证等曝光时长。

## 重跑

在 `/Users/stoic/code/skills/clone-ad-video`：

```sh
python3 -m unittest discover -s tests -v
python3 scripts/batch-ad-matrix.py examples/ad-creative-batch/variants.csv ./output_runs --aspect 9:16 --test-field hook
mkdir -p output
./scripts/cav-runner.sh build examples/ad-creative-batch/run.json --mock --output output/master.mp4
./scripts/probe-mp4.sh output/master.mp4 1080x1920 30
```

输出参考：`fixed-hook-problem-mock.mp4`、`fixed-hook-animation-h264.mp4`、`fixed-review.json`、`fixed-result.json`。


## 连续动效升级与更正

已增加kinetic-report母版及真实生产入口，见MOTION_MASTER.md。先前“合法闭合HOST标签”的修复表述有误：当前原生SVML角色标记不使用闭合标签；现已更正并通过真实引擎AST测试，重新生成五段配音。
