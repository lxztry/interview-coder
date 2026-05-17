# Generate a clean, simple test page to verify the approach works
# Then generate the real page properly

test_html = '''<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>Test</title></head>
<body>
<h1>AI智能出题助手</h1>
<div id="output"></div>
<script>
var selectedPreset = "ai_tools";
var presetTemplates = {
    ai_tools: {name: "[AI]AI工具使用能力", desc: "适合校招/初级社招", prompt: "第一行\\n第二行\\n第三行"},
    code_rewrite: {name: "[CODE]代码理解与改写", desc: "适合中级社招", prompt: "测试prompt"}
};

function render() {
    var tmpl = presetTemplates[selectedPreset];
    document.getElementById("output").innerHTML = "<div>" + tmpl.name + "</div><div>" + tmpl.prompt + "</div>";
}

function switchTemplate(id) {
    selectedPreset = id;
    render();
}

document.write("<button onclick='switchTemplate(\"code_rewrite\")'>切换</button>");
render();
</script>
</body>
</html>'''

with open(r'D:\code\aipkgame\interview-coder\templates\test.html', 'w', encoding='utf-8') as f:
    f.write(test_html)
print("done")