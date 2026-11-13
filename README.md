# Clone Ad Video (`clone-ad-video`)

> 面向 AI Coding Agent 的商业广告与效果投放视频生产技能包。
> 全面依托 **[clone-any-video](https://github.com/jseanj/clone-any-video)** 确定性媒体引擎驱动。

> [!TIP]
> **前置依赖**：本项目依托 `clone-any-video` 媒体引擎运行。如果本地尚未安装，请跟随官方教程完成安装：
> **[https://github.com/jseanj/clone-any-video](https://github.com/jseanj/clone-any-video)**
>
> 引擎就绪后，可通过将 `clone-any-video` 置于 `PATH`、设置 `CAV_WORKSPACE` / `CAV_BIN` 环境变量，或保持工作区目录同级，脚本将自动探测。

---

## 🌟 核心特性与技术架构

`clone-ad-video` 构建了工业级、确定性的自动化广告视频生产流，全面拥抱纯 Rust 打造的 `clone-any-video` 引擎底座：
1. **语义剧本驱动 (SVML)**：将商业转化漏斗（Hook / Context / Payoff / Proof / CTA）结构化写入 `.svml`，解耦语义叙事与物理秒数，由弹性时间轴根据真实配音时长动态求解对齐。
2. **Web-as-Video 视觉组件化**：使用标准 HTML/CSS/GSAP 打造高保真视觉卡片、动态标语与海报版式，通过 Google Chrome 无头 CDP 协议逐帧录制带透明 Alpha 通道的视频流，零外部框架捆绑，渲染确定且像素级保真。
3. **专业 48kHz 混音与避让**：原生支持旁白与背景音乐的智能动态避让（Ducking -14dB），并在 Sizzle 宣传片的 Drop 点精准对齐 Boom / Flash 冲击音效。
4. **确定性任务图 (Production DAG)**：基于 `author.json` 与 `run.json`，依托内容哈希增量缓存与断点续做，一键将 CSV 矩阵批量并发编译并渲染为数十条 A/B 测试视频。
5. **自动化技术质检**：内置 `review` 与 `probe-mp4.sh`，严密检查音画同步、LUFS 响度与平台安全区。

---

## 📁 目录结构

```text
clone-ad-video/
├── README.md                          # 本项目说明
├── .claude-plugin/                    # Agent 插件标准清单 (plugin.json, marketplace.json)
├── scripts/                           # 核心执行与验证工具链
│   ├── cav-runner.sh                  # clone-any-video 引擎代理执行器
│   ├── batch-ad-matrix.py             # CSV 展开为 SVML 与 Production DAG 的矩阵编译器
│   ├── probe-mp4.sh                   # 视频分辨率/帧率检查脚本 (FFprobe)
│   └── contact-sheet.sh               # 关键帧并排审查预览图拼贴器 (FFmpeg)
├── templates/                         # Web-as-Video 纯 HTML/CSS/GSAP 动态视觉组件
│   ├── hook-title/                    # 0~3s 抓眼球 Hook 标语
│   ├── quote-card/                    # 客户口碑评价卡（错峰滑入、动态打分、人物认证）
│   ├── feature-montage/               # 功能卡点大字与关键指标徽标
│   └── end-card-cta/                  # 尾卡品牌 Logo、Slogan 与 CTA 按钮
├── examples/                          # 开箱即用可运行案例
│   ├── ad-creative-batch/             # 案例 1：效果广告 5 组 Hook 单变量 A/B 测试
│   ├── launch-hype/                   # 案例 2：30s 新品发布 Sizzle 宣传片（Drop 卡点）
│   └── testimonial-proof/             # 案例 3：真实客户引言视频
└── skills/                            # 面向 Agent 挂载的技能定义文档
    ├── clone-ad-video/                # 统领总技能 (Master Ad Skill)
    ├── ad-creative-video/             # 效果广告与单变量测试技能
    ├── launch-video/                  # 产品发布与 Sizzle 宣传片技能
    └── testimonial-video/             # 真实口碑与好评背书技能
```

---

## 🚀 快速上手 (Quick Start)

### 1. 验证 clone-any-video 引擎联通
```bash
./scripts/cav-runner.sh --help
```

### 2. 运行单变量 A/B 测试 CSV 批量展开
```bash
# 将 5 组 Hook 测试变体编译为各自独立的 SVML 和 DAG
python3 scripts/batch-ad-matrix.py \
  examples/ad-creative-batch/variants.csv \
  ./output_runs \
  --aspect 9:16 --test-field hook
```

### 3. 执行快速演练 (Mock 模式) 或正式生产
```bash
# 快速演练模式（真实编码；画面与声音为合成测试夹具）
mkdir -p output
./scripts/cav-runner.sh plan examples/ad-creative-batch/run.json --mock
./scripts/cav-runner.sh build examples/ad-creative-batch/run.json --mock --output output/master.mp4

# 验收输出的 MP4 物理规格
./scripts/probe-mp4.sh output/master.mp4 1080x1920 30
```

---

完整批量命令、实测时长与 Mock/正式模式区别参见 [Batch Ad Pipeline](skills/ad-creative-video/references/batch-ad-pipeline.md)。示例五段均接入配音、动态卡片、混音、合成与技术审查；无额外音乐或词级字幕。收益数字仅为演示文案。

## 🎯 业务支持的 3 类广告形态

1. **[ad-creative-video](skills/ad-creative-video/SKILL.md)**：
   - 痛点直击、认知打破、好奇鸿沟、即时收益、精准点名 5 类 Hook。
   - Hook 与结尾 CTA 严格语义咬合（Message-Match）。
   - 正中心 1:1 安全区自适应重裁剪到 9:16、4:5、1:1、16:9。
2. **[launch-video](skills/launch-video/SKILL.md)**：
   - Hook → Tease → Reveal on the Drop → Feature Montage → End Card 经典弧线。
   - 音乐先导视听（Sound Design Leads Picture）。
3. **[testimonial-video](skills/testimonial-video/SKILL.md)**：
   - 阅读顺位错峰逐行入场。
   - 动态小数星级填充（4.5~5.0 星）。
   - 真实人物与公司认证签名。

## 连续动效母版（需要有设计感的广告时使用）

基础 batch 示例验证任务链；需要海报字体、产品UI揭示、数字动画和声音编排时，使用 [Kinetic Report 母版](skills/ad-creative-video/references/kinetic-report.md)。入口为 `scripts/build-motion-ad.py`，模板在 `templates/kinetic-report/index.html`。仍然完全通过 clone-any-video 的 Chrome / mix / compose 输出。

## 三个技能分别实测

[Blender公开真实资料案例](examples/blender-trilogy/README.md)：效果广告 / 5.2 LTS发布片 / 历史公开访谈口碑片。三条独立设计，真实MiMo声音、原生Chrome和原生混音/合成。入口为 `scripts/build-skill-campaign.py`。所有数据与引言出处存入 `campaign.json`。
