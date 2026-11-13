---
name: testimonial-video
description: 用于“制作客户好评视频”、“将用户评论做成动态视频”、“打造带星级的证言视频 (Social Proof)”、“制作引言背书卡片”或“从评论列表批量渲染好评视频”。基于 clone-any-video 引擎，覆盖阅读顺序逐行错峰入场、关键短语高亮、平滑动态打分（支持 4.5 等小数星级）以及真实人物签署背书。
version: 1.0.0
---

# Testimonial Video (真实客户口碑与好评背书视频)

将一段真实的客户评论、引言或用户评测，转化为 6~12 秒高信任度、排版讲究的社交背书短视频。**核心信条：建立信任优先于炫技动效（Trust before motion）**。克制的字形排版让人感到客观真实，过度花哨的特效反而容易被当作粗制滥造的硬广直接滑过。

基于 `clone-any-video` 引擎，由纯 HTML/CSS/GSAP 构建的高保真组件通过无头 Chrome 逐帧渲染，并与真实的 TTS 旁白严格对其。

---

## 已验证的真实生产入口

使用 [Blender三技能实测案例](../../examples/blender-trilogy/README.md)，完整生产入口：

```sh
# 默认自动检测本地 clone-any-video 引擎及环境配置（亦可显式传入 --env-file /path/to/.env.local）
python3 scripts/build-skill-campaign.py examples/blender-trilogy/campaign.json ./runs/blender-testimonial --video testimonial --output /absolute/path/testimonial.mp4
```

以上命令在技能包根目录运行，默认调用真实TTS与Chrome；先加 `--prepare-only` 检查剧本和关键帧，再用 `--render-only` 继续。素材与事实来源必须可核实。技术通过不替代成片内容审查。


## 三大信任法则

1. **按阅读顺序错峰入场（Reading-Order Reveal）**：
   人眼必须先读完第一行，第二行才紧随其后滑入。按子句/行错峰入场（每行间隔 ~0.2s），严禁所有字无序同时乱跳。
2. **忠实原话（Verbatim Quote）**：
   严禁随意窜改客户原话、杜撰星级或胡乱截断句子。如果要突出重点短语，必须是客户原汁原味的词句。
3. **署名是背书的基石（Author Attribution）**：
   没有真实姓名与身份的引言只是空洞口号。姓名 + 当时职位 + 公司 + 可核验出处是署名基础。头像仅在来源与使用条件明确时加入；否则用文字署名或姓名首字母，不虚构真人照片。没有评分来源时不显示星级。

---

## 证言卡片核心解构

| 视觉元素 | 职责与心理暗示 | 动效节奏 |
| :--- | :--- | :--- |
| **引言大引号 (“)** | 视觉锚点：在观众看清文字前即刻认知“这是真实引言” | 第 0 帧，微缩放并淡入 |
| **评述正文** | 客户评述本身，逐行递进展开 | 错峰平滑滑入（偏移 ~20px） |
| **高亮重点词** | 传达最有商业说服力的核心结果（例如“节省2天时间”） | 在所在行稳定后点亮黄色/强调色 |
| **动态星级打分** | 权威评分背书，支持精准小数填充（如 4.8 星） | 在引言之后由左至右平滑点亮 |
| **作者身份栏** | 真实背书人姓名、职位、公司与头像 | 最后上浮固定，为全片画下句号 |
| **长静态定格** | 画面完全静止，让观众有充分时间读完并信任 | 占全片后半程（≥3~5 秒） |

---

## clone-any-video 工作流

1. **SVML 剧本描述**：
   ```xml
   <script id="testimonial_sarah">
     <quote_lead><HOST>We cut our reporting cycle from two days down to 15 minutes.</quote_lead>
     <quote_detail><HOST>Our whole team cannot imagine going back.</quote_detail>
     <author_signoff><HOST>Sarah Chen, VP of Product Operations at FinTech Global.</author_signoff>
   </script>
   ```

2. **Web-as-Video 渲染**：
   使用 `templates/quote-card/index.html` 模板，传入客户名字、星级与引言，由 Chrome CDP 无损捕获为 1080×1920 透明图层。

3. **终审与压制**：
   音频由真实 TTS 朗读，背景叠加品牌质感微动视频，单次压制输出交付。
