# AI 面试出题系统

AI时代研发招聘出题系统 — 题库管理、AI助手提示词生成、试卷组装、候选人跟踪。

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 功能特性

- **题库管理**：按维度/难度筛选题目，CRUD操作，支持标签和评分标准
- **试卷管理**：从题库选题组装试卷，一键导出 Markdown
- **候选人跟踪**：记录面试进度，查看历史评估
- **AI助手**：5个预设提示词模板 + 自定义维度生成器
- **AI生成题目**：模拟 DeepSeek/Gemini/联网搜索 生成面试题

## 考察维度

- AI工具使用能力
- 代码理解与改写
- 业务建模能力
- 调试与排查能力
- 综合架构设计（可选）

## 快速启动

```bash
cd D:\code\aipkgame\interview-coder
pip install flask
python app.py
```

打开浏览器访问：http://127.0.0.1:5123

## 页面导航

- `/` — 首页
- `/questions` — 题库管理
- `/papers` — 试卷管理
- `/candidates` — 候选人
- `/ai-assist` — AI助手
- `/evaluate` — AI评估

## 技术栈

- **后端**：Python Flask + SQLite
- **前端**：HTML/CSS/JavaScript（原生，无框架）
- **数据库**：SQLite（数据文件 `data/interview.db`）

## 项目结构

```
interview-coder/
├── app.py                  # Flask 主应用
├── templates/              # HTML 模板
│   ├── index.html
│   ├── questions.html
│   ├── papers.html
│   ├── candidates.html
│   ├── ai_assist.html
│   └── evaluate.html
└── data/
    └── interview.db        # SQLite 数据库
```

## License

MIT