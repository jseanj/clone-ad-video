# Batch Reviews to Videos — 批量客户口碑自动化流水线

用于将客服系统、Trustpilot、App Store 或 G2 导出的用户好评 CSV，一键批量生产为成套的背书视频短片。

---

## 一、 输入数据表格格式 (reviews.csv)

```csv
id,name,role,company,quote,highlight,rating
rev_01,"Alex Rivera","CTO","CloudPulse","Deployment times dropped by 70%. Best dev tool we adopted this year.","dropped by 70%",5.0
rev_02,"Elena Rostova","Head of Growth","SaaSify","Our ad ROAS went from 1.4 to 3.8 in under three weeks.","ROAS went from 1.4 to 3.8",4.9
rev_03,"Marcus Vance","Lead Architect","Veloce AI","Zero pipeline breaks across 10 million transactions. Pure engineering joy.","Zero pipeline breaks",4.8
```

---

## 二、 自动化生产批处理脚本

编写 Python 或 Shell 脚本，遍历 CSV：
1. 替换 `templates/quote-card/index.html` 中的姓名、引言、星级。
2. 生成对应的 SVML 朗读剧本。
3. 调度 `clone-any-video` 完成声音配音与透明图层录制。
4. 压制合成输出 `out/rev_01.mp4`, `out/rev_02.mp4`...

```bash
# 本仓库已验证的真实证言案例；reviews.csv不能交给广告文案CSV编译器。
python3 scripts/build-skill-campaign.py examples/blender-trilogy/campaign.json ./review_runs/blender --video testimonial --output /absolute/path/testimonial.mp4
```

批量真实评论需先适配为证言案例结构，逐条保存原文、姓名、身份、日期与来源链接。上面的Alex等CSV只是格式占位，不能当作真实客户评价发布。
