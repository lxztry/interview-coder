"""
AI时代研发招聘出题系统
帮面试官出题、管理题库、AI辅助评分
"""

import os
import json
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from pathlib import Path

app = Flask(__name__)
app.config['SECRET_KEY'] = 'interview-coder-2026'
BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / 'data' / 'interview.db'
QUESTION_DIR = BASE_DIR / 'questions'

# 确保目录存在
(BASE_DIR / 'data').mkdir(exist_ok=True)
QUESTION_DIR.mkdir(exist_ok=True)

# 初始化数据库
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 题库表
    c.execute('''CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dimension TEXT NOT NULL,      -- AI工具使用/代码理解/业务建模/调试排查
        level TEXT NOT NULL,          -- L1/L2/L3
        title TEXT NOT NULL,
        content TEXT NOT NULL,        -- Markdown格式任务描述
        hints TEXT,                   -- 面试官提示词
        grading TEXT NOT NULL,        -- JSON格式评分标准
        tags TEXT,                    -- 逗号分隔标签
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 试卷表
    c.execute('''CREATE TABLE IF NOT EXISTS papers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        question_ids TEXT NOT NULL,   -- JSON数组
        difficulty TEXT,              -- easy/medium/hard
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 候选人表
    c.execute('''CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        position TEXT NOT NULL,      -- 应聘职位
        paper_id INTEGER,
        status TEXT DEFAULT 'pending',  -- pending/doing/done
        answers TEXT,                 -- JSON格式答案
        scores TEXT,                 -- JSON格式评分结果
        feedback TEXT,               -- 面试官反馈
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (paper_id) REFERENCES papers(id)
    )''')
    
    # 评分记录表
    c.execute('''CREATE TABLE IF NOT EXISTS evaluations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id INTEGER,
        question_id INTEGER,
        score REAL,                  -- 0-100
        comment TEXT,
        evaluated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (candidate_id) REFERENCES candidates(id),
        FOREIGN KEY (question_id) REFERENCES questions(id)
    )''')
    
    conn.commit()
    conn.close()

init_db()

# ============ 路由 ============

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/questions')
def questions():
    """题库管理页"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    dimension = request.args.get('dimension', '')
    level = request.args.get('level', '')
    
    query = "SELECT * FROM questions WHERE 1=1"
    params = []
    if dimension:
        query += " AND dimension = ?"
        params.append(dimension)
    if level:
        query += " AND level = ?"
        params.append(level)
    
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    
    questions = [dict(row) for row in rows]
    return render_template('questions.html', 
                          questions=questions,
                          dimensions=['AI工具使用能力', '代码理解与改写', '业务建模能力', '调试与排查能力'],
                          levels=['L1', 'L2', 'L3'])

@app.route('/papers')
def papers():
    """试卷管理页"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM papers ORDER BY created_at DESC")
    papers = [dict(row) for row in c.fetchall()]
    conn.close()
    return render_template('papers.html', papers=papers)

@app.route('/candidates')
def candidates_page():
    """候选人管理页"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT c.*, p.name as paper_name FROM candidates c LEFT JOIN papers p ON c.paper_id = p.id ORDER BY c.created_at DESC")
    candidates = [dict(row) for row in c.fetchall()]
    conn.close()
    return render_template('candidates.html', candidates=candidates)

@app.route('/ai-assist')
def ai_assist():
    """AI辅助出题页"""
    return render_template('ai_assist.html')

@app.route('/evaluate/<int:candidate_id>')
def evaluate_page(candidate_id):
    """评分工作台"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM candidates WHERE id = ?", (candidate_id,))
    candidate = dict(c.fetchone())
    
    paper = None
    if candidate['paper_id']:
        c.execute("SELECT * FROM papers WHERE id = ?", (candidate['paper_id'],))
        paper = dict(c.fetchone())
    
    questions_list = []
    if paper:
        q_ids = json.loads(paper['question_ids'])
        placeholders = ','.join(['?'] * len(q_ids))
        c.execute(f"SELECT * FROM questions WHERE id IN ({placeholders})", q_ids)
        questions_list = [dict(row) for row in c.fetchall()]
    
    conn.close()
    return render_template('evaluate.html', 
                          candidate=candidate, 
                          paper=paper,
                          questions=questions_list)

# ============ API 接口 ============

