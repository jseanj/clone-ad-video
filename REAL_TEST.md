# Flow + MiMo 真实实测记录

日期：2026-11-13。第一组 `hook_problem`，全程未使用 Mock。

## 实际调用与产物

- 配置参照本地引擎 `.env.local`（可通过 `CAV_ENV_FILE` 显式指定），使用当前 clone-any-video 引擎；没有复制或输出密钥。
- IMAGE_PROVIDER / VIDEO_PROVIDER：flowkit；生成一张场景图，再以该图生成一段8秒背景视频。
- Flow 视频：omni_flash，OMNI_VERSION=1.1，360p。实际下载为360×640、24fps、8.043秒。五个段落共享该背景，按镜头独立采样，过短时显式loop。
- TTS_PROVIDER：mimo；模型 `mimo-v2.5-tts`，音色“冰糖”，五段英文真实配音分别生成并测量时长。
- 五张透明卡片由真实Chrome逐帧录制；段落标题入场动画完成后保持。卡片上移以保留电脑主体。
- 实测语音驱动时间轴，原生混音与合成，最终19.20秒、576帧、1080×1920、恒定30fps、H.264、48kHz双声道。
- 所有图片、视频、音频输出在Result中的模式均为production，build结果succeeded。

## 验证

- 原生审查 `passed: true`、`mode: production`。
- 物理规格检查通过，完整FFmpeg解码无错误。
- 已查看生成场景图、背景视频抽帧和成片五个段落中点，文字均出现，CTA完整，画面保留电脑背景。
- 生成请求和返回素材的原生来源记录已保留；后续合成复用首次已成功的图片和五段配音，没有重复提交这些生成任务。

## 实测发现与处理

1. 之前 runner 不读取旧项目配置。已增加 `CAV_ENV_FILE`，也默认支持引擎目录的 `.env.local`。
2. 旧编译器固定Mia音色，不能假设跨Provider兼容。已增加 `--voice`，OpenAI默认alloy，MiMo本次显式使用“冰糖”。仓库示例同步更新，七项回归测试通过。
3. 原生mix产物为-18.5 LUFS，true peak -4.5 dBFS，审查给出轻微响度警告（建议-18..-14 LUFS）。本次保留原始实测结果，尚未增加母带响度归一化步骤。
4. 配置选择360p，所以最终1080×1920包含背景放大，文字层在1080×1920直接渲染；没有宣称背景原生1080p。
5. 本机ASR服务8765未启动，没有进行独立语音转写核验。TTS成功与媒体技术通过不等于逐词听审已经完成。
6. `ready_for_delivery: false`：没有签署完整创意验收。示例收益数字仍为演示主张，无音乐或逐词字幕。

## 交付文件

- `ad-hook-problem.mp4`：完整真实成片。
- `contact-sheet.png`：五段成片关键帧。
- `flow-scene.png` / `flow-background.mp4`：真实生成的场景图与背景视频。
- `narration-mix.wav`：真实配音混音。
- `review.json` / `facts.json` / `result.json`：审查、摘要和原生执行证据。
- `production-project.zip`：无密钥的完整声明工程。重新build会真实调用生成服务。

原始运行工程与回执保留于 `/Users/stoic/Documents/Codex/2026-11-13/wo/work/ad-creative-production`。


## 后续内容核验更正

在连续动效母版制作时，直接核对原始TTS请求发现本记录对应旧版本的 spoken_text 混入 `/HOST>`。原因是编译器把当前原生SVML角色标记误当作XML容器加了闭合标签。之前的技术审查通过不能证明发音内容正确。

当前已修正编译器，新增真实引擎AST与CSV逐段一致性回归测试，并重新生成五段MiMo配音。旧成片保留为问题复现证据；后续应采用 ad-motion-v2 新成片和记录。
