---
name: pptx
description: 文字转PPT，创建、读取、编辑 .pptx 演示文稿。触发词：PPT、演示文稿、slides、deck、幻灯片
tags: ppt,pptx,presentation,slides
---

# PPTX 技能

## 快速参考

| 任务 | 方式 |
|------|------|
| 读取/解析内容 | `python -m markitdown presentation.pptx` |
| 从模板编辑 | python-pptx |
| 从零创建 | python-pptx 或 pptxgenjs |

## 工作流程

### 1. 内容规划

收到用户请求后，先规划大纲：
- 确定主题和目标受众
- 列出每页标题和要点（5-10 页为宜）
- 确认配色方案和风格

### 2. 创建 PPTX

使用 python-pptx 库生成：

```python
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

prs = Presentation()
prs.slide_width = Inches(13.333)  # 16:9
prs.slide_height = Inches(7.5)

# 添加标题页
slide = prs.slides.add_slide(prs.slide_layouts[6])  # 空白布局
# ... 添加文本框、图形等
prs.save("output.pptx")
```

### 3. 设计原则

- **60/40 法则**：60% 视觉 + 40% 文字
- **行动式标题**：用"市场规模三年翻倍"代替"市场分析"
- 每页不超过 6 个要点
- 选择与主题匹配的配色，不要默认蓝色
- 使用大字体：标题 36pt+，正文 24pt+

### 4. 配色参考

| 主题 | 主色 | 辅色 | 背景 |
|------|------|------|------|
| 科技 | #2D3436 | #0984E3 | #DFE6E9 |
| 商务 | #2C3E50 | #E74C3C | #ECF0F1 |
| 学术 | #1B4332 | #40916C | #F0FFF0 |
| 创意 | #6C5CE7 | #FD79A8 | #F8F9FA |

## 依赖

```bash
pip install python-pptx markitdown
```

## 注意事项

- 优先使用空白布局（layout 6），手动控制位置
- 文本框需设置 word_wrap=True 避免溢出
- 中文字体用"微软雅黑"或"思源黑体"
- 生成后用 markitdown 反向验证内容完整性
