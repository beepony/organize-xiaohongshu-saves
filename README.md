# 小红书点赞与收藏整理 Skill

把用户本人有权访问的小红书点赞、收藏或指定专辑，整理成可追溯、可断点续做的结构化报告。

它不是一个绕过登录或批量爬取工具。它是一套给 AI Agent 使用的工作流：按用户指定范围逐条审阅正文、图片、视频画面和必要评论，筛选相关内容，提取自定义字段，并在每篇完成后立即保存。

> English summary: An evidence-grounded, resumable AI workflow for organizing a user's authorized Xiaohongshu/REDnote likes and favorites. It supports custom fields, media review, relevance filtering, per-post checkpoints, and Markdown/CSV-first delivery.

## 适合解决什么问题

- 旅行收藏：地址、交通、停车、门票、厕所、餐饮、路线、注意事项。
- 餐厅收藏：地址、人均、必点菜、预约、排队、营业时间。
- 装修收藏：品牌、型号、尺寸、价格、购买渠道、优缺点和避坑信息。
- 健身收藏：动作、目标肌群、器械、组数、错误示范和禁忌。
- 任何需要“筛选相关帖子 + 从图文中提取自定义字段”的个人收藏整理任务。

## 核心特点

- **证据优先**：每个字段同时保存值、证据位置和可信状态，不根据常识补齐地址、费用或设施。
- **图片与评论分层**：区分正文、图片、作者评论和普通评论，冲突信息单独标记。
- **逐篇落盘**：每完成一篇就原子更新 `items.json`，并重建 Markdown 与 CSV。
- **断点续做**：任务中断后从最小的缺失或待处理序号继续。
- **范围可验证**：以审阅的来源帖子数量作为完成目标，排除内容不会偷偷改变统计口径。
- **跨平台降级**：没有浏览器或脚本工具时，可切换到截图/导出文件的辅助模式。

## 工作模式

| 模式 | 条件 | 能做什么 |
|---|---|---|
| 完整浏览器模式 | AI 能操作用户已登录的浏览器并写本地文件 | 逐条打开收藏、检查媒体、自动断点保存 |
| 辅助模式 | AI 不能访问登录态，但用户能提供截图、复制内容或导出包 | 按相同证据规则分批提取并返回检查点 |
| 通用提示词模式 | 普通消费级 AI，仅支持对话或上传文件 | 使用便携提示词处理用户主动提供的内容 |

仅安装说明不会给 AI 新增浏览器权限。能否直接查看登录后的小红书，取决于宿主产品提供的浏览器、电脑操作、OCR、文件和文档能力。

## 仓库结构

```text
.
├── skill/organize-xiaohongshu-saves/  # 可安装 Skill
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── references/
│   └── scripts/xhs_project.py
├── portable/                           # ChatGPT、豆包等平台的提示词适配
├── examples/                           # 完全虚构的脱敏示例
├── docs/PORTABILITY.md                 # 跨平台设计与能力边界
└── tests/                              # 标准库测试
```

## 安装到 Codex

复制完整 Skill 文件夹：

```bash
mkdir -p ~/.codex/skills
cp -R skill/organize-xiaohongshu-saves ~/.codex/skills/
```

重新打开 Codex 或新建任务，然后显式调用：

```text
使用 $organize-xiaohongshu-saves。

来源：我的收藏 → 专辑 → 周末亲水活动
范围：按显示顺序审阅前 30 条
保留：玩水、溯溪、桨板等直接相关内容
排除：纯徒步、普通公园和其他无关内容
字段：导航地址、注意事项、停车及费用、是否有厕所、周围饮食
输出：Word；每处理一条立即保存，全部 30 条验证通过后结束。
```

## Claude、Gemini、ChatGPT 和豆包

- **Claude / 支持 Skill ZIP 的产品**：将 `skill/organize-xiaohongshu-saves` 目录单独压缩后上传。
- **Gemini Spark**：按当前产品要求上传以 `SKILL.md` 为根文件的 Skill 包；脚本和外部网站能力受宿主限制。
- **ChatGPT 自定义 GPT**：把 `portable/chatgpt-instructions.md` 放入 Instructions，并把 schema/reference 文件作为知识文件。
- **豆包或其他智能体产品**：复制 `portable/doubao-agent-instructions.md`；如果产品不能访问登录态页面，使用截图或导出文件模式。
- **任意聊天 AI**：使用 `portable/universal-prompt.md`。

平台能力会变化，请以宿主产品当时的官方说明和实际权限为准。详细兼容策略见 [docs/PORTABILITY.md](docs/PORTABILITY.md)。

## 检查点命令行工具

工具仅使用 Python 标准库。

初始化项目：

```bash
python skill/organize-xiaohongshu-saves/scripts/xhs_project.py init \
  --project ./workspace/demo \
  --source-type album \
  --source-name "示例专辑" \
  --limit 30 \
  --field "导航地址" \
  --field "注意事项" \
  --include "与目标主题直接相关" \
  --exclude "与目标主题无关" \
  --output-title "收藏整理报告"
```

生成一条空白检查点：

```bash
python skill/organize-xiaohongshu-saves/scripts/xhs_project.py template \
  --project ./workspace/demo \
  --order 1 \
  --output ./workspace/item-001.json
```

写入并立即重建报告：

```bash
python skill/organize-xiaohongshu-saves/scripts/xhs_project.py upsert \
  --project ./workspace/demo \
  --item-file ./workspace/item-001.json
```

查看状态并进行最终校验：

```bash
python skill/organize-xiaohongshu-saves/scripts/xhs_project.py status --project ./workspace/demo
python skill/organize-xiaohongshu-saves/scripts/xhs_project.py validate --project ./workspace/demo
```

项目会生成：

- `project.json`：来源、数量、字段和筛选规则。
- `items.json`：逐篇结构化检查点。
- `report.md`：持续重建的工作报告。
- `included.csv`：保留记录。
- `excluded.csv`：排除条目和原因。

## 可信状态

| 状态 | 含义 |
|---|---|
| `confirmed` | 作者正文或清晰媒体明确提供 |
| `author-comment` | 作者在评论中补充 |
| `comment-only` | 普通评论者提供，尚未验证 |
| `conflicting` | 正文、媒体或评论相互冲突 |
| `not-mentioned` | 已检查但没有可靠信息 |
| `image-unreadable` | 信息可能在图片中，但无法可靠读取 |

## 安全与隐私

- 只处理用户本人有权访问的内容。
- 不请求、导出或保存密码、Cookie、Token 或浏览器配置。
- 不绕过验证码、私密账号控制、速率限制或网站限制。
- 不自动点赞、取消收藏、评论、关注、发布或私信。
- 以结构化摘要为主，不复制或重新发布完整帖子。
- 不要把个人项目目录、截图或浏览记录提交到本仓库。

发现安全或隐私问题时，请不要在公开 Issue 中附上账号、收藏截图或原始数据；参见 [SECURITY.md](SECURITY.md)。

## 测试

```bash
python -m unittest discover -s tests -v
python -m py_compile skill/organize-xiaohongshu-saves/scripts/xhs_project.py
```

## 许可证

[MIT](LICENSE)
