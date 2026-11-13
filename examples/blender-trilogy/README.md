# Blender 真实公开资料：三技能实测案例

三个独立美术方向，均为中文、1080×1920、30fps，真实MiMo配音、原生Chrome逐帧渲染、原创配乐与原生合成。完全使用原生生产链路，无第三方未授权音频或模拟伪装。

| video | 技能 | 设计 |
|---|---|---|
| ad | ad-creative-video | 免费开源主题；动效字体、四类创作流程、原创三维视觉、CTA |
| launch | launch-video | Blender 5.2 LTS版本发布演绎；150BPM，6.4秒Drop，0.8秒蒙太奇，24秒 |
| testimonial | testimonial-video | Ubisoft公开访谈摘录；真实姓名、时任身份、原文日期，12秒，未编造评分 |

全部事实出处见 `campaign.json`。5.2 LTS为2026-07-14发布的特定版本，不声称是当前最新版本。Pierrot Jacquet的引言来自2019年访谈，不是对5.2版本的新评价。

## 执行

在技能包根目录：

```sh
# 默认自动检测本地 clone-any-video 引擎及环境配置（亦可显式传入 --env-file /path/to/.env.local）
python3 scripts/build-skill-campaign.py examples/blender-trilogy/campaign.json ./runs/blender-ad \
  --video ad --output /absolute/path/ad.mp4
```

把 `--video` 换为 `launch` / `testimonial`，并更换输出目录。默认执行真实服务，配音由配置文件中的Provider决定；本案例配置为MiMo“冰糖”。

先检查关键帧可使用 `--prepare-only`。继续使用 `--render-only`，显式读取该目录已接受的配音与实测时长，不重新提交TTS。已存在的输出不可随意用于改过的文案：脚本会核对所有声轨的发音文本与音色。

## 质量要求

- 原生SVML使用 `<HOST>` 角色标记，不使用角色闭合标签。TTS之前核对真实引擎AST。
- 广告根据真实声音实测时长编排；发布片先定乐曲节拍和窗口，超长配音只允许有限的原生保音高调速，重新测量后不得超窗。
- 出处、身份、星级、版本均需要证据；没有星级就不显示，不虚构头像。
- `review.passed`不等于内容已经审查。需要检查关键帧、实际成片、字幕、事实、配乐和媒体来源。
- 这些是独立编辑创作，不是Blender或Ubisoft授权发布的官方广告。片内有明确的非官方标识；文字名称用于指向产品，未使用官方图形Logo。

图示由本模板的Canvas/SVG程序原创绘制，是功能视觉演绎，不是Blender界面录屏或官方作品素材。实际产品功能与所有事实均以官方资料为依据。
