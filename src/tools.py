"""
🛠️ TOOL REGISTRY & SCHEMAS - Cupid Agent
Các công cụ phục vụ hệ thống Chatbot ghép đôi thông minh.

Luồng Chatbot (theo test_cases.json):
  Người dùng chat --> parse_user_profile (Gemini API)
                  --> search_profiles
                  --> filter_candidates  (loại điều kiện cứng + guardrails)
                  --> calculate_compatibility_score (Gemini API, từng ứng viên)
                  --> rank_matches
                  --> detect_red_flags   (tùy chọn)
                  --> suggest_opening_message / suggest_date_ideas
"""

import json
import re
import os
import sys

# Đảm bảo import providers từ cùng thư mục src/
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ─────────────────────────────────────────────────────────────
# 📦 DỮ LIỆU MẪU  (10 hồ sơ ứng viên)
# ─────────────────────────────────────────────────────────────
MOCK_CANDIDATES = [
    {
        "id": 1, "name": "Minh Anh", "gender": "nữ", "age": 24, "location": "Hà Nội",
        "hobbies": ["đọc sách", "cà phê yên tĩnh", "trò chuyện sâu"],
        "personality": "hướng nội", "relationship_goal": "nghiêm túc",
        "lifestyle": "ổn định", "deal_breakers": ["hút thuốc"],
        "notes": "Khá bận vào cuối tuần, cần hẹn lịch trước."
    },
    {
        "id": 2, "name": "Hoàng Nam", "gender": "nam", "age": 26, "location": "Hà Nội",
        "hobbies": ["thể thao", "du lịch", "cà phê"],
        "personality": "hướng ngoại", "relationship_goal": "nghiêm túc",
        "lifestyle": "năng động", "deal_breakers": ["yêu xa"],
        "notes": "Thích người có thể đi du lịch cùng."
    },
    {
        "id": 3, "name": "Gia Huy", "gender": "nam", "age": 23, "location": "TP.HCM",
        "hobbies": ["chơi game", "xem phim", "nuôi mèo"],
        "personality": "hướng nội", "relationship_goal": "tìm hiểu",
        "lifestyle": "hay thức khuya", "deal_breakers": ["ghét động vật"],
        "notes": "Rất yêu động vật, đặc biệt là mèo."
    },
    {
        "id": 4, "name": "Bảo Ngọc", "gender": "nữ", "age": 25, "location": "Hà Nội",
        "hobbies": ["nghệ thuật", "chụp ảnh", "cà phê yên tĩnh"],
        "personality": "hướng nội", "relationship_goal": "nghiêm túc",
        "lifestyle": "nghệ thuật", "deal_breakers": ["người không tôn trọng không gian riêng"],
        "notes": "Thích những buổi hẹn hò ở bảo tàng hoặc triển lãm."
    },
    {
        "id": 5, "name": "Tuấn Kiệt", "gender": "nam", "age": 27, "location": "Hà Nội",
        "hobbies": ["đọc sách", "kinh doanh", "gym"],
        "personality": "hướng ngoại", "relationship_goal": "nghiêm túc",
        "lifestyle": "kỷ luật", "deal_breakers": ["hút thuốc"],
        "notes": "Đề cao sự nghiệp và sự ổn định."
    },
    {
        "id": 6, "name": "Lan Chi", "gender": "nữ", "age": 22, "location": "Hà Nội",
        "hobbies": ["mua sắm", "làm đẹp", "đi bar"],
        "personality": "hướng ngoại", "relationship_goal": "tìm hiểu",
        "lifestyle": "thích tiệc tùng", "deal_breakers": ["người quá kiểm soát"],
        "notes": "Thích những buổi hẹn hò sôi động và vui vẻ."
    },
    {
        "id": 7, "name": "Quốc Bảo", "gender": "nam", "age": 28, "location": "Hà Nội",
        "hobbies": ["nấu ăn", "chăm sóc gia đình", "đọc sách"],
        "personality": "hướng nội", "relationship_goal": "kết hôn",
        "lifestyle": "hướng về gia đình", "deal_breakers": ["yêu xa", "không thích trẻ con"],
        "notes": "Rất giỏi nấu ăn và thích nấu cho người yêu."
    },
    {
        "id": 8, "name": "Hải Yến", "gender": "nữ", "age": 24, "location": "Hà Nội",
        "hobbies": ["yoga", "thiền", "ăn chay"],
        "personality": "hướng nội", "relationship_goal": "nghiêm túc",
        "lifestyle": "lành mạnh, tối giản", "deal_breakers": ["người thường xuyên nhậu nhẹt"],
        "notes": "Quan tâm nhiều đến sức khỏe tinh thần."
    },
    {
        "id": 9, "name": "Đức Trí", "gender": "nam", "age": 26, "location": "TP.HCM",
        "hobbies": ["công nghệ", "code", "nghe nhạc"],
        "personality": "hướng nội", "relationship_goal": "nghiêm túc",
        "lifestyle": "bận rộn", "deal_breakers": ["người không tôn trọng thời gian cá nhân"],
        "notes": "Là kỹ sư phần mềm, khá bận rộn trong tuần."
    },
    {
        "id": 10, "name": "Thu Thảo", "gender": "nữ", "age": 23, "location": "Hà Nội",
        "hobbies": ["dã ngoại", "đạp xe", "nuôi chó"],
        "personality": "hướng ngoại", "relationship_goal": "tìm hiểu",
        "lifestyle": "năng động, yêu thiên nhiên", "deal_breakers": ["người thụ động"],
        "notes": "Rất thích các hoạt động ngoài trời và mạo hiểm nhẹ."
    }
]

