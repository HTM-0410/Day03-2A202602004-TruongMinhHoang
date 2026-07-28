"""
🚀 CUPRESS AGENT - Core App với đầy đủ Guardrails & Fix Test Cases
Fixed: Input binding, Routing, Safety, Validation, Empty results, Clarification
"""

import json
import os
import sys
import re
import time
from datetime import datetime

# UTF-8 support
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from tools import (
    MOCK_CANDIDATES,
    AVAILABLE_TOOLS,
    parse_user_profile,
    search_profiles,
    filter_candidates,
    calculate_compatibility_score,
    rank_matches,
    detect_red_flags,
    suggest_opening_message,
    suggest_date_ideas,
)
from providers import get_llm_provider
from prompts import CHATBOT_BASELINE_PROMPT, REACT_SYSTEM_PROMPT, MAX_ITERATIONS

# ============================================================================
# 🔧 CONSTANTS & CONFIG
# ============================================================================

FORBIDDEN_KEYWORDS = [
    "ép buộc", "bắt buộc", "theo dõi", "hack", "xâm nhập",
    "thao túng", "bẫy", "lừa", "chiếm đoạt", "làm hại", "cưỡng bức",
    "stalk", "force", "manipulate", "spy", "kidnap", "ép yêu", "đe dọa"
]

SIMPLE_QUERY_KEYWORDS = [
    "là gì", "thế nào", "tư vấn", "cho hỏi", "giải thích",
    "khái niệm", "lời khuyên", "khác gì", "concept", "explain", "advice", "tip", "mẹo"
]

# ============================================================================
# 🔧 HELPER FUNCTIONS
# ============================================================================

def parse_json_safe(json_str, fallback=None):
    """Parse JSON safely, return fallback on error"""
    if isinstance(json_str, (dict, list)):
        return json_str
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return fallback if fallback is not None else {}


def is_safety_violation(text: str) -> bool:
    """Kiểm tra vi phạm an toàn (Guardrail G4)"""
    text_lower = text.lower()
    return any(kw in text_lower for kw in FORBIDDEN_KEYWORDS)


def is_simple_query(text: str) -> bool:
    """Kiểm tra câu hỏi đơn giản không cần tools (Test 1, 2)"""
    text_lower = text.lower()
    # Không chứa từ khóa tìm kiếm cụ thể
    search_keywords = ["tìm", "match", "phù hợp", "ghép", "ứng viên", "người"]
    needs_search = any(kw in text_lower for kw in search_keywords)
    if needs_search:
        return False
    # Có từ khóa câu hỏi chung
    return any(kw in text_lower for kw in SIMPLE_QUERY_KEYWORDS)


def validate_input(user_input: str) -> tuple:
    """
    Validate input đầu vào (Guardrail G7 - Test 7)
    Returns: (is_valid, error_message)
    """
    # Kiểm tra tuổi không hợp lệ
    age_mentions = re.findall(r'(\d+)\s*tuổi', user_input.lower())
    for age_str in age_mentions:
        try:
            age = int(age_str)
            if age > 100 or age < 10:
                return False, f"Tuổi {age} không hợp lệ. Hệ thống chỉ hỗ trợ tìm kiếm trong khoảng 18–100 tuổi."
        except ValueError:
            pass
    
    # Kiểm tra ngày tháng không hợp lệ
    date_patterns = [
        r'(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})',
        r'(\d{4})[/\-.](\d{1,2})[/\-.](\d{1,2})'
    ]
    for pattern in date_patterns:
        matches = re.findall(pattern, user_input)
        for match in matches:
            try:
                if len(match[2]) == 4:  # DD/MM/YYYY or YYYY/MM/DD
                    day, month, year = int(match[0]), int(match[1]), int(match[2])
                else:  # MM/DD/YYYY
                    month, day, year = int(match[0]), int(match[1]), int(match[2])
                
                if month > 12 or month < 1 or day > 31 or day < 1:
                    return False, f"Ngày {day}/{month}/{year} không hợp lệ."
                if month == 2 and day > 29:
                    return False, f"Tháng 2 không có ngày {day}."
            except ValueError:
                pass
    
    return True, ""


def check_insufficient_info(profile: dict) -> bool:
    """
    Kiểm tra thông tin có đủ để tìm kiếm không (Guardrail G1 - Test 9)
    Cần ít nhất 2 trong 3: location, relationship_goal, hobbies
    """
    has_location = bool(profile.get("location", "").strip())
    has_goal = bool(profile.get("relationship_goal", "").strip())
    has_hobbies = len(profile.get("hobbies", [])) > 0
    has_personality = bool(profile.get("personality", "").strip())
    
    filled_count = sum([has_location, has_goal, has_hobbies or has_personality])
    return filled_count < 2


