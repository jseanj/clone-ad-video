# REPORT / FLOW：连续动效广告示范

入口：`scripts/build-motion-ad.py`。使用同仓库 `examples/ad-creative-batch/variants.csv` 的第一行。

这条母版展示海报大字、表格痛点、示意产品界面、指标计数、CTA收束和声音设计。引擎固定为 clone-any-video，不使用 Remotion。

```sh
# 默认自动检测本地 clone-any-video 引擎及环境配置（亦可显式传入 --env-file /path/to/.env.local）
python3 scripts/build-motion-ad.py examples/ad-creative-batch/variants.csv ./motion_runs/hook_problem \
  --id hook_problem --voice 冰糖 \
  --workspace-image /absolute/path/flow-scene.png \
  --output /absolute/path/report-flow.mp4
```

需要一张已验收且有 `.provenance.json` 的图，可复用之前Flow生成的工作台场景图。该图只用于产品揭示中的局部画面，文字和UI完全由HTML直接渲染。

可先加 `--prepare-only` 检查真实发音和截图；继续时指定 `--reuse-preparation` 为首次准备Result，避免重复配音。

母版固定“2小时 / 每周节省小时数 / 14天试用”的叙事，脚本会拒绝与之矛盾的文案。用于其他产品时必须同步修改视觉母题。示例品牌与收益数据为概念演示。

详见 `skills/ad-creative-video/references/kinetic-report.md`。