def load_candidates():
    """
    Load candidate profiles from config/candidate_profiles.json.
    Falls back to MOCK_CANDIDATES if file not found.
    """
    # Determine project root (src/ -> project root)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    config_path = os.path.join(project_root, "config", "candidate_profiles.json")
    
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                candidates = json.load(f)
            if isinstance(candidates, list) and len(candidates) > 0:
                return candidates
        except (json.JSONDecodeError, IOError):
            pass  # Fallback to MOCK_CANDIDATES
    
    return MOCK_CANDIDATES


# ─────────────────────────────────────────────────────────────
# 🔧 HÀM PHỤ TRỢ NỘI BỘ
# ─────────────────────────────────────────────────────────────

def _get_gemini_provider():
    """Khởi tạo GeminiProvider từ module providers."""
    from providers import GeminiProvider
    return GeminiProvider()

def _parse_json_arg(arg):
    """Parse chuỗi JSON từ Agent, xử lý các format không chuẩn (markdown code block...)."""
    if isinstance(arg, (dict, list)):
        return arg
    if not isinstance(arg, str):
        return None
    try:
        arg = arg.strip()
        # Bóc markdown code block nếu có
        if arg.startswith("```json"):
            arg = arg[7:]
        if arg.startswith("```"):
            arg = arg[3:]
        if arg.endswith("```"):
            arg = arg[:-3]
        return json.loads(arg.strip())
    except Exception:
        return None

def _is_safety_violation(text: str) -> bool:
    """Guardrail: Phát hiện các yêu cầu vi phạm an toàn (ép buộc, theo dõi, thao túng)."""
    dangerous_keywords = [
        "ép buộc", "bắt buộc", "theo dõi", "bí mật", "hack", "xâm nhập",
        "thao túng", "bẫy", "lừa", "chiếm đoạt", "làm hại", "cưỡng bức",
        "stalk", "force", "manipulate", "spy", "bắt cóc"
    ]
    text_lower = text.lower()
    return any(kw in text_lower for kw in dangerous_keywords)

def _is_insufficient_info(profile: dict) -> bool:
    """Guardrail: Kiểm tra hồ sơ có đủ thông tin cơ bản để tìm kiếm không."""
    # Cần ít nhất 2 trong 3: location, relationship_goal, hobbies (hoặc personality)
    has_location = bool(profile.get("location", "").strip())
    has_goal = bool(profile.get("relationship_goal", "").strip())
    has_hobbies = len(profile.get("hobbies", [])) > 0
    has_personality = bool(profile.get("personality", "").strip())
    filled_count = sum([has_location, has_goal, has_hobbies or has_personality])
    return filled_count < 2