# ============================================================================
# 🚀 ROUTER: Simple vs Multi-step Query
# ============================================================================

def route_query(user_input: str, provider) -> str:
    """
    Routing: Phân biệt câu hỏi simple vs multi-step (Test 1, 2)
    - Simple: Trả lời trực tiếp bằng baseline chatbot
    - Multi-step: Sử dụng ReAct agent với tools
    """
    # Guardrail: Safety check TRƯỚC TIÊN
    if is_safety_violation(user_input):
        return """🚫 **Cupid không hỗ trợ yêu cầu này.**

Tôi không thể giúp với các yêu cầu liên quan đến:
- Ép buộc, đe dọa người khác
- Theo dõi, xâm phạm quyền riêng tư
- Thao túng, lừa đảo

Mỗi người đều có quyền tự do lựa chọn. Hãy để kết nối diễn ra tự nhiên và tôn trọng! 🌸

*Nếu bạn đang gặp vấn đề về mối quan hệ, hãy thử hỏi tôi về cách giao tiếp hiệu quả hoặc tư vấn hẹn hò nhé!* 💕"""

    # Validate input (Test 7)
    is_valid, error_msg = validate_input(user_input)
    if not is_valid:
        return f"⚠️ **Thông tin không hợp lệ:**\n\n{error_msg}\n\nVui lòng kiểm tra lại và nhập thông tin chính xác nhé!"

    # Simple query routing (Test 1, 2)
    if is_simple_query(user_input):
        print(f"\n💬 [ROUTING] Simple query → Baseline Chatbot")
        return provider.generate(user_input, system_prompt=CHATBOT_BASELINE_PROMPT)
    
    # Multi-step query → ReAct Agent
    print(f"\n🤖 [ROUTING] Multi-step query → ReAct Agent")
    return run_react_agent(user_input, provider)


# ============================================================================
# 🤖 REACT AGENT IMPLEMENTATION
# ============================================================================

