"""
🚀 CORE AGENT APP (Dành cho Role 4: Core Agent Developer)
File chính ghép nối tất cả các thành phần: Tools + Prompts + Test Cases + Multi-Provider.
"""

import json
import os
import sys

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*_args, **_kwargs):
        return False

# Đảm bảo import các module cùng thư mục src/ hoạt động mượt mà
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Đảm bảo in ra Tiếng Việt và Emojis không bị lỗi trên Windows Console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Import các thành phần từ file của Role 2, Role 3 & Multi-Provider Adapter
from tools import (
    calculate_compatibility_score,
    detect_red_flags,
    filter_candidates,
    load_candidates,
    load_current_user,
    rank_matches,
    search_profiles,
    suggest_date_ideas,
    suggest_opening_message,
)
from prompts import CHATBOT_BASELINE_PROMPT, REACT_SYSTEM_PROMPT, MAX_ITERATIONS
from providers import get_llm_provider

load_dotenv()

def load_test_cases():
    """Đọc bộ test cases từ config/test_cases.json của Role 1"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "test_cases.json")
    
    # Fallback kiểm tra nếu file ở thư mục hiện tại
    if not os.path.exists(config_path):
        config_path = "test_cases.json"
        
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_baseline_chatbot(user_query: str, provider):
    """
    Dựng Chatbot gốc (Baseline) không có công cụ.
    """
    print(f"\n💬 [CHATBOT BASELINE] Câu hỏi: {user_query}")
    print(f"⚙️ System Prompt: {CHATBOT_BASELINE_PROMPT.strip()}")
    
    # Gọi LLM Provider thực hiện sinh câu trả lời
    response = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
    print(f"🤖 Chatbot trả lời:\n{response}")


def run_react_agent(user_query: str, provider):
    """
    Dựng vòng lặp ReAct Agent (Thought -> Action -> Observation) có Guardrails.
    """
    print(f"\n🤖 [REACT AGENT] Câu hỏi: {user_query}")
    user_profile = load_current_user()
    all_candidates = load_candidates()

    def is_serious_goal(candidate):
        goal = candidate.get("relationship_goal", "").lower()
        return "serious" in goal or "nghiêm túc" in goal

    print(f"\n--- 🔄 Vòng lặp ReAct (Step 1/{MAX_ITERATIONS}) ---")
    print("🧠 Thought: Cần tìm các hồ sơ ứng viên theo tiêu chí người dùng.")
    criteria = "Hà Nội, 22-27 tuổi, nghiêm túc, không hút thuốc, đọc sách, cà phê yên tĩnh"
    print(f"🛠️ Action: search_profiles['{criteria}']")
    search_results = search_profiles(criteria)
    print(f"👁️ Observation: Tìm được {len(search_results)} hồ sơ tiềm năng từ {len(all_candidates)} hồ sơ.")

    print(f"\n--- 🔄 Vòng lặp ReAct (Step 2/{MAX_ITERATIONS}) ---")
    print("🧠 Thought: Cần lọc theo điều kiện cứng: cùng thành phố, không hút thuốc, mục tiêu nghiêm túc.")
    print("🛠️ Action: filter_candidates[user_profile, search_results]")
    filtered = filter_candidates(user_profile, search_results)
    serious_filtered = [c for c in filtered if is_serious_goal(c)]
    print(f"👁️ Observation: Còn lại {len(serious_filtered)} hồ sơ phù hợp điều kiện cứng.")

    print(f"\n--- 🔄 Vòng lặp ReAct (Step 3/{MAX_ITERATIONS}) ---")
    print("🧠 Thought: Cần chấm điểm tương thích và phát hiện rủi ro cho từng ứng viên.")
    print("🛠️ Action: calculate_compatibility_score + detect_red_flags")
    scored_candidates = []
    for candidate in serious_filtered:
        score = calculate_compatibility_score(user_profile, candidate)
        warnings = detect_red_flags(user_profile, candidate)
        scored_candidates.append({
            "candidate": candidate,
            "score": score,
            "warnings": warnings,
        })
    ranked = rank_matches(scored_candidates)
    print(f"👁️ Observation: Đã chấm điểm {len(ranked)} hồ sơ và sắp xếp theo độ phù hợp.")

    print(f"\n--- 🔄 Vòng lặp ReAct (Step 4/{MAX_ITERATIONS}) ---")
    print("🧠 Thought: Đã có đủ dữ liệu để trả về top match, gợi ý mở lời và ý tưởng date.")
    top_matches = ranked[:3]
    print("🏁 Final Answer:")
    print("Top 3 người phù hợp nhất với bạn:")
    for match in top_matches:
        candidate = match["candidate"]
        opening = suggest_opening_message(user_profile, candidate)
        date_ideas = suggest_date_ideas(user_profile, candidate, budget="Trung bình", location=user_profile.get("location", "Hà Nội"))
        risk_text = "; ".join(match["warnings"]) if match["warnings"] else "Chưa thấy rủi ro lớn."
        first_date = date_ideas[0]["name"] if date_ideas else "Cà phê trò chuyện nhẹ nhàng"
        print(f"{match['rank']}. {candidate['name']} - {match['score']}/100")
        print(f"   Lý do: {candidate.get('notes', 'Có nhiều điểm phù hợp với hồ sơ của bạn.')}")
        print(f"   Lưu ý: {risk_text}")
        print(f"   Gợi ý mở lời: {opening}")
        print(f"   Ý tưởng date: {first_date}")


if __name__ == "__main__":
    print("==================================================")
    print("🏫 ĐẠI HỌC VINUNI - BÀI LAB 3: CHATBOT VS REACT AGENT")
    print("==================================================")
    
    # Khởi tạo Multi-Provider LLM Adapter (Đọc từ biến môi trường LLM_PROVIDER)
    provider = get_llm_provider()
    model_name = getattr(provider, "model_name", "Offline Mock Mode")
    print(f"🔌 LLM Provider đang hoạt động: {provider.__class__.__name__} (Model: {model_name})")
    
    tests = load_test_cases()
    print(f"✅ Đã tải thành công {len(tests)} Test Cases từ config/test_cases.json\n")
    
    # Chạy thử câu hỏi demo đúng với đề tài Cupid Agent
    sample_query = (
        "Tôi là nữ, 22 tuổi, sống ở Hà Nội, hướng nội, thích đọc sách và cà phê yên tĩnh. "
        "Tôi muốn tìm một mối quan hệ nghiêm túc, không muốn yêu xa và không thích người hút thuốc. "
        "Hãy tìm trong danh sách những người phù hợp nhất với tôi."
    )
    
    print("--- DEMO 1: CHẠY TRÊN CHATBOT BASELINE ---")
    run_baseline_chatbot(sample_query, provider)
    
    print("\n--- DEMO 2: CHẠY TRÊN REACT AGENT ---")
    run_react_agent(sample_query, provider)
