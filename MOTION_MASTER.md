# 连续动效母版交付记录

日期：2026-11-13。

## 结果

`report-flow.mp4`：15.933秒，478帧，1080×1920，恒定30fps，H.264，48kHz双声道。

全部通过 `clone-any-video` 原生工具执行：真实MiMo配音、真实Chrome连续逐帧捕获、mix混音、media prepare-audio母带处理、compose合成、review审查。没有使用Remotion或Mock。

视觉参考为原包展示页的海报大字、错层运动、色带转场、数字强调和独立尾卡。没有复用其品牌标识，也没有沿用五张同构文字卡。

## 设计变化

- 2H大字撞入、描边GONE、时间环与工作日印章。
- 三张交叠表格，COPY / PASTE / REPEAT错峰入场。
- ONE CLICK揭示、点击波纹、图表生长、完成通知，配有一张已验收Flow场景图作为局部插图。
- 11小时数字计数、爆点印章与节拍标记。
- TAKE IT BACK独立尾卡、14天试用印章、简洁CTA按钮；旁白结束后增加1.5秒停留。
- 原创程序合成120BPM配乐与转场声音，按实测段落边界编排；原生混音根据人声活动避让。

REPORT/FLOW为概念品牌，仪表盘为示意UI，数字为原CSV演示主张，不是对真实产品的核实。

## 源码已写入技能包

根目录：`/Users/stoic/code/skills/clone-ad-video`

新增：

- `templates/kinetic-report/index.html`：完整连续动效母版，数据注入，单一frame时钟，无墙钟或网络动画依赖。
- `scripts/build-motion-ad.py`：真实配音→测量→完整动画录制→音乐/音效混音→响度处理→原生合成与审查。
- `skills/ad-creative-video/references/kinetic-report.md`：视觉职责、生产命令、验收和适用范围。
- `examples/ad-creative-motion/README.md`：重跑入口。
- `tests/test_motion_ad.py`：时间轴、数据注入、旧配音拒绝、原创音频和母题一致性测试。

同步更新主技能、广告技能、README和基础编译器。

## 修正了之前未被技术审查发现的发音问题

此前我误把 `<HOST>` 当作XML容器添加 `</HOST>`。当前引擎使用角色标记语法，闭合标记会混入 spoken_text。新的编译器已修正，并使用真正的引擎AST检验所有段落发音文本与CSV一致。五段MiMo配音已重新生成，旧配音未复用。

旧实测记录也已追加更正。新的复用入口会逐段核对真实来源、音色和发音文本，拒绝带有旧标记或其他文本差异的声音。

## 验证

- 12项测试通过，包含真实引擎AST测试。
- 渲染前查看五段关键帧；渲染后从实际编码成片重新提取五段中点与尾卡进行检查。
- 全片FFmpeg解码无错误；规格检查通过。
- 原生review：`passed: true`、`mode: production`；全部技术检查项Pass，无Warning。
- 实测响度：-16.6 LUFS，true peak -1.9 dBFS，LRA 2.6 LU。上一版响度警告已消除。
- 工程包独立目录原生plan通过，无阻断；重新渲染仅需Chrome/FFmpeg，不调用生成服务。

## 尚未承诺的范围

- 没有可用ASR服务，检查的是TTS请求/解析文本一致性，不冒充独立逐词听审或声学对齐。
- `ready_for_delivery` 保持false，未签署真实品牌、事实主张和正式投放验收。
- 本次重点验收9:16；其他画幅应另做截图验收。
- 配乐是原创程序合成电子节奏，不是Flow或音乐模型生成的歌曲。

## 引擎能力观察

本次没有被引擎能力阻断，无需更换渲染引擎。以下能力可使后续生产更顺畅，当前已由技能脚本分阶段处理：

1. render-html的frames当前需写入固定值；真实配音完成后，外部脚本读取实测项目再编译渲染任务。未来可支持直接绑定project/clock的总帧数。
2. 生产图mix没有目标响度参数；当前外部调用原生media prepare-audio后显式选用母带。未来可增加母带处理Producer。
3. SVML对不支持的角色闭合标记缺少明确诊断，容易把语法误写传入TTS；可增加保留标记校验。

## 可复用交付

- `report-flow.mp4`：最终成片。
- `contact-sheet.png`：从最终编码视频提取的五段关键帧。
- `poster.png`：尾卡大图。
- `motion-master-project.zip`：含真实声音、图片、母版、布局与原生Run，不含密钥；可本地修改画面后重新渲染。
- `review.json` / `facts.json` / `result.json`：审查和执行证据。

修改文案需重新生成或明确验收匹配的配音，不能仅改HTML文字却继续用旧声音。