@app.route('/api/questions', methods=['GET', 'POST'])
def api_questions():
    """题库API"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    if request.method == 'POST':
        data = request.json
        c.execute('''INSERT INTO questions (dimension, level, title, content, hints, grading, tags)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (data['dimension'], data['level'], data['title'], 
                   data['content'], data.get('hints', ''),
                   json.dumps(data['grading']), data.get('tags', '')))
        conn.commit()
        question_id = c.lastrowid
        conn.close()
        return jsonify({'id': question_id, 'success': True})
    
    # GET
    dimension = request.args.get('dimension')
    level = request.args.get('level')
    query = "SELECT * FROM questions WHERE 1=1"
    params = []
    if dimension:
        query += " AND dimension = ?"
        params.append(dimension)
    if level:
        query += " AND level = ?"
        params.append(level)
    
    c.execute(query, params)
    questions = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(questions)

@app.route('/api/questions/<int:qid>', methods=['GET', 'PUT', 'DELETE'])
def api_question(qid):
    """单题操作"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    if request.method == 'GET':
        c.execute("SELECT * FROM questions WHERE id = ?", (qid,))
        q = dict(c.fetchone())
        conn.close()
        return jsonify(q)
    
    if request.method == 'PUT':
        data = request.json
        c.execute('''UPDATE questions SET dimension=?, level=?, title=?, content=?, 
                     hints=?, grading=?, tags=?, updated_at=CURRENT_TIMESTAMP WHERE id=?''',
                  (data['dimension'], data['level'], data['title'], data['content'],
                   data.get('hints', ''), json.dumps(data['grading']), 
                   data.get('tags', ''), qid))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    if request.method == 'DELETE':
        c.execute("DELETE FROM questions WHERE id = ?", (qid,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})

@app.route('/api/papers', methods=['GET', 'POST'])
def api_papers():
    """试卷API"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    if request.method == 'POST':
        data = request.json
        c.execute('''INSERT INTO papers (name, description, question_ids, difficulty)
                     VALUES (?, ?, ?, ?)''',
                  (data['name'], data.get('description', ''),
                   json.dumps(data['question_ids']), data.get('difficulty', 'medium')))
        conn.commit()
        paper_id = c.lastrowid
        conn.close()
        return jsonify({'id': paper_id, 'success': True})
    
    c.execute("SELECT * FROM papers ORDER BY created_at DESC")
    papers = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(papers)

@app.route('/api/papers/<int:pid>', methods=['GET', 'DELETE'])
def api_paper(pid):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    if request.method == 'GET':
        c.execute("SELECT * FROM papers WHERE id = ?", (pid,))
        paper = dict(c.fetchone())
        # 加载关联题目
        q_ids = json.loads(paper['question_ids'])
        placeholders = ','.join(['?'] * len(q_ids))
        c.execute(f"SELECT * FROM questions WHERE id IN ({placeholders})", q_ids)
        paper['questions'] = [dict(row) for row in c.fetchall()]
        conn.close()
        return jsonify(paper)
    
    if request.method == 'DELETE':
        c.execute("DELETE FROM papers WHERE id = ?", (pid,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})

@app.route('/api/candidates', methods=['GET', 'POST'])
def api_candidates():
    """候选人API"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    if request.method == 'POST':
        data = request.json
        c.execute('''INSERT INTO candidates (name, position, paper_id, status)
                     VALUES (?, ?, ?, ?)''',
                  (data['name'], data['position'], data.get('paper_id'), 'pending'))
        conn.commit()
        cand_id = c.lastrowid
        conn.close()
        return jsonify({'id': cand_id, 'success': True})
    
    c.execute("SELECT c.*, p.name as paper_name FROM candidates c LEFT JOIN papers p ON c.paper_id = p.id ORDER BY c.created_at DESC")
    candidates = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(candidates)

@app.route('/api/candidates/<int:cid>', methods=['GET', 'PUT'])
def api_candidate(cid):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    if request.method == 'GET':
        c.execute("SELECT * FROM candidates WHERE id = ?", (cid,))
        cand = dict(c.fetchone())
        conn.close()
        return jsonify(cand)
    
    if request.method == 'PUT':
        data = request.json
        if 'status' in data:
            c.execute("UPDATE candidates SET status=? WHERE id=?", (data['status'], cid))
        if 'answers' in data:
            c.execute("UPDATE candidates SET answers=? WHERE id=?", (json.dumps(data['answers']), cid))
        if 'scores' in data:
            c.execute("UPDATE candidates SET scores=? WHERE id=?", (json.dumps(data['scores']), cid))
        if 'feedback' in data:
            c.execute("UPDATE candidates SET feedback=? WHERE id=?", (data['feedback'], cid))
        conn.commit()
        conn.close()
        return jsonify({'success': True})

