"""
Cupid Agent Web Dashboard Server
Runs an interactive HTTP web app allowing users to submit queries and see live ReAct Agent traces.
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os
import sys
from urllib.parse import parse_qs, urlparse

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import CupidReActEngine

PORT = 8080

HTML_PAGE = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💘 Cupid Agent - Trợ lý Hẹn hò ReAct AI</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0f172a;
            --card-bg: rgba(30, 41, 59, 0.8);
            --accent-pink: #ec4899;
            --accent-purple: #8b5cf6;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --border-color: rgba(255, 255, 255, 0.1);
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Outfit', sans-serif; }
        body {
            background-color: var(--bg-color);
            background-image: radial-gradient(at 0% 0%, rgba(236, 72, 153, 0.15) 0, transparent 50%),
                              radial-gradient(at 100% 100%, rgba(139, 92, 246, 0.15) 0, transparent 50%);
            color: var(--text-main);
            min-height: 100vh;
            padding: 2rem;
        }
        .container { max-width: 1100px; margin: 0 auto; }
        header { text-align: center; margin-bottom: 2.5rem; }
        h1 {
            font-size: 2.5rem;
            background: linear-gradient(135deg, #f472b6, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        p.subtitle { color: var(--text-muted); font-size: 1.1rem; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
        .card {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 1.5rem;
            backdrop-filter: blur(12px);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }
        h2 { font-size: 1.3rem; margin-bottom: 1rem; color: #f472b6; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem; }
        label { display: block; margin-top: 0.8rem; font-size: 0.9rem; color: var(--text-muted); }
        input, select, textarea {
            width: 100%;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 0.75rem;
            color: white;
            margin-top: 0.3rem;
            font-size: 0.95rem;
        }
        textarea { height: 90px; resize: vertical; }
        button {
            width: 100%;
            margin-top: 1.2rem;
            background: linear-gradient(135deg, var(--accent-pink), var(--accent-purple));
            color: white;
            border: none;
            padding: 0.9rem;
            border-radius: 8px;
            font-weight: 600;
            font-size: 1rem;
            cursor: pointer;
            transition: transform 0.2s, opacity 0.2s;
        }
        button:hover { opacity: 0.9; transform: translateY(-2px); }
        .trace-step {
            background: rgba(15, 23, 42, 0.8);
            border-left: 4px solid var(--accent-purple);
            padding: 0.8rem;
            border-radius: 6px;
            margin-bottom: 0.8rem;
            font-size: 0.9rem;
        }
        .trace-thought { color: #f472b6; font-weight: 600; }
        .trace-action { color: #38bdf8; font-family: monospace; }
        .trace-obs { color: #a7f3d0; margin-top: 0.3rem; font-size: 0.85rem; }
        .final-result {
            background: rgba(236, 72, 153, 0.1);
            border: 1px solid var(--accent-pink);
            border-radius: 12px;
            padding: 1.2rem;
            white-space: pre-wrap;
            line-height: 1.6;
            margin-top: 1rem;
        }
        .full-width { grid-column: span 2; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>💘 Cupid Agent System</h1>
            <p class="subtitle">Trợ lý AI phân tích tương thích, lọc deal-breaker & gợi ý hẹn hò (ReAct Architecture)</p>
        </header>

        <div class="grid">
            <div class="card">
                <h2>1. Hồ sơ cá nhân của bạn</h2>
                <label>Họ tên / Giới tính / Độ tuổi:</label>
                <input type="text" id="userInfo" value="Nữ, 22 tuổi, ở Hà Nội">
                <label>Tính cách & Sở thích:</label>
                <input type="text" id="interests" value="Hướng nội, đọc sách, cà phê yên tĩnh, nói chuyện sâu">
                <label>Mục tiêu quan hệ:</label>
                <select id="goal">
                    <option value="nghiêm túc">Nghiêm túc lâu dài</option>
                    <option value="tìm hiểu tự nhiên">Tìm hiểu tự nhiên</option>
                </select>
                <label>Tiêu chuẩn bắt buộc (Deal-breakers):</label>
                <input type="text" id="dealBreakers" value="không hút thuốc, không muốn yêu xa">
            </div>

            <div class="card">
                <h2>2. Yêu cầu dành cho Cupid Agent</h2>
                <label>Nhập câu hỏi hoặc yêu cầu ghép đôi:</label>
                <textarea id="query">Tìm Top 3 match phù hợp nhất với mình kèm gợi ý tin nhắn mở lời và ý tưởng đi date cho từng người.</textarea>
                <button onclick="runCupid()">🚀 Phân tích & Tìm kiếm Match</button>
            </div>

            <div class="card full-width">
                <h2>3. Luồng suy luận ReAct Trace (Thought -> Action -> Observation)</h2>
                <div id="traceContainer"><p style="color: var(--text-muted);">Bấm "Phân tích & Tìm kiếm Match" để xem các bước ReAct loop...</p></div>
            </div>

            <div class="card full-width">
                <h2>4. Kết quả Đề xuất từ Cupid Agent (Final Answer)</h2>
                <div id="resultContainer" class="final-result">Chưa có kết quả.</div>
            </div>
        </div>
    </div>

    <script>
        async function runCupid() {
            const traceBox = document.getElementById('traceContainer');
            const resultBox = document.getElementById('resultContainer');
            traceBox.innerHTML = '<p style="color: #f472b6;">⏳ Cupid Agent đang suy luận và chạy ReAct tools...</p>';
            resultBox.innerHTML = 'Đang phân tích...';

            const userProfile = {
                age: 22,
                gender: "Nữ",
                location: "Hà Nội",
                personality: "Hướng nội",
                interests: ["đọc sách", "cà phê yên tĩnh", "nói chuyện sâu"],
                relationship_goal: document.getElementById('goal').value,
                deal_breakers: document.getElementById('dealBreakers').value.split(',').map(s => s.trim())
            };

            const query = document.getElementById('query').value;

            try {
                const res = await fetch('/api/query', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_profile: userProfile, question: query })
                });
                const data = await res.json();

                traceBox.innerHTML = '';
                if (data.trace && data.trace.length > 0) {
                    data.trace.forEach((step, idx) => {
                        const div = document.createElement('div');
                        div.className = 'trace-step';
                        div.innerHTML = `
                            <div class="trace-thought">Step ${step.iteration || idx + 1} Thought: ${step.thought}</div>
                            <div class="trace-action">Action: ${step.action}</div>
                            <div class="trace-obs">Observation: ${step.observation}</div>
                        `;
                        traceBox.appendChild(div);
                    });
                } else {
                    traceBox.innerHTML = '<p style="color: var(--text-muted);">ReAct Direct Path executed.</p>';
                }

                resultBox.innerText = data.final_answer;
            } catch (err) {
                traceBox.innerHTML = '<p style="color: #ef4444;">Lỗi kết nối máy chủ.</p>';
                resultBox.innerText = err.toString();
            }
        }
    </script>
</body>
</html>
"""

class CupidRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode('utf-8'))
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/api/query":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            req_json = json.loads(post_data.decode('utf-8'))

            user_profile = req_json.get("user_profile", {})
            question = req_json.get("question", "")

            engine = CupidReActEngine(user_profile)
            res = engine.run(question)

            self.send_response(200)
            self.send_header("Content-Type", "json/application; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(res, ensure_ascii=False).encode('utf-8'))

def run_web_server():
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, CupidRequestHandler)
    print(f"Cupid Agent Dashboard running at http://localhost:{PORT}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_web_server()
