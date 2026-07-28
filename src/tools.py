"""
Cupid Agent Tools - ReAct Agent Tools Implementation
Role 2: Tool Engineer - Implement các công cụ cho Agent

HIỆN TRẠNG: Mock implementations - Role 2 sẽ implement thật sau
"""

import json
import os
from typing import List, Dict, Any, Optional


# =============================================================================
# DATA LOADING
# =============================================================================

def get_data_path(filename: str) -> str:
    """Get path to data files"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "config", filename)


def load_candidates() -> List[Dict]:
    """Load candidate profiles from JSON file"""
    data_path = get_data_path("candidate_profiles.json")
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []


def load_current_user() -> Dict:
    """Load current user profile from config"""
    data_path = get_data_path("current_user.json")
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        # Return default user
        return {
            "name": "Người dùng",
            "age": 25,
            "gender": "Nữ",
            "location": "Hà Nội",
            "personality": "hướng nội, thích đọc sách",
            "interests": ["đọc sách", "cà phê yên tĩnh"],
            "goal": "Nghiêm túc",
            "no_smoking": True,
            "no_long_distance": True
        }


# =============================================================================
# TOOL 1: search_profiles
# =============================================================================

def search_profiles(criteria: str) -> List[Dict]:
    """
    Tìm hồ sơ ứng viên theo tiêu chí tìm kiếm.
    
    Args:
        criteria (str): Tiêu chí tìm kiếm (VD: "hướng nội, thích đọc sách, Hà Nội")
    
    Returns:
        List[Dict]: Danh sách các hồ sơ phù hợp với tiêu chí
    """
    candidates = load_candidates()
    if not candidates:
        return []
    
    criteria_lower = criteria.lower()
    criteria_words = criteria_lower.replace(",", " ").split()
    
    results = []
    for candidate in candidates:
        score = 0
        matched_fields = []
        
        # Check location
        if any(word in candidate.get("location", "").lower() for word in criteria_words):
            score += 2
            matched_fields.append("location")
        
        # Check personality (can be string or list)
        personality = candidate.get("personality", "")
        if isinstance(personality, list):
            personality = " ".join(personality)
        if any(word in personality.lower() for word in criteria_words):
            score += 2
            matched_fields.append("personality")
        
        # Check interests (can be list or string)
        interests = candidate.get("interests", [])
        if isinstance(interests, str):
            interests = [interests]
        interests_text = " ".join(interests).lower()
        if any(word in interests_text for word in criteria_words):
            score += 1
            matched_fields.append("interests")
        
        # Check relationship goal
        goal = candidate.get("relationship_goal", "")
        if any(word in goal.lower() for word in criteria_words):
            score += 2
            matched_fields.append("relationship_goal")
        
        # Check bio
        bio = candidate.get("bio", "")
        if any(word in bio.lower() for word in criteria_words if len(word) > 3):
            score += 1
            matched_fields.append("bio")
        
        if score > 0:
            results.append({
                "candidate": candidate,
                "match_score": score,
                "matched_fields": matched_fields
            })
    
    # Sort by match score
    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results[:10]  # Return top 10


# =============================================================================
# TOOL 2: filter_candidates
# =============================================================================

def filter_candidates(user_profile: Dict, candidates: List[Dict]) -> List[Dict]:
    """
    Lọc ứng viên theo điều kiện cứng (hard filters).
    
    Args:
        user_profile (Dict): Hồ sơ người dùng
        candidates (List[Dict]): Danh sách ứng viên cần lọc
    
    Returns:
        List[Dict]: Danh sách ứng viên đã lọc
    """
    filtered = []
    
    for candidate in candidates:
        # Get candidate dict if wrapped in match result
        if "candidate" in candidate:
            candidate = candidate["candidate"]
        
        # Skip if same gender (simplified - assume straight relationships)
        user_gender = user_profile.get("gender", "").lower()
        cand_gender = candidate.get("gender", "").lower()
        
        # Handle "Nam" vs "nam", "Nữ" vs "nữ"
        if user_gender in ["nam", "nữ"] and cand_gender in ["nam", "nữ"]:
            if user_gender == cand_gender:
                continue
        
        # Age range check (±10 years)
        age_diff = abs(user_profile.get("age", 25) - candidate.get("age", 25))
        if age_diff > 10:
            continue
        
        # Smoking conflict
        user_no_smoking = user_profile.get("no_smoking", False)
        cand_smoking = candidate.get("smoking", False)
        if user_no_smoking and cand_smoking:
            continue
        
        # Location preference (soft filter - don't exclude different location)
        user_location = user_profile.get("location", "")
        cand_location = candidate.get("location", "")
        
        # Long distance check
        user_no_long_distance = user_profile.get("no_long_distance", False)
        cand_long_distance_ok = candidate.get("long_distance_ok", True)
        
        # If user doesn't want long distance and candidate doesn't support it
        if user_no_long_distance and not cand_long_distance_ok:
            if user_location != cand_location and user_location and cand_location:
                continue
        
        filtered.append(candidate)
    
    return filtered


# =============================================================================
# TOOL 3: calculate_compatibility_score
# =============================================================================

def calculate_compatibility_score(user_profile: Dict, candidate: Dict) -> int:
    """
    Tính điểm tương thích giữa người dùng và ứng viên.
    
    Args:
        user_profile (Dict): Hồ sơ người dùng
        candidate (Dict): Hồ sơ ứng viên
    
    Returns:
        int: Điểm tương thích (0-100)
    """
    score = 50  # Base score
    
    # Location match (+15 points)
    user_location = user_profile.get("location", "")
    cand_location = candidate.get("location", "")
    if user_location and cand_location:
        if user_location.lower() in cand_location.lower() or cand_location.lower() in user_location.lower():
            score += 15
        elif user_location == "Khác" or user_location == "":
            score += 5
    
    # Age compatibility (+10 points max)
    age_diff = abs(user_profile.get("age", 25) - candidate.get("age", 25))
    if age_diff <= 3:
        score += 10
    elif age_diff <= 7:
        score += 5
    elif age_diff <= 10:
        score += 2
    
    # Relationship goal match (+20 points)
    user_goal = user_profile.get("goal", "")
    cand_goal = candidate.get("relationship_goal", "")
    if user_goal and cand_goal:
        user_goal_lower = user_goal.lower()
        cand_goal_lower = cand_goal.lower()
        if user_goal_lower in cand_goal_lower or cand_goal_lower in user_goal_lower:
            score += 20
        elif "nghiêm túc" in user_goal_lower and "nghiêm túc" in cand_goal_lower:
            score += 20
        elif user_goal_lower == "không rõ" or cand_goal_lower == "không rõ":
            score += 5
    
    # Smoking compatibility (-15 points if conflict)
    user_no_smoking = user_profile.get("no_smoking", False)
    cand_smoking = candidate.get("smoking", False)
    if user_no_smoking and cand_smoking:
        score -= 15
    
    # Interest overlap (+10 points max, 2 points per shared interest)
    user_interests = user_profile.get("interests", [])
    if isinstance(user_interests, str):
        user_interests = [i.strip() for i in user_interests.split(",")]
    user_interests = set(i.lower().strip() for i in user_interests if i)
    
    cand_interests = candidate.get("interests", [])
    if isinstance(cand_interests, str):
        cand_interests = [i.strip() for i in cand_interests.split(",")]
    cand_interests = set(i.lower().strip() for i in cand_interests if i)
    
    overlap = user_interests & cand_interests
    score += min(len(overlap) * 2, 10)
    
    # Long distance compatibility (-10 points if conflict)
    user_no_long_distance = user_profile.get("no_long_distance", False)
    cand_long_distance_ok = candidate.get("long_distance_ok", True)
    if user_no_long_distance and not cand_long_distance_ok:
        score -= 10
    
    # Clamp score to 0-100
    return max(0, min(100, score))


# =============================================================================
# TOOL 4: rank_matches
# =============================================================================

def rank_matches(scored_candidates: List[Dict]) -> List[Dict]:
    """
    Xếp hạng các ứng viên theo điểm tương thích.
    
    Args:
        scored_candidates (List[Dict]): Danh sách ứng viên đã chấm điểm
                                       Format: [{"candidate": {...}, "score": 85}, ...]
    
    Returns:
        List[Dict]: Danh sách đã sắp xếp theo điểm giảm dần
    """
    # Sort by score descending
    sorted_matches = sorted(
        scored_candidates,
        key=lambda x: x.get("score", 0),
        reverse=True
    )
    
    # Add rank
    for i, match in enumerate(sorted_matches):
        match["rank"] = i + 1
    
    return sorted_matches


# =============================================================================
# TOOL 5: detect_red_flags
# =============================================================================

def detect_red_flags(user_profile: Dict, candidate: Dict) -> List[str]:
    """
    Phát hiện các điểm rủi ro (red flags) trong cặp đôi.
    
    Args:
        user_profile (Dict): Hồ sơ người dùng
        candidate (Dict): Hồ sơ ứng viên
    
    Returns:
        List[str]: Danh sách các cảnh báo
    """
    warnings = []
    
    # Goal mismatch
    user_goal = user_profile.get("goal", "")
    cand_goal = candidate.get("relationship_goal", "")
    if user_goal and cand_goal:
        user_goal_lower = user_goal.lower()
        cand_goal_lower = cand_goal.lower()
        
        if "nghiêm túc" in user_goal_lower and "nghiêm túc" not in cand_goal_lower:
            warnings.append(f"Mục tiêu khác nhau: bạn muốn '{user_goal}' nhưng người này muốn '{cand_goal}'")
        if "không ràng buộc" in cand_goal_lower or "không rõ" in cand_goal_lower:
            if "nghiêm túc" in user_goal_lower:
                warnings.append(f"Người này chưa sẵn sàng cho mối quan hệ nghiêm túc")
    
    # Smoking conflict
    user_no_smoking = user_profile.get("no_smoking", False)
    cand_smoking = candidate.get("smoking", False)
    if user_no_smoking and cand_smoking:
        warnings.append("Người này hút thuốc - có thể xung đột với mong muốn của bạn")
    elif not user_no_smoking and cand_smoking:
        warnings.append("Bạn không hút thuốc nhưng người này hút - cần thảo luận thêm")
    
    # Long distance conflict
    user_no_long_distance = user_profile.get("no_long_distance", False)
    cand_long_distance_ok = candidate.get("long_distance_ok", True)
    user_location = user_profile.get("location", "")
    cand_location = candidate.get("location", "")
    
    if user_no_long_distance and not cand_long_distance_ok:
        if user_location and cand_location and user_location != cand_location:
            warnings.append(f"Bạn không muốn yêu xa nhưng người này ở {cand_location}")
    elif user_no_long_distance and user_location != cand_location:
        warnings.append(f"Hai bạn ở khác thành phố - cần cân nhắc về khoảng cách")
    
    # Age gap
    age_diff = abs(user_profile.get("age", 25) - candidate.get("age", 25))
    if age_diff > 8:
        warnings.append(f"Chênh lệch tuổi ({age_diff} năm) - cần thời gian hiểu nhau hơn")
    
    # Check important_criteria (deal breakers)
    important_criteria = candidate.get("important_criteria", [])
    for criteria in important_criteria:
        criteria_lower = criteria.lower()
        if "không hút thuốc" in criteria_lower and cand_smoking:
            warnings.append(f"Người này yêu cầu đối phương không hút thuốc (nhưng bạn có thể không)")
    
    return warnings


# =============================================================================
# TOOL 6: suggest_opening_message
# =============================================================================

def suggest_opening_message(user_profile: Dict, candidate: Dict) -> str:
    """
    Gợi ý tin nhắn mở lời dựa trên điểm chung.
    
    Args:
        user_profile (Dict): Hồ sơ người dùng
        candidate (Dict): Hồ sơ ứng viên
    
    Returns:
        str: Tin nhắn gợi ý
    """
    # Find common interests
    user_interests = user_profile.get("interests", [])
    if isinstance(user_interests, str):
        user_interests = [i.strip() for i in user_interests.split(",")]
    user_interests = set(i.lower().strip() for i in user_interests if i)
    
    cand_interests = candidate.get("interests", [])
    if isinstance(cand_interests, str):
        cand_interests = [i.strip() for i in cand_interests.split(",")]
    cand_interests = set(i.lower().strip() for i in cand_interests if i)
    
    common = user_interests & cand_interests
    
    # Find personality compatibility
    user_personality = user_profile.get("personality", "").lower()
    cand_personality = candidate.get("personality", "")
    if isinstance(cand_personality, list):
        cand_personality = " ".join(cand_personality)
    cand_personality = cand_personality.lower()
    
    messages = []
    cand_name = candidate.get("name", "bạn")
    
    # Interest-based message
    if common:
        interest = list(common)[0].title()
        templates = [
            f"Mình thấy bạn cũng thích {interest}! Bạn hay {interest} ở đâu?",
            f"Chào {cand_name}! Mình thấy chúng ta cùng thích {interest}, hay lắm!",
            f"Hi! Mình thấy profile của bạn thú vị lắm, đặc biệt là {interest}. Bạn có thể chia sẻ thêm không?"
        ]
        messages.append(templates[len(common) % len(templates)])
    
    # Personality-based message
    if any(trait in cand_personality for trait in ["hướng nội", "trầm tính", "điềm đạm"]):
        messages.append(f"Mình thấy bạn là người {cand_personality.split(',')[0] if ',' in cand_personality else cand_personality}. Mình cũng thế!")
    
    if any(trait in cand_personality for trait in ["hướng ngoại", "năng động", "quảng giao"]):
        messages.append(f"Mình thấy bạn rất năng động! Bạn thường làm gì để tiếp thêm năng lượng?")
    
    # Location-based message
    user_location = user_profile.get("location", "")
    cand_location = candidate.get("location", "")
    if user_location and cand_location:
        if user_location.lower() in cand_location.lower() or cand_location.lower() in user_location.lower():
            messages.append(f"Mình ở {user_location} như bạn luôn! Bạn có quán yêu thích nào ở đây không?")
    
    # Bio-based message
    bio = candidate.get("bio", "")
    if bio:
        if "cà phê" in bio.lower():
            messages.append("Mình thấy bạn cũng thích cà phê như mình! Quán nào bạn hay đến?")
        elif "đọc sách" in bio.lower():
            messages.append("Mình thấy bạn thích đọc sách! Bạn đang đọc cuốn gì thú vị không?")
    
    # Return best message
    if messages:
        return messages[0]
    else:
        return f"Chào {cand_name}! Mình thấy profile của bạn rất thú vị. Bạn có thể chia sẻ thêm về mình không?"


# =============================================================================
# TOOL 7: suggest_date_ideas
# =============================================================================

def suggest_date_ideas(user_profile: Dict, candidate: Dict, budget: str = "Trung bình", location: str = "") -> List[Dict]:
    """
    Gợi ý ý tưởng buổi hẹn hò đầu tiên.
    
    Args:
        user_profile (Dict): Hồ sơ người dùng
        candidate (Dict): Hồ sơ ứng viên
        budget (str): Ngân sách ("Tiết kiệm", "Trung bình", "Cao cấp")
        location (str): Địa điểm ưu tiên
    
    Returns:
        List[Dict]: Danh sách các ý tưởng date
    """
    ideas = []
    
    # Use candidate's location if not specified
    if not location:
        location = candidate.get("location", "Hà Nội")
    
    # Get interests for personalization
    user_interests = user_profile.get("interests", [])
    if isinstance(user_interests, str):
        user_interests = [i.strip() for i in user_interests.split(",")]
    user_interests = [i.lower() for i in user_interests]
    
    cand_interests = candidate.get("interests", [])
    if isinstance(cand_interests, str):
        cand_interests = [i.strip() for i in cand_interests.split(",")]
    cand_interests = [i.lower() for i in cand_interests]
    
    all_interests = set(user_interests + cand_interests)
    
    # Interest-based suggestions
    if any(i in all_interests for i in ["cà phê", "cafe", "coffee"]):
        ideas.append({
            "name": "Cà phê tại quán yên tĩnh",
            "description": "Gặp nhau tại một quán cà phê có không gian thoải mái để trò chuyện",
            "location": location,
            "estimated_cost": "50,000 - 150,000 VND",
            "suitable_for": ["Hướng nội", "Thích trò chuyện sâu"]
        })
    
    if any(i in all_interests for i in ["du lịch", "khám phá", "phượt", "travel"]):
        ideas.append({
            "name": "Khám phá địa điểm mới",
            "description": "Đi bộ khám phá các địa điểm nổi tiếng hoặc ẩn danh trong thành phố",
            "location": location,
            "estimated_cost": "100,000 - 300,000 VND",
            "suitable_for": ["Hướng ngoại", "Thích mạo hiểm nhẹ"]
        })
    
    if any(i in all_interests for i in ["phim", "xem phim", "movie"]):
        ideas.append({
            "name": "Xem phim tại rạp",
            "description": "Chọn một bộ phim cả hai cùng thích và thưởng thức",
            "location": location,
            "estimated_cost": "150,000 - 350,000 VND/người",
            "suitable_for": ["Mọi người", "Lần đầu gặp"]
        })
    
    if any(i in all_interests for i in ["ẩm thực", "nấu ăn", "food", "ăn uống", "ẩm thực đường phố"]):
        ideas.append({
            "name": "Thử nhà hàng mới",
            "description": "Cùng nhau khám phá ẩm thực tại một nhà hàng mới mẻ",
            "location": location,
            "estimated_cost": "200,000 - 800,000 VND",
            "suitable_for": ["Mọi người", "Thích trải nghiệm"]
        })
    
    if any(i in all_interests for i in ["nhạc", "nghe nhạc", "music", "acoustic"]):
        ideas.append({
            "name": "Nghe nhạc live",
            "description": "Tìm quán có acoustic live hoặc sự kiện âm nhạc",
            "location": location,
            "estimated_cost": "100,000 - 300,000 VND",
            "suitable_for": ["Thích âm nhạc", "Không ép buộc nói chuyện liên tục"]
        })
    
    if any(i in all_interests for i in ["leo núi", "chạy bộ", "yoga", "vận động"]):
        ideas.append({
            "name": "Hoạt động ngoài trời",
            "description": "Cùng nhau đi dạo, chạy bộ hoặc yoga ở công viên",
            "location": location,
            "estimated_cost": "0 - 50,000 VND",
            "suitable_for": ["Thích vận động", "Sức khỏe"]
        })
    
    # Default suggestions
    if len(ideas) < 3:
        ideas.extend([
            {
                "name": "Đi dạo công viên",
                "description": "Câu chuyện đơn giản nhưng hiệu quả để làm quen",
                "location": location,
                "estimated_cost": "0 VND",
                "suitable_for": ["Mọi người", "Tiết kiệm"]
            },
            {
                "name": "Ice cream date",
                "description": "Một buổi chiều nhẹ nhàng thưởng thức kem cùng nhau",
                "location": location,
                "estimated_cost": "50,000 - 150,000 VND",
                "suitable_for": ["Mùa hè", "Thoải mái"]
            }
        ])
    
    return ideas[:5]  # Return top 5 suggestions


# =============================================================================
# AVAILABLE TOOLS REGISTRY
# =============================================================================

AVAILABLE_TOOLS = {
    "search_profiles": search_profiles,
    "filter_candidates": filter_candidates,
    "calculate_compatibility_score": calculate_compatibility_score,
    "rank_matches": rank_matches,
    "detect_red_flags": detect_red_flags,
    "suggest_opening_message": suggest_opening_message,
    "suggest_date_ideas": suggest_date_ideas,
}


# =============================================================================
# TOOL SCHEMAS (for LLM context)
# =============================================================================

TOOL_SCHEMAS = {
    "search_profiles": {
        "name": "search_profiles",
        "description": "Tìm hồ sơ ứng viên theo tiêu chí tìm kiếm",
        "parameters": {
            "criteria": "str - Tiêu chí tìm kiếm (VD: 'hướng nội, thích đọc sách, Hà Nội')"
        }
    },
    "filter_candidates": {
        "name": "filter_candidates",
        "description": "Lọc ứng viên theo điều kiện cứng",
        "parameters": {
            "user_profile": "dict - Hồ sơ người dùng",
            "candidates": "list - Danh sách ứng viên"
        }
    },
    "calculate_compatibility_score": {
        "name": "calculate_compatibility_score",
        "description": "Tính điểm tương thích (0-100)",
        "parameters": {
            "user_profile": "dict - Hồ sơ người dùng",
            "candidate": "dict - Hồ sơ ứng viên"
        }
    },
    "rank_matches": {
        "name": "rank_matches",
        "description": "Xếp hạng ứng viên theo điểm",
        "parameters": {
            "scored_candidates": "list - Danh sách đã chấm điểm"
        }
    },
    "detect_red_flags": {
        "name": "detect_red_flags",
        "description": "Phát hiện điểm rủi ro",
        "parameters": {
            "user_profile": "dict - Hồ sơ người dùng",
            "candidate": "dict - Hồ sơ ứng viên"
        }
    },
    "suggest_opening_message": {
        "name": "suggest_opening_message",
        "description": "Gợi ý tin nhắn mở lời",
        "parameters": {
            "user_profile": "dict - Hồ sơ người dùng",
            "candidate": "dict - Hồ sơ ứng viên"
        }
    },
    "suggest_date_ideas": {
        "name": "suggest_date_ideas",
        "description": "Gợi ý ý tưởng date",
        "parameters": {
            "user_profile": "dict - Hồ sơ người dùng",
            "candidate": "dict - Hồ sơ ứng viên",
            "budget": "str - Ngân sách ('Tiết kiệm', 'Trung bình', 'Cao cấp')",
            "location": "str - Địa điểm"
        }
    }
}