def run_react_agent(user_query: str, provider=None) -> str:
    """
    ReAct Agent với đầy đủ Guardrails đã fix
    Fix: Parse user_query thực, không hard-code
    """
    if provider is None:
        provider = get_llm_provider()
    
    print(f"\n🤖 [REACT AGENT] Câu hỏi: {user_query}")
    
    # Bước 0: Parse user profile từ câu hỏi THỰC (FIX ROOT CAUSE)
    parsed_result = parse_user_profile(user_query)
    user_profile = parse_json_safe(parsed_result, {})
    
    # Guardrail G1: Thiếu thông tin → hỏi lại (Test 9)
    if not user_profile or user_profile.get("error") or check_insufficient_info(user_profile):
        return """💡 **Cupid cần thêm thông tin để tìm người phù hợp cho bạn!**

Bạn có thể cho mình biết thêm không? Ví dụ:
- 🔢 **Tuổi** của bạn?
- 📍 **Địa điểm** bạn đang sống?
- ❤️ **Sở thích** của bạn là gì?
- 🎯 **Mục tiêu** của bạn là gì (nghiêm túc, tìm hiểu, kết hôn)?

Càng nhiều thông tin, tôi càng tìm được người phù hợp với bạn! 😊"""

    user_profile_json = json.dumps(user_profile, ensure_ascii=False)
    
    # Trích xuất criteria TỪ user_profile thực (FIX)
    location = user_profile.get("location", "")
    goal = user_profile.get("relationship_goal", "")
    hobbies = user_profile.get("hobbies", [])
    personality = user_profile.get("personality", "")
    
    criteria_parts = [p for p in [location, goal, personality] if p]
    if hobbies and isinstance(hobbies, list):
        criteria_parts.extend(hobbies[:3])
    criteria = ", ".join(criteria_parts)
    
    print(f"🧠 [REACT] Parse profile thành công: {user_profile.get('name', 'N/A')}")
    print(f"🔍 [REACT] Criteria tìm kiếm: {criteria}")
    
    # Bước 1: Search profiles
    print(f"\n--- 🔄 Step 1/MAX_ITERATIONS ---")
    print(f"🛠️ Action: search_profiles['{criteria}']")
    search_results_json = search_profiles(criteria)
    search_results = parse_json_safe(search_results_json, [])
    
    # FIX: Nếu search trả về error
    if isinstance(search_results, dict) and search_results.get("error"):
        print(f"👁️ Observation: {search_results.get('message')}")
        search_results = MOCK_CANDIDATES
    
    print(f"👁️ Observation: Tìm được {len(search_results)} hồ sơ tiềm năng")
    
    # Bước 2: Filter candidates
    print(f"\n--- 🔄 Step 2/MAX_ITERATIONS ---")
    print(f"🛠️ Action: filter_candidates")
    filtered_json = filter_candidates(user_profile_json, json.dumps(search_results, ensure_ascii=False))
    filtered = parse_json_safe(filtered_json, [])
    
    # Guardrail G2: Không tìm thấy kết quả (Test 6)
    if isinstance(filtered, dict) and filtered.get("error"):
        return f"""😔 **Cupid chưa tìm thấy ai phù hợp với tiêu chí hiện tại của bạn.**

{filtered.get('message', '')}

Bạn có muốn thử:
- 🔄 Mở rộng khoảng cách địa lý (chấp nhận yêu xa)?
- 🎯 Bớt một số điều kiện deal-breaker?
- 📍 Tìm ở thành phố khác?

Hãy cho tôi biết để điều chỉnh nhé! 😊"""
    
    if not filtered or (isinstance(filtered, list) and len(filtered) == 0):
        return """😔 **Cupid chưa tìm thấy ai phù hợp với tiêu chí hiện tại của bạn.**

Có thể do:
- Không có ứng viên cùng thành phố
- Deal-breaker quá nghiêm ngặt
- Mục tiêu quan hệ chưa có trong danh sách

Bạn có muốn thử điều chỉnh một số tiêu chí không? 😊"""
    
    print(f"👁️ Observation: Còn lại {len(filtered)} hồ sơ sau khi lọc")
    
    # Bước 3: Calculate compatibility scores
    print(f"\n--- 🔄 Step 3/MAX_ITERATIONS ---")
    print(f"🛠️ Action: calculate_compatibility_score cho {len(filtered)} ứng viên")
    
    scored_candidates = []
    for candidate in filtered[:10]:  # Giới hạn 10 ứng viên
        cand_json = json.dumps(candidate, ensure_ascii=False)
        scored_json = calculate_compatibility_score(user_profile_json, cand_json)
        scored = parse_json_safe(scored_json, None)
        
        if scored and isinstance(scored, dict) and "error" not in scored:
            # Thêm red flags
            warnings = detect_red_flags(user_profile_json, cand_json)
            scored["red_flags"] = warnings
            scored_candidates.append(scored)
    
    if not scored_candidates:
        return """😔 **Có lỗi khi đánh giá độ tương thích.**

Vui lòng thử lại với thông tin khác hoặc liên hệ hỗ trợ."""
    
    print(f"👁️ Observation: Đã chấm điểm {len(scored_candidates)} hồ sơ")
    
    # Bước 4: Rank matches
    print(f"\n--- 🔄 Step 4/MAX_ITERATIONS ---")
    print(f"🛠️ Action: rank_matches")
    ranked_json = rank_matches(json.dumps(scored_candidates, ensure_ascii=False))
    ranked = parse_json_safe(ranked_json, scored_candidates)
    
    if not ranked or (isinstance(ranked, dict) and ranked.get("error")):
        # Fallback: sắp xếp thủ công
        ranked = sorted(scored_candidates, key=lambda x: x.get("compatibility_score", 0), reverse=True)
    
    print(f"👁️ Observation: Đã xếp hạng {len(ranked)} hồ sơ")
    
    # Bước 5: Build Final Answer
    print(f"\n--- 🏁 Final Answer ---")
    
    # Lấy top matches (tối đa 5)
    top_matches = ranked[:5] if len(ranked) >= 5 else ranked
    
    # Xây dựng response
    response = f"🎉 **Kết quả tìm kiếm cho bạn!**\n\n"
    response += f"Tôi đã phân tích {len(scored_candidates)} hồ sơ phù hợp với tiêu chí của bạn.\n\n"
    response += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for i, match in enumerate(top_matches, 1):
        name = match.get("name", "N/A")
        score = match.get("compatibility_score", 0)
        reason = match.get("compatibility_reason", match.get("notes", "Phù hợp"))
        age = match.get("age", "N/A")
        location = match.get("location", "N/A")
        hobbies = match.get("hobbies", [])
        if isinstance(hobbies, list):
            hobbies_str = ", ".join(hobbies[:3])
        else:
            hobbies_str = str(hobbies)
        
        response += f"**🏆 TOP {i}: {name}**, {age} tuổi\n"
        response += f"📍 Địa điểm: {location}\n"
        response += f"⭐ Điểm tương thích: **{score}/100**\n"
        response += f"💡 {reason}\n"
        response += f"❤️ Sở thích: {hobbies_str}\n"
        
        # Thêm red flags nếu có
        red_flags = match.get("red_flags", "")
        if red_flags and "Không phát hiện" not in red_flags:
            response += f"\n⚠️ **{red_flags}**\n"
        
        response += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # Gợi ý mở lời cho TOP 1
    if top_matches:
        top = top_matches[0]
        opening = suggest_opening_message(user_profile_json, json.dumps(top, ensure_ascii=False))
        response += f"💬 **Gợi ý mở lời với {top.get('name', 'người này')}:**\n{opening}\n\n"
    
    response += "*Lưu ý: Đây chỉ là gợi ý dựa trên thông tin có sẵn. Hãy trò chuyện để hiểu nhau hơn nhé! 💕*"
    
    return response


