# LatexToReadMe

LaTeX 论文 + 代码仓库 → 专业 GitHub README，一个 Claude Code Skill。

## 这是什么

写论文的人经常要把代码开源到 GitHub，但从 LaTeX 论文里手动整理 README
很费劲——标题、摘要、方法、结果、引用散落在 `.tex` 和 `.bib` 里，还得
单独写安装步骤和用法。

这个 Skill 自动完成这件事：

1. 解析 `.tex` 文件，提取标题 / 作者 / 摘要 / 方法论 / 实验结果 / 引用
2. 扫描代码仓库，找到依赖文件、入口脚本、项目结构
3. 合成为一个开发者友好的 README.md

## 效果对比

用一份模拟的 "HierGAT 分子性质预测" 论文 + Python 代码库测试：

| 指标 | 用 Skill | 不用 Skill |
|------|:--------:|:----------:|
| 标准 README 通过率 | **100%** | 63.6% |
| 行数 | 120 行 | 365 行 |
| HTML 包装 | 无 | `<p align="center">` |
| 编造内容 (venv) | 无 | 有 |
| 重复章节 | 无 | 依赖表 + 可复现章节 |
| Badge 全验证 | ✓ | ✓ |

核心区别：Skill 生成的 README 更短、更干净、没有编造内容，且 Install
排在 Methodology 前面（面向开发者，而非审稿人）。

## 安装

```bash
cp -r readme-generator ~/.claude/skills/
```

## 使用

在 Claude Code 中直接说：

```
帮我把这个项目生成 README，论文在 paper.tex，代码在 src/ 里
```

支持的定制：

| 提示词 | 效果 |
|--------|------|
| `中文` / `in Chinese` | 中文 README |
| `short` / `minimal` | 精简版（标题 + 摘要 + 安装 + 快速开始 + 引用） |
| `focus on <dir>` | 只看指定代码目录 |
| `skip <section>` | 跳过某个章节 |

## 项目结构

```
readme-generator/
├── SKILL.md                 # Skill 定义
├── evals/
│   ├── evals.json           # 测试用例 + 质量断言
│   └── files/paper-repo/    # 测试用模拟项目
│       ├── paper.tex        #   示例 LaTeX 论文
│       ├── references.bib   #   示例引用
│       └── src/, scripts/   #   示例 Python 代码
└── readme-generator-workspace/
    └── iteration-2/
        ├── benchmark.json   # 量化对比数据
        └── review.html      # 可视化对比页面
```