def _parse_profile_offline(profile_text: str) -> dict:
    """Fallback parser for mock/offline mode so lab demos work without an API key."""
    text = profile_text.lower()
    profile = {
        "gender": "",
        "target_gender": "",
        "age": None,
        "location": "",
        "hobbies": [],
        "personality": "",
        "relationship_goal": "",
        "deal_breakers": [],
    }

    if " nữ" in f" {text}" or "là nữ" in text:
        profile["gender"] = "nữ"
    elif " nam" in f" {text}" or "là nam" in text:
        profile["gender"] = "nam"

    if re.search(r"tìm\s+(bạn\s+)?nam|người\s+nam|đối tượng\s+nam", text):
        profile["target_gender"] = "nam"
    elif re.search(r"tìm\s+(bạn\s+)?nữ|người\s+nữ|đối tượng\s+nữ", text):
        profile["target_gender"] = "nữ"

    age_match = re.search(r"(\d+)\s*tuổi", text)
    if age_match:
        profile["age"] = int(age_match.group(1))

    locations = {
        "hà nội": "Hà Nội",
        "ha noi": "Hà Nội",
        "tp.hcm": "TP.HCM",
        "tphcm": "TP.HCM",
        "hồ chí minh": "TP.HCM",
        "đà nẵng": "Đà Nẵng",
        "da nang": "Đà Nẵng",
        "hà giang": "Hà Giang",
        "atlantis": "Atlantis",
    }
    for keyword, location in locations.items():
        if keyword in text:
            profile["location"] = location
            break

    hobby_keywords = [
        "đọc sách", "cà phê yên tĩnh", "cà phê", "du lịch bụi", "du lịch",
        "đua xe f1", "đi quẩy", "ở nhà", "tiết kiệm", "tiêu xài",
        "yoga", "thiền", "nấu ăn", "xem phim", "chơi game"
    ]
    profile["hobbies"] = [hobby for hobby in hobby_keywords if hobby in text]

    if "hướng nội" in text:
        profile["personality"] = "hướng nội"
    elif "hướng ngoại" in text:
        profile["personality"] = "hướng ngoại"

    if "không muốn kết hôn" in text or "chưa muốn kết hôn" in text:
        profile["relationship_goal"] = "tìm hiểu"
    elif "kết hôn" in text:
        profile["relationship_goal"] = "kết hôn"
    elif "nghiêm túc" in text:
        profile["relationship_goal"] = "nghiêm túc"
    elif "tìm hiểu" in text:
        profile["relationship_goal"] = "tìm hiểu"

    if "không hút thuốc" in text or "không thích người hút thuốc" in text:
        profile["deal_breakers"].append("hút thuốc")
    if "không yêu xa" in text:
        profile["deal_breakers"].append("yêu xa")

    return profile


# ─────────────────────────────────────────────────────────────
# ✅ TOOL 1: PARSE USER PROFILE  (sử dụng Gemini API)
# ─────────────────────────────────────────────────────────────

