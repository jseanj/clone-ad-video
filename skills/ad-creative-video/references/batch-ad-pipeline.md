# Batch Ad Pipeline

## 可运行的完整任务图

`scripts/batch-ad-matrix.py` 为每行 CSV 生成：

- 五段合法 SVML，包含 Hook、Context、Payoff、Proof、Outro。
- `layout.json`：设计时间轴、尺寸、五个镜头与五个语音窗口。
- 五张自包含动态 HTML 卡片，以 `window.renderFrame(frame, progress)` 确定性驱动。
- Author / Run：五段配音 → 实测时长 realign → mix；五张卡片 render-html → compose → review。

`final.video` 引用 `compose.video`，`final.review` 引用 `review.report`。HTML 是显式任务输入，文案或样式修改会参与缓存失效。

卡片录制 30 帧：前 20 帧入场，随后保持。镜头使用显式 `sampling.shortage: hold` 延长最后一帧至对应实测配音结束。设计时间轴为 25 秒，最终长度由五段实际配音决定，不保证恰为 25 秒。段落级对齐不代表词级声学对齐。本示例无额外 BGM、音效或词级字幕。

## 执行

在技能包根目录：

```bash
python3 scripts/batch-ad-matrix.py examples/ad-creative-batch/variants.csv ./output_runs --aspect 9:16 --test-field hook
mkdir -p output
for run in output_runs/*/*.run.json; do
  ./scripts/cav-runner.sh build "$run" --mock --output "output/$(basename "$(dirname "$run")").mp4"
done
```

`--mock` 运行全任务图并实际编码，但配音和画面是合成测试夹具，不会呈现 HTML 的广告样式，不可作为正式广告。正式模式去掉 `--mock`，需要配置引擎支持的真实 TTS Provider 与凭据，并安装 Chrome、FFmpeg。Mock 构建成功不证明真实 TTS 可用。

源目录自带 `examples/ad-creative-batch/run.json`，可直接运行单条完整示例：

```bash
./scripts/cav-runner.sh plan examples/ad-creative-batch/run.json --mock
./scripts/cav-runner.sh build examples/ad-creative-batch/run.json --mock --output output/master.mp4
./scripts/probe-mp4.sh output/master.mp4 1080x1920 30
```

Result 路径由 build 输出，其中含 review 报告路径。Review 只给出技术和来源结论；正式交付仍需检查文案、可读性、事实主张和实际平台遮挡。`probe-mp4.sh` 仅检查视频物理规格，不检查画面安全区。

## 单变量约束

`--test-field hook` 校验其余文案、CTA、强调色和背景色相同，允许 id 不同。示例五组 Hook 均围绕“省下两小时”，固定同一 CTA。省略此参数可以生成多套创意方向，但不应宣称为单变量测试。真实 TTS 会使不同 Hook 的实际时长发生变化；需要严格控制曝光时长的实验，应另做等长剪辑设计。

示例收益数字为演示文案，不是已核实的产品承诺。

## 独立检查 HTML

```bash
./scripts/cav-runner.sh capture screenshot --input examples/ad-creative-batch/hook_card.html --frame 29 --width 1080 --height 1920 --to output/hook.png
./scripts/cav-runner.sh capture record --input examples/ad-creative-batch/hook_card.html --total-frames 30 --width 1080 --height 1920 --fps 30 --to output/hook.mp4
```

本机独立 CLI 默认透明，MP4 实测使用 PNG 编码；需要通用播放时用 FFmpeg 转为 H.264。生成 DAG 的 render-html 配置显式 `transparent: false`，直接输出 H.264。

不要使用旧的 `capture render --html --output` 命令。所有详细参数以本地 `--help` 为准。

## 使用现有 MiMo / Flow 配置

```bash
python3 scripts/batch-ad-matrix.py examples/ad-creative-batch/variants.csv output_runs --aspect 9:16 --test-field hook --voice 冰糖
# 自动读取当前环境或引擎下的 .env.local（亦可通过 CAV_ENV_FILE 指定独立配置）
./scripts/cav-runner.sh build output_runs/hook_problem/hook_problem.run.json --output output/mimo-ad.mp4
```

`--voice` 必须使用 Provider 支持的音色；默认 `alloy` 面向 OpenAI，MiMo 可指定“冰糖”。runner 默认读取引擎目录的 `.env.local`，也可通过 `CAV_ENV_FILE` 选择已有配置，不复制密钥。上面仍是卡片广告，Flow 背景需要在 Author 中显式声明 image/video 任务和对应轨道，不能因环境设置 IMAGE_PROVIDER 就认为已生成图片。