# ============================================================================
# 🧪 TEST RUNNER
# ============================================================================

def load_test_cases():
    """Load test cases from config"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "test_cases.json")
    
    if not os.path.exists(config_path):
        config_path = "test_cases.json"
    
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def run_test_cases():
    """Chạy tất cả test cases"""
    print("=" * 60)
    print("🧪 CUPRESS AGENT - TEST CASES RUNNER")
    print("=" * 60)
    
    provider = get_llm_provider()
    print(f"🔌 Provider: {provider.__class__.__name__}")
    
    tests = load_test_cases()
    if not tests:
        print("⚠️ Không tìm thấy test cases!")
        return
    
    print(f"✅ Đã tải {len(tests)} test cases\n")
    
    for i, test in enumerate(tests, 1):
        test_input = test.get("input") or test.get("question") or ""
        test_type = test.get("type") or test.get("category") or "N/A"
        print(f"\n{'='*60}")
        print(f"📋 TEST #{i}: {test_type}")
        print(f"📝 Input: {test_input[:100]}...")
        print(f"{'='*60}")
        
        start = time.time()
        result = route_query(test_input, provider)
        elapsed = time.time() - start
        
        print(f"\n📤 Output ({elapsed:.2f}s):\n{result[:500]}...")
        
        # Kiểm tra kỳ vọng
        expected = test.get('expected_behavior', '')
        if test_type == 'simple' and 'gọi tool' in expected.lower():
            print("⚠️ [FAIL] Simple query không nên gọi tool!")
        elif test_type == 'edge_empty' and 'top 3' in result.lower():
            print("⚠️ [FAIL] Edge case rỗng không nên trả Top 3!")
        
        print(f"\n⏱️ Thời gian: {elapsed:.2f}s")


# ============================================================================
# 💬 CLI INTERFACE
# ============================================================================

def run_cli():
    """Chạy chatbot CLI tương tác"""
    print("=" * 60)
    print("💕 CUPRESS AGENT - INTERACTIVE CLI")
    print("=" * 60)
    
    provider = get_llm_provider()
    print(f"🔌 Provider: {provider.__class__.__name__}")
    print("\n💡 Gõ 'exit' hoặc 'quit' để thoát\n")
    
    while True:
        try:
            user_input = input("👤 Bạn: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'thoát', 'q']:
                print("\n💕 Cảm ơn bạn đã trò chuyện! Chúc bạn tìm được người phù hợp! 💘")
                break
            
            print("\n💕 Cupid đang suy nghĩ...")
            response = route_query(user_input, provider)
            print(f"\n💕 Cupid: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\n💕 Tạm biệt! 💘")
            break
        except Exception as e:
            print(f"\n⚠️ Lỗi: {str(e)}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Cupid Agent - ReAct Chatbot")
    parser.add_argument("--test", action="store_true", help="Chạy test cases")
    parser.add_argument("--cli", action="store_true", help="Chạy CLI tương tác")
    parser.add_argument("--query", type=str, help="Chạy một câu hỏi cụ thể")
    
    args = parser.parse_args()
    
    if args.test:
        run_test_cases()
    elif args.query:
        provider = get_llm_provider()
        result = route_query(args.query, provider)
        print(result)
    else:
        run_cli()
