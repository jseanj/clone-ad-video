---
name: ad-creative-video
description: 用于“制作广告视频”、“生成效果广告/信息流创意”、“批量生产 A/B 测试视频变体”、“替换 Hook/CTA 测款”或“将一条广告自适应导出为 9:16/4:5/1:1/16:9”。基于 clone-any-video 引擎，覆盖 5 类 Hook 结构、Hook 与 CTA 语义咬合（Message-Match）、CSV 批量生产 DAG 以及各平台 UI 安全区避让。
version: 1.0.0
---

# Ad Creative Video (效果广告与单变量 A/B 测试)

构建 1 套标准数据驱动的广告工程模型，通过表格/CSV 批量生产 N 个变体——测试不同的 Hook、利益点、Proof 背书与 CTA，帮助效果广告优化师在 Meta Feed、TikTok、Reels 与 YouTube 上进行精确的单变量 A/B 测试。

**技术底座**：彻底剔除 Remotion，全面基于 `clone-any-video` 引擎（SVML 语义剧本 + Web-as-Video Chrome CDP 捕获 + FFmpeg 压制）。

---

## 已验证的真实生产入口

使用 [Blender三技能实测案例](../../examples/blender-trilogy/README.md)，完整生产入口：

```sh
# 默认自动检测本地 clone-any-video 引擎及环境配置（亦可显式传入 --env-file /path/to/.env.local）
python3 scripts/build-skill-campaign.py examples/blender-trilogy/campaign.json ./runs/blender-ad --video ad --output /absolute/path/ad.mp4
```

以上命令在技能包根目录运行，默认调用真实TTS与Chrome；先加 `--prepare-only` 检查剧本和关键帧，再用 `--render-only` 继续。素材与事实来源必须可核实。技术通过不替代成片内容审查。


## 成片设计入口

用户要求有设计感、展示页级别或精致广告时，优先参考 [Kinetic Report 连续动效母版](references/kinetic-report.md)，使用 `scripts/build-motion-ad.py`。这是报表工具的专用示范，可扩展行业母版；不要把五张同构卡片加配音当作完成广告设计。海报大字、产品演示、数字证明、CTA 应承担不同视觉职责，动画覆盖完整时间轴，配乐与转场声音对齐实测段落。

原生 SVML 的 `<HOST>` 是角色标记，不使用 `</HOST>`。在调用TTS之前检查引擎解析出的 spoken_text，保证与原文一致。

## 核心商业法则

1. **单变量隔离（Isolate One Variable）**：
   测试只有在每次只改变 1 个变量时才有解释意义。固定背景视觉风格、色系、动效节奏与时长；仅改变正在测试的字段（如只换 5 组 Hook 文案）。
2. **前后语义咬合（Message-Match）**：
   前 3 秒 Hook 作出的承诺，必须由结尾的 CTA 按钮原样兑现。前置“每天省下 2 小时”，结尾必须是“立即免费试用，省下 2 小时”，绝不使用泛泛的“立即购买”。
3. **安全区核心 1:1 保活**：
   所有关键文字、产品主体与 CTA 必须置于画面正中心的 1:1 方块内。通过切换 `project.json` 中的宽高配置，同一套模板无需黑边（Letterboxing）即可自适应重裁剪到 9:16（竖屏）、4:5（Feed 黄金尺寸）、1:1 与 16:9。

---

## 15~30s 广告结构节奏表

| 节拍 | 时长配额 | 核心任务 | SVML 对应标签 |
| :--- | :--- | :--- | :--- |
| **Hook** | 0–3s | 破冰抓注意力，打破信息流滑动（Scroll-stopper） | `<hook>` |
| **Context** | 3–8s | 激化用户痛点，引发同理心与问题感 | `<context>` |
| **Payoff** | 8–18s | 展示产品作为解法，给出 1 个核心价值 | `<payoff>` |
| **Proof** | 18–25s | 具体的硬核数字、客户背书或成果演示 | `<proof>` |
| **CTA** | 尾部 ≥2s | 强指令、清晰动作、与 Hook 咬合 | `<outro>` |

---

## 5 类经典 Hook 分类表

| Hook 类型 | 句式公式 | 获胜场景 |
| :--- | :--- | :--- |
| **痛点直击 (Problem-first)** | “直到...我才意识到 X 每天耗费我多少时间” | 用户有痛感但尚未总结出解法 |
| **认知打破 (Pattern-interrupt)** | “说出来可能很反直觉，但是...” | 同质化严重的成熟类目 |
| **好奇鸿沟 (Curiosity-gap)** | “几乎没人提过的这 1 个关键技巧...” | 认知较高、警惕心强的专业人群 |
| **即时收益 (Immediate-benefit)** | “7 天内将你的 X 降低一半” | 结果可明确量化的高价值工具 |
| **精准点名 (Direct-callout)** | “如果你每天早上还在做 X，请立刻停下” | 画像清晰的垂直细分受众 |

---

## 批量化生产管线 (CSV × DAG = N 视频)

1. 准备 `variants.csv`，列出测试变体：
   ```csv
   id,hook,context,payoff,proof,cta,accent,bg
   v1,"Spending 2 hrs/day on reports?","Most managers drown in spreadsheets.","One-click live dashboard.","Save 11 hrs/week.","Save 2 Hours — Try Free","#38bdf8","rgba(15,23,42,0.95)"
   v2,"Your reporting tool is lying to you.","Broken syncs cost millions.","Sub-second direct database queries.","99.99% accuracy.","See Real Numbers — Free","#ef4444","rgba(15,23,42,0.95)"
   ```

以上两行演示多创意方向，不能用于单变量实验；使用 `--test-field hook` 时，除 Hook 与 id 外其余字段必须固定。可直接采用仓库 `examples/ad-creative-batch/variants.csv`。

2. 运行矩阵编译脚本，将 CSV 编译为 `clone-any-video` 生产 DAG：
   ```bash
   python3 scripts/batch-ad-matrix.py variants.csv ./output_runs --aspect 9:16 --test-field hook
   ```

3. 使用 `clone-any-video` 进行批量渲染：
   ```bash
   mkdir -p out
   for run in output_runs/*/*.run.json; do
     ./scripts/cav-runner.sh build "$run" --output "out/$(basename $(dirname $run)).mp4"
   done
   ```

详细平台安全区像素规范参见 [platform-specs.md](./references/platform-specs.md)。
完整 DAG 与组件挂载实现参见 [batch-ad-pipeline.md](./references/batch-ad-pipeline.md)。