@app.route('/api/ai/generate-question', methods=['POST'])
def api_ai_generate():
    """AI生成题目"""
    data = request.json
    dimension = data.get('dimension', '')
    level = data.get('level', 'L2')
    focus = data.get('focus', '')
    
    # 构建提示词
    dimension_cn = {
        'AI工具使用能力': 'AI工具使用能力（Copilot/Claude等AI辅助编程）',
        '代码理解与改写': '代码理解与改写（阅读遗留代码、重构优化）',
        '业务建模能力': '业务建模能力（从需求到技术方案）',
        '调试与排查能力': '调试与排查能力（定位问题、根因分析）'
    }.get(dimension, dimension)
    
    level_desc = {
        'L1': '入门级（30分钟内完成，考察基础概念）',
        'L2': '中级（1-2小时，考察系统设计思维）',
        'L3': '高级（2-4小时，考察综合架构能力）'
    }.get(level, '中级')
    
    prompt = f"""你是一个资深的面试官，请为AI时代的研发招聘生成一道面试题。

要求：
- 维度：{dimension_cn}
- 难度：{level_desc}
- 重点：{focus if focus else '考察候选人实际解决问题的能力'}
- 场景要贴近真实工作，避免纯粹的理论题

请生成以下格式的JSON（不要加markdown代码块）：
{{
  "title": "题目标题",
  "content": "## 任务背景\\n[描述一个真实的工作场景]\\n\\n## 具体要求\\n[清晰的验收标准]",
  "hints": "## 面试官提示词\\n[如果候选人卡住，可以给的提示]",
  "grading": {{
    "excellent": "优秀标准（80-100分）：",
    "good": "良好标准（60-79分）：",
    "pass": "及格标准（40-59分）：",
    "fail": "不及格标准（0-39分）："
  }},
  "estimated_time": "预计完成时间"
}}

请直接输出JSON，不要有其他文字。"""
    
    # 这里需要接入AI服务
    # 预留接口，可以通过环境变量或配置切换
    return jsonify({
        'prompt': prompt,
        'status': 'ready',
        'message': '提示词已生成，请调用AI服务获取结果'
    })

@app.route('/api/export/paper/<int:paper_id>')
def api_export_paper(paper_id):
    """导出试卷为Markdown"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute("SELECT * FROM papers WHERE id = ?", (paper_id,))
    paper = dict(c.fetchone())
    q_ids = json.loads(paper['question_ids'])
    placeholders = ','.join(['?'] * len(q_ids))
    c.execute(f"SELECT * FROM questions WHERE id IN ({placeholders})", q_ids)
    questions = [dict(row) for row in c.fetchall()]
    conn.close()
    
    # 生成Markdown
    md = f"# {paper['name']}\n\n"
    md += f"{paper.get('description', '')}\n\n"
    md += f"**难度：** {paper.get('difficulty', 'medium')}\n\n"
    md += "---\n\n"
    
    for i, q in enumerate(questions, 1):
        md += f"## 第{i}题：{q['title']}\n\n"
        md += f"**维度：** {q['dimension']} | **难度：** {q['level']}\n\n"
        md += f"{q['content']}\n\n"
        if q['hints']:
            md += f"### 面试官提示词\n{q['hints']}\n\n"
        
        grading = json.loads(q['grading'])
        md += "### 评分标准\n"
        for level, desc in grading.items():
            md += f"- **{level.upper()}**: {desc}\n"
        md += "\n---\n\n"
    
    return jsonify({
        'markdown': md,
        'filename': f"{paper['name']}.md"
    })

if __name__ == '__main__':
    print("=" * 50)
    print("AI时代研发招聘出题系统")
    print("=" * 50)
    print(f"数据库: {DB_PATH}")
    print(f"题库目录: {QUESTION_DIR}")
    print("启动中... http://127.0.0.1:5123")
    app.run(host='0.0.0.0', port=5123, debug=True)