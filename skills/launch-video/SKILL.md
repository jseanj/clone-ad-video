---
name: launch-video
description: 用于“制作新品发布视频”、“打造高能预热宣传片/Sizzle Film”、“制作卡点 Hero Video”、“在音乐 Drop 点 Snap 揭晓产品”或“剪辑快节奏功能蒙太奇”。基于 clone-any-video 引擎，遵循 Sound-design-leads-picture 原则与多尺寸渲染交付。
version: 1.0.0
---

# Launch Video (新品发布与 Hype Sizzle 宣传片)

打造一支 15~60 秒、高能量、卡点精准、富有冲击力的新品发布宣传片。遵循经典的商业叙事弧线：**Hook（抓眼球）→ Tease（悬念预热）→ Reveal（Drop 点重拍揭晓）→ Feature Montage（高频卡点蒙太奇）→ End Card（稳重收口）**。

采用显式节拍表与 Chrome CDP 动态组件捕获，让画面严格按照配乐节奏剪切。本案例使用先行编排的原创乐曲，不冒充对外部歌曲的自动节拍检测。

---

## 已验证的真实生产入口

使用 [Blender三技能实测案例](../../examples/blender-trilogy/README.md)，完整生产入口：

```sh
# 默认自动检测本地 clone-any-video 引擎及环境配置（亦可显式传入 --env-file /path/to/.env.local）
python3 scripts/build-skill-campaign.py examples/blender-trilogy/campaign.json ./runs/blender-launch --video launch --output /absolute/path/launch.mp4
```

以上命令在技能包根目录运行，默认调用真实TTS与Chrome；先加 `--prepare-only` 检查剧本和关键帧，再用 `--render-only` 继续。素材与事实来源必须可核实。技术通过不替代成片内容审查。


## 核心法则

1. **音乐与声音先导（Sound Design Leads Picture）**：
   先锁定配乐曲目，标记重拍瞬态（kick/snare transients）与最关键的 **Drop 爆发时刻**；剪辑和动效必须根据音频节拍点排布，严禁把画面剪完再去套无关配乐。
2. **宁精勿滥（Quality over Quantity）**：
   3 个高质感的特写与动态渲染镜头，远胜 10 个平庸混乱的拼接。
3. **Drop 点 Snap 揭晓**：
   Logo 或产品真容必须在 Drop 发生的瞬间以微过冲（Micro-overshoot，例如 scale 1.15→1.0）+ 闪白冲击（Flash hit）亮相，给观众最强烈的感官确信。

---

## 30s 标准发布片结构

```text
00:00–00:03  【HOOK】   极具视觉冲击力的单帧或微距推进，低音氛围渐起，绝不提前出现 Logo。
00:03–00:09  【TEASE】  光影掠过、机械结构剪影、局部质感；Riser 音效持续升温拉扯张力。
00:09–00:13  【REVEAL】 配乐 Drop 爆发！产品完整亮相，闪白过渡，停留 1.2s 让观众看清。
00:13–00:25  【MONTAGE】高能卡点蒙太奇（~0.8s/shot），一个核心卖点对应一个大字关键词+视觉动作。
00:25–00:30  【END CARD】品牌 Logo + 核心 Slogan + CTA，画面完全静止沉淀，音乐平滑收口。
```

---

## clone-any-video 实现机制

1. **SVML 剧本描述**：
   ```xml
   <script id="aurora_launch">
     <hook><HOST>Speed changed forever.</hook>
     <tease><HOST>Zero latency. Infinite throughput.</tease>
     <reveal><HOST>Meet Aurora Engine.</reveal>
     <montage><HOST>Rust core. Chrome CDP. Single-pass composite.</montage>
     <outro><HOST>Get started at aurora.dev</outro>
   </script>
   ```

2. **音频与 SFX 智能吸附**：
   在明确的Reveal和切镜时刻准备SFX素材或音轨，再交给原生mix混音；mix不会自动猜测音乐Drop位置。

3. **蒙太奇视觉卡片**：
   使用 `templates/feature-montage/` 中的 HTML 组件，无头 Chrome 批量渲染为透明图层，一次性压制到视频主轨。