def parse_user_profile(profile_text: str) -> str:
    """
    [Tool 1] Phân tích đoạn văn bản / câu chat tự do của người dùng,
    trích xuất thành hồ sơ JSON chuẩn dùng cho các bước tìm kiếm & match.
    Sử dụng Gemini API để đảm bảo hiểu được mọi cách diễn đạt tự nhiên.

    Args:
        profile_text (str): Đoạn văn bản giới thiệu bản thân hoặc câu chat của người dùng.

    Returns:
        str: JSON string gồm các field: gender, age, location, hobbies,
             personality, relationship_goal, deal_breakers.
             Trả về JSON với key "error" nếu gặp lỗi hoặc vi phạm guardrail.
    """
    # ── Guardrail 1: An toàn ──
    if _is_safety_violation(profile_text):
        return json.dumps({
            "error": "SAFETY_VIOLATION",
            "message": "Yêu cầu của bạn vi phạm quy tắc an toàn. Cupid Agent không hỗ trợ các yêu cầu ép buộc, theo dõi hoặc thao túng người khác."
        }, ensure_ascii=False)

    if not profile_text or not profile_text.strip():
        return json.dumps({}, ensure_ascii=False)

    try:
        provider = _get_gemini_provider()

        system_prompt = """Bạn là chuyên gia phân tích hồ sơ hẹn hò (NLP Specialist).
Đọc đoạn giới thiệu bản thân và trích xuất thông tin thành JSON với đúng các trường sau:

{
  "gender": "nam hoặc nữ (để trống nếu không đề cập)",
  "target_gender": "nam hoặc nữ nếu người dùng nói rõ muốn tìm giới tính nào (để trống nếu không đề cập)",
  "age": số nguyên tuổi (null nếu không có),
  "location": "thành phố/tỉnh sinh sống (để trống nếu không có)",
  "hobbies": ["sở thích 1", "sở thích 2", ...],
  "personality": "hướng nội hoặc hướng ngoại (để trống nếu không rõ)",
  "relationship_goal": "kết hôn | nghiêm túc | tìm hiểu (để trống nếu không có)",
  "deal_breakers": ["điều không chấp nhận 1", "điều không chấp nhận 2", ...]
}

QUAN TRỌNG:
- Chỉ trả về JSON thuần túy. KHÔNG giải thích, KHÔNG markdown, KHÔNG ```json```.
- Nếu không tìm thấy thông tin, dùng giá trị rỗng ("", null, hoặc [])."""

        response = provider.generate(prompt=profile_text, system_prompt=system_prompt)
        parsed = _parse_json_arg(response)

        if parsed and isinstance(parsed, dict):
            return json.dumps(parsed, ensure_ascii=False, indent=2)
        else:
            return json.dumps(_parse_profile_offline(profile_text), ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps(_parse_profile_offline(profile_text), ensure_ascii=False, indent=2)


# ─────────────────────────────────────────────────────────────
# ✅ TOOL 2: SEARCH PROFILES
# ─────────────────────────────────────────────────────────────

def search_profiles(criteria: str) -> str:
    """
    [Tool 2] Tìm kiếm hồ sơ ứng viên theo tiêu chí từ khóa đơn giản.
    Nếu criteria rỗng, trả về toàn bộ danh sách.

    Args:
        criteria (str): Từ khóa tìm kiếm, cách nhau bằng dấu phẩy.
                        VD: "Hà Nội, nghiêm túc, hướng nội"
                        Để trống ("") để lấy tất cả ứng viên.

    Returns:
        str: JSON array danh sách hồ sơ ứng viên tìm được.
    """
    if not criteria or not criteria.strip():
        return json.dumps(MOCK_CANDIDATES, ensure_ascii=False)

    # ── Guardrail: Tuổi không hợp lệ (>100 hoặc <10) ──
    age_mentions = re.findall(r'(\d+)\s*tuổi', criteria)
    for age_str in age_mentions:
        age = int(age_str)
        if age > 100 or age < 10:
            return json.dumps({
                "error": "INVALID_PARAMS",
                "message": f"Tuổi {age} không hợp lệ. Hệ thống chỉ hỗ trợ tìm kiếm trong khoảng 18–60 tuổi."
            }, ensure_ascii=False)

    criteria_lower = criteria.lower()
    keywords = [kw.strip() for kw in criteria_lower.split(",") if kw.strip()]
    results = []
    for cand in MOCK_CANDIDATES:
        cand_str = json.dumps(cand, ensure_ascii=False).lower()
        if any(kw in cand_str for kw in keywords):
            results.append(cand)

    if not results:
        # Trả về tất cả để các tool sau tự lọc thêm
        results = MOCK_CANDIDATES

    return json.dumps(results, ensure_ascii=False)


# ─────────────────────────────────────────────────────────────
# ✅ TOOL 3: FILTER CANDIDATES
# ─────────────────────────────────────────────────────────────

def filter_candidates(user_profile: str, candidate_profiles: str) -> str:
    """
    [Tool 3] Lọc ứng viên theo điều kiện cứng: vị trí (nếu không muốn yêu xa),
    deal breakers hai chiều (người dùng và ứng viên).

    Args:
        user_profile (str): JSON string hồ sơ người dùng (output của parse_user_profile).
        candidate_profiles (str): JSON string danh sách ứng viên (output của search_profiles).

    Returns:
        str: JSON array danh sách ứng viên hợp lệ sau khi lọc.
             Trả về mảng rỗng [] nếu không có ai phù hợp.
             Trả về JSON với key "error" nếu dữ liệu đầu vào không hợp lệ.
    """
    user = _parse_json_arg(user_profile)
    candidates = _parse_json_arg(candidate_profiles)

    # ── Guardrail: Dữ liệu không hợp lệ ──
    if not user or not isinstance(user, dict):
        return json.dumps({
            "error": "INVALID_INPUT",
            "message": "Hồ sơ người dùng không hợp lệ hoặc thiếu thông tin cần thiết."
        }, ensure_ascii=False)

    if not candidates or not isinstance(candidates, list):
        return json.dumps({
            "error": "INVALID_INPUT",
            "message": "Danh sách ứng viên không hợp lệ."
        }, ensure_ascii=False)

    # ── Guardrail: Thông tin người dùng quá mơ hồ ──
    if _is_insufficient_info(user):
        return json.dumps({
            "error": "INSUFFICIENT_INFO",
            "message": "Thông tin hồ sơ quá mơ hồ. Bạn có thể cho Cupid biết thêm về nơi ở, mục tiêu quan hệ hoặc sở thích của bạn không?"
        }, ensure_ascii=False)

    user_location = user.get("location", "").strip().lower()
    user_gender = user.get("gender", "").strip().lower()
    target_gender = user.get("target_gender", "").strip().lower()
    if not target_gender and user_gender in {"nam", "nữ"}:
        # Demo lab mặc định ghép đôi khác giới khi người dùng không nói rõ preference.
        # Nếu muốn hỗ trợ mọi xu hướng, truyền target_gender rõ ràng trong user_profile.
        target_gender = "nữ" if user_gender == "nam" else "nam"
    user_deal_breakers = [db.lower().strip() for db in user.get("deal_breakers", [])]
    no_long_distance = "yêu xa" in user_deal_breakers

    filtered = []
    for cand in candidates:
        valid = True
        cand_gender = cand.get("gender", "").strip().lower()
        cand_location = cand.get("location", "").strip().lower()
        cand_str = json.dumps(cand, ensure_ascii=False).lower()

        # Lọc 1: Giới tính mục tiêu
        if target_gender and cand_gender and cand_gender != target_gender:
            valid = False

        # Lọc 2: Không yêu xa
        if no_long_distance and user_location and cand_location and user_location != cand_location:
            valid = False

        # Lọc 3: Deal breakers của người dùng vi phạm thông tin ứng viên
        if valid:
            for db in user_deal_breakers:
                if db != "yêu xa" and db in cand_str:
                    valid = False
                    break

        # Lọc 4: Deal breakers của ứng viên vi phạm thông tin người dùng
        if valid:
            cand_dbs = [db.lower().strip() for db in cand.get("deal_breakers", [])]
            user_str = json.dumps(user, ensure_ascii=False).lower()
            for db in cand_dbs:
                if db != "yêu xa" and db in user_str:
                    valid = False
                    break

        if valid:
            filtered.append(cand)

    return json.dumps(filtered, ensure_ascii=False)


# ─────────────────────────────────────────────────────────────
# ✅ TOOL 4: CALCULATE COMPATIBILITY SCORE  (sử dụng Gemini API)
# ─────────────────────────────────────────────────────────────

def calculate_compatibility_score(user_profile: str, candidate_profile: str) -> str:
    """
    [Tool 4] Tính điểm tương thích giữa người dùng và một ứng viên,
    sử dụng Gemini API để phân tích toàn diện (tính cách, mục tiêu, sở thích, lifestyle).

    Args:
        user_profile (str): JSON string hồ sơ người dùng.
        candidate_profile (str): JSON string hồ sơ một ứng viên.

    Returns:
        str: JSON string của ứng viên được gắn thêm 2 field mới:
             - compatibility_score (int 0–100)
             - compatibility_reason (str giải thích ngắn gọn)
             Trả về JSON với key "error" nếu lỗi.
    """
    cand = _parse_json_arg(candidate_profile)

    if not user_profile or not candidate_profile:
        return json.dumps({"error": "INVALID_INPUT", "message": "Thiếu dữ liệu đầu vào."}, ensure_ascii=False)

    try:
        provider = _get_gemini_provider()

        system_prompt = """Bạn là chuyên gia tâm lý học và tư vấn tình cảm (Matchmaker chuyên nghiệp).
Đánh giá độ tương thích giữa hai hồ sơ dưới đây theo thang 0–100.

Tiêu chí chấm điểm:
1. Mục tiêu quan hệ (30đ): Giống nhau = +30, khác nhau nghiêm trọng (kết hôn vs tìm hiểu) = -20
2. Tính cách (20đ): Cùng hướng nội/ngoại = +20, bù trừ hợp lý = +10, xung đột = +5
3. Sở thích chung (20đ): Mỗi sở thích chung +5đ, tối đa 20đ
4. Deal breakers (20đ tối đa): Vi phạm deal breaker = -20 (nặng nhất)
5. Lifestyle & giá trị sống (10đ): Phong cách sống phù hợp = +10

Trả về DUY NHẤT JSON sau (không text ngoài, không markdown):
{
  "compatibility_score": <số nguyên 0-100>,
  "compatibility_reason": "<2-3 câu giải thích cụ thể lý do điểm cao/thấp>"
}"""

        prompt = f"HỒ SƠ NGƯỜI DÙNG:\n{user_profile}\n\nHỒ SƠ ỨNG VIÊN:\n{candidate_profile}"
        response = provider.generate(prompt=prompt, system_prompt=system_prompt)
        
        # Xử lý JSON prettified (indent=2) và plain
        parsed = _parse_json_arg(response)

        # Merge kết quả vào candidate object gốc
        if isinstance(cand, dict) and isinstance(parsed, dict):
            cand["compatibility_score"] = int(parsed.get("compatibility_score", 50))
            cand["compatibility_reason"] = parsed.get("compatibility_reason") or parsed.get("reason") or "Phù hợp dựa trên thông tin có sẵn."
            return json.dumps(cand, ensure_ascii=False)
        elif isinstance(parsed, dict):
            return json.dumps(parsed, ensure_ascii=False)
        else:
            # Fallback: parse thủ công nếu Gemini trả về text không chuẩn
            score_match = re.search(r'"compatibility_score"\s*:\s*(\d+)', response)
            reason_match = re.search(r'"compatibility_reason"\s*:\s*"?([^",\n}]+)"?', response)
            if isinstance(cand, dict):
                cand["compatibility_score"] = int(score_match.group(1)) if score_match else 50
                cand["compatibility_reason"] = reason_match.group(1).strip() if reason_match else "Phù hợp dựa trên thông tin có sẵn."
                return json.dumps(cand, ensure_ascii=False)
            return response

    except Exception as e:
        return json.dumps({"error": f"Lỗi calculate_compatibility_score: {str(e)}"}, ensure_ascii=False)


# ─────────────────────────────────────────────────────────────
# ✅ TOOL 5: RANK MATCHES
# ─────────────────────────────────────────────────────────────

def rank_matches(scored_candidates: str) -> str:
    """
    [Tool 5] Sắp xếp danh sách ứng viên (đã có compatibility_score) từ cao xuống thấp.

    Args:
        scored_candidates (str): JSON array ứng viên đã được chấm điểm
                                 (output nhiều lần từ calculate_compatibility_score).

    Returns:
        str: JSON array ứng viên đã xếp hạng theo compatibility_score giảm dần.
             Trả về JSON với key "error" nếu dữ liệu không hợp lệ.
    """
    candidates = _parse_json_arg(scored_candidates)

    if not candidates or not isinstance(candidates, list):
        return json.dumps({
            "error": "INVALID_INPUT",
            "message": "Danh sách ứng viên không hợp lệ hoặc rỗng."
        }, ensure_ascii=False)

    # Lọc những ứng viên không có điểm (lỗi từ bước trước)
    valid = [c for c in candidates if isinstance(c, dict) and "compatibility_score" in c]

    if not valid:
        return json.dumps({
            "error": "NO_SCORED_CANDIDATES",
            "message": "Không có ứng viên nào được chấm điểm thành công."
        }, ensure_ascii=False)

    valid.sort(key=lambda x: x.get("compatibility_score", 0), reverse=True)
    return json.dumps(valid, ensure_ascii=False)


# ─────────────────────────────────────────────────────────────
# ✅ TOOL 6: DETECT RED FLAGS
# ─────────────────────────────────────────────────────────────

def detect_red_flags(user_profile: str, candidate_profile: str) -> str:
    """
    [Tool 6] Phát hiện và liệt kê các điểm rủi ro, mâu thuẫn trong mối quan hệ
    giữa người dùng và ứng viên.

    Args:
        user_profile (str): JSON string hồ sơ người dùng.
        candidate_profile (str): JSON string hồ sơ ứng viên.

    Returns:
        str: Chuỗi văn bản cảnh báo các red flags tìm được (hoặc thông báo an toàn).
    """
    user = _parse_json_arg(user_profile)
    cand = _parse_json_arg(candidate_profile)

    if not user or not isinstance(user, dict):
        return "Lỗi: Hồ sơ người dùng không hợp lệ."
    if not cand or not isinstance(cand, dict):
        return "Lỗi: Hồ sơ ứng viên không hợp lệ."

    flags = []
    cand_name = cand.get("name", "Ứng viên")

    # Red flag 1: Chênh lệch tuổi > 10
    user_age = user.get("age")
    cand_age = cand.get("age")
    if user_age and cand_age and abs(user_age - cand_age) > 10:
        flags.append(f"⚠️ Chênh lệch tuổi lớn ({user_age} vs {cand_age} tuổi). Có thể tạo ra sự khác biệt trong quan điểm sống.")

    # Red flag 2: Mục tiêu quan hệ trái ngược nghiêm trọng
    ug = user.get("relationship_goal", "").lower()
    cg = cand.get("relationship_goal", "").lower()
    if ug and cg and ug != cg:
        serious_mismatch = (
            ("kết hôn" in ug and "tìm hiểu" in cg) or
            ("kết hôn" in cg and "tìm hiểu" in ug)
        )
        if serious_mismatch:
            flags.append(f"🚨 Mục tiêu quan hệ khác biệt rõ rệt: Bạn muốn '{ug}' nhưng {cand_name} hướng đến '{cg}'. Đây là điểm bất đồng quan trọng cần thảo luận sớm.")
        else:
            flags.append(f"⚠️ Mục tiêu quan hệ chưa hoàn toàn thống nhất ('{ug}' vs '{cg}'). Nên làm rõ ngay từ đầu.")

    # Red flag 3: Lifestyle xung đột
    user_life = user.get("lifestyle", "").lower()
    cand_life = cand.get("lifestyle", "").lower()
    conflict_pairs = [
        ("thức khuya", "ngủ sớm"), ("tiệc tùng", "tối giản"),
        ("năng động", "ổn định"), ("tiêu xài", "tiết kiệm")
    ]
    for kw1, kw2 in conflict_pairs:
        if (kw1 in user_life and kw2 in cand_life) or (kw2 in user_life and kw1 in cand_life):
            flags.append(f"⚠️ Phong cách sống có thể xung đột: '{user_life}' vs '{cand_life}'.")

    # Red flag 4: Deal breakers bị vi phạm (cảnh báo bổ sung ngoài filter)
    user_dbs = [db.lower() for db in user.get("deal_breakers", [])]
    cand_str_lower = json.dumps(cand, ensure_ascii=False).lower()
    for db in user_dbs:
        if db != "yêu xa" and db in cand_str_lower:
            flags.append(f"🚨 Vi phạm điều bạn không chấp nhận: '{db}'.")

    if not flags:
        return (f"✅ Không phát hiện red flag nghiêm trọng với {cand_name}. "
                "Tuy nhiên, luôn cần thời gian tìm hiểu thực tế và tôn trọng ranh giới cá nhân của nhau.")

    intro = f"🔍 Các điểm cần lưu ý khi tìm hiểu {cand_name}:\n"
    return intro + "\n".join(flags)


# ─────────────────────────────────────────────────────────────
# ✅ TOOL 7: SUGGEST OPENING MESSAGE
# ─────────────────────────────────────────────────────────────

def suggest_opening_message(user_profile: str, candidate_profile: str) -> str:
    """
    [Tool 7] Gợi ý tin nhắn mở lời (icebreaker) dựa trên điểm chung giữa
    người dùng và ứng viên. Ưu tiên khai thác sở thích chung cụ thể.

    Args:
        user_profile (str): JSON string hồ sơ người dùng.
        candidate_profile (str): JSON string hồ sơ ứng viên.

    Returns:
        str: Gợi ý câu mở lời tự nhiên, thân thiện.
    """
    user = _parse_json_arg(user_profile)
    cand = _parse_json_arg(candidate_profile)

    cand_name = cand.get("name", "bạn") if isinstance(cand, dict) else "bạn"

    if not user or not isinstance(user, dict) or not cand or not isinstance(cand, dict):
        return f'💬 Gợi ý: "Chào {cand_name}, mình thấy hồ sơ của bạn khá ấn tượng. Bạn có thể kể thêm về bản thân không?"'

    # Tìm sở thích chung
    user_hobbies = set(h.lower().strip() for h in user.get("hobbies", []))
    cand_hobbies = set(h.lower().strip() for h in cand.get("hobbies", []))
    common = list(user_hobbies.intersection(cand_hobbies))

    if common:
        hobby = common[0]
        templates = [
            f'"Chào {cand_name}, mình thấy bạn cũng thích {hobby}! Bạn hay {hobby} ở đâu vậy?"',
            f'"Ồ, bạn cũng mê {hobby} à? Mình mới {hobby} tuần trước xong và thấy rất vui. Bạn thích điểm gì nhất ở {hobby}?"',
            f'"Chào {cand_name}! Mình để ý bạn thích {hobby} – đây cũng là điều mình yêu thích. Mình nên bắt đầu cuộc trò chuyện từ đây thôi 😄"'
        ]
        return '💬 ' + templates[0]

    # Nếu không có sở thích chung, khai thác personality hoặc location
    cand_personality = cand.get("personality", "")
    cand_location = cand.get("location", "")
    if cand_location:
        return f'💬 Gợi ý: "Chào {cand_name}, mình thấy bạn cũng đang ở {cand_location}. Gần đây có quán nào hay không bạn?"'

    return f'💬 Gợi ý: "Chào {cand_name}, đọc hồ sơ của bạn mình thấy khá hợp nhau. Bạn có muốn trò chuyện thêm không?"'


# ─────────────────────────────────────────────────────────────
# ✅ TOOL 8: SUGGEST DATE IDEAS
# ─────────────────────────────────────────────────────────────

def suggest_date_ideas(user_profile: str, candidate_profile: str, budget: str = "thoải mái", location: str = "") -> str:
    """
    [Tool 8] Gợi ý ý tưởng hẹn hò phù hợp dựa trên sở thích chung,
    tính cách của cả hai và ngân sách / địa điểm mong muốn.

    Args:
        user_profile (str): JSON string hồ sơ người dùng.
        candidate_profile (str): JSON string hồ sơ ứng viên.
        budget (str): Ngân sách (VD: "200k", "500k", "thoải mái"). Mặc định: "thoải mái".
        location (str): Thành phố muốn hẹn hò. Nếu rỗng, dùng location của ứng viên.

    Returns:
        str: Danh sách 2–4 ý tưởng date được cá nhân hóa.
    """
    user = _parse_json_arg(user_profile)
    cand = _parse_json_arg(candidate_profile)

    user_hobbies = [h.lower() for h in user.get("hobbies", [])] if isinstance(user, dict) else []
    cand_hobbies = [h.lower() for h in cand.get("hobbies", [])] if isinstance(cand, dict) else []
    all_hobbies = user_hobbies + cand_hobbies

    cand_name = cand.get("name", "bạn") if isinstance(cand, dict) else "bạn"
    if not location and isinstance(cand, dict):
        location = cand.get("location", "thành phố bạn đang sống")

    ideas = []

    # Gợi ý dựa trên sở thích
    if any(h in all_hobbies for h in ["đọc sách", "cà phê", "cà phê yên tĩnh", "trò chuyện sâu"]):
        ideas.append("☕ Hẹn tại một quán cà phê sách yên tĩnh – vừa đọc, vừa trò chuyện không áp lực.")
    if any(h in all_hobbies for h in ["nghệ thuật", "chụp ảnh"]):
        ideas.append("🎨 Cùng nhau thăm triển lãm tranh hoặc bảo tàng nghệ thuật – rất hợp cho người thích sáng tạo.")
    if any(h in all_hobbies for h in ["thể thao", "gym", "đạp xe", "dã ngoại"]):
        ideas.append("🚴 Buổi sáng đạp xe quanh hồ hoặc đi bộ leo núi nhẹ – năng động và gần gũi thiên nhiên.")
    if any(h in all_hobbies for h in ["nuôi chó", "nuôi mèo", "thú cưng"]):
        ideas.append("🐾 Hẹn tại quán cà phê thú cưng – vừa cute vừa dễ phá băng.")
    if any(h in all_hobbies for h in ["du lịch"]):
        ideas.append("🗺️ Lên kế hoạch chuyến day-trip cùng nhau đến vùng ngoại ô gần đó.")
    if any(h in all_hobbies for h in ["nấu ăn"]):
        ideas.append("🍳 Cùng nhau nấu một bữa ăn tại nhà – vừa vui, vừa thể hiện được sự chăm sóc.")
    if any(h in all_hobbies for h in ["xem phim", "chơi game"]):
        ideas.append("🎬 Xem phim tại rạp hoặc ở nhà cùng nhau – thư giãn và thoải mái cho buổi đầu.")
    if any(h in all_hobbies for h in ["yoga", "thiền"]):
        ideas.append("🧘 Tham gia buổi yoga hoặc thiền cùng nhau tại công viên vào sáng cuối tuần.")

    # Fallback nếu không match sở thích nào
    if not ideas:
        ideas = [
            "☕ Gặp nhau uống cà phê tại một không gian yên tĩnh để có cuộc trò chuyện chân thật.",
            "🌳 Đi dạo quanh công viên – nhẹ nhàng, không áp lực và dễ kéo dài tự nhiên."
        ]

    header = f"📅 Gợi ý date cho bạn và {cand_name} tại {location} (Ngân sách: {budget}):\n"
    body = "\n".join(f"{i+1}. {idea}" for i, idea in enumerate(ideas[:4]))
    footer = "\n\n💡 Lưu ý: Hãy hỏi ý kiến đối phương trước khi quyết định địa điểm. Sự tôn trọng là nền tảng của mọi cuộc hẹn tốt đẹp."
    return header + body + footer


# ─────────────────────────────────────────────────────────────
# AVAILABLE_TOOLS: Đăng ký tất cả tool để Agent gọi
# ─────────────────────────────────────────────────────────────
AVAILABLE_TOOLS = {
    "parse_user_profile": parse_user_profile,
    "search_profiles": search_profiles,
    "filter_candidates": filter_candidates,
    "calculate_compatibility_score": calculate_compatibility_score,
    "rank_matches": rank_matches,
    "detect_red_flags": detect_red_flags,
    "suggest_opening_message": suggest_opening_message,
    "suggest_date_ideas": suggest_date_ideas,
}
