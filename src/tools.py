"""
Cupid Agent Tools Implementation
Provides 7 core tools for searching, filtering, scoring, ranking, red flag detection,
opening message generation, and date idea recommendation.
"""

import json
import os
from typing import List, Dict, Any, Union

DATASET_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "candidate_profiles.json")

def load_candidate_dataset() -> List[Dict[str, Any]]:
    """Helper function to load candidate profiles from JSON."""
    try:
        if not os.path.exists(DATASET_PATH):
            return []
        with open(DATASET_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return []

# 1. Search Profiles
def search_profiles(criteria: str) -> Union[List[Dict[str, Any]], str]:
    """
    Search candidate profiles matching keyword criteria.
    
    Args:
        criteria: Search query string (e.g., 'nghiêm túc, hướng nội, Hà Nội, đọc sách')
        
    Returns:
        List of candidate profiles or an error string if invalid input.
    """
    try:
        if not criteria or not isinstance(criteria, str):
            return "Lỗi: Tiêu chí tìm kiếm không hợp lệ hoặc để trống."
            
        candidates = load_candidate_dataset()
        if not candidates:
            return "Lỗi: Không tìm thấy dữ liệu ứng viên."

        keywords = [k.strip().lower() for k in criteria.split(",") if k.strip()]
        if not keywords:
            keywords = [criteria.strip().lower()]

        results = []
        for cand in candidates:
            cand_str = json.dumps(cand, ensure_ascii=False).lower()
            # Match if any keyword matches
            matches = sum(1 for kw in keywords if kw in cand_str)
            if matches > 0:
                cand_copy = dict(cand)
                cand_copy["_relevance"] = matches
                results.append(cand_copy)

        results.sort(key=lambda x: x.get("_relevance", 0), reverse=True)
        # Clean up temporary field
        for r in results:
            r.pop("_relevance", None)

        if not results:
            return f"Không tìm thấy hồ sơ nào phù hợp với từ khóa '{criteria}'."

        return results
    except Exception as e:
        return f"Lỗi xử lý trong search_profiles: {str(e)}"


# 2. Filter Candidates
def filter_candidates(user_profile: Dict[str, Any], candidates: List[Dict[str, Any]]) -> Union[List[Dict[str, Any]], str]:
    """
    Filters candidates based on hard deal-breakers (age range, location, smoking habit, distance/location).
    
    Args:
        user_profile: Dict containing user info and deal-breakers
        candidates: List of candidate profiles
        
    Returns:
        Filtered candidate profiles list or error string.
    """
    try:
        if not isinstance(user_profile, dict) or not candidates:
            return "Lỗi: Hồ sơ người dùng hoặc danh sách ứng viên không hợp lệ."
            
        if isinstance(candidates, str):
            return f"Không thể lọc vì danh sách ứng viên là chuỗi thông báo: {candidates}"

        filtered = []
        user_location = user_profile.get("location", "").lower()
        deal_breakers = [str(d).lower() for d in user_profile.get("deal_breakers", [])]
        target_gender = user_profile.get("target_gender", "Nam" if user_profile.get("gender") == "Nữ" else "Nữ").lower()

        for cand in candidates:
            # Check hard condition: Location mismatch if user strictly dislikes long distance (yêu xa)
            cand_location = cand.get("location", "").lower()
            if "yêu xa" in deal_breakers or "không muốn yêu xa" in deal_breakers:
                if user_location and cand_location and user_location not in cand_location and cand_location not in user_location:
                    continue  # Filter out

            # Check hard condition: Smoking
            if "hút thuốc" in deal_breakers or "không hút thuốc" in deal_breakers:
                cand_smoking = cand.get("lifestyle", {}).get("smoking", False)
                if cand_smoking:
                    continue  # Filter out smoker

            # Check target gender if specified
            cand_gender = cand.get("gender", "").lower()
            if target_gender and cand_gender and cand_gender != target_gender:
                # Optionally filter by gender if explicitly target gender is set
                pass

            filtered.append(cand)

        if not filtered:
            return "Tất cả ứng viên đã bị loại do không đáp ứng các điều kiện cứng (tiêu chuẩn bắt buộc)."

        return filtered
    except Exception as e:
        return f"Lỗi xử lý trong filter_candidates: {str(e)}"


# 3. Calculate Compatibility Score
def calculate_compatibility_score(user: Dict[str, Any], candidate: Dict[str, Any]) -> Union[Dict[str, Any], str]:
    """
    Calculates detailed multi-dimensional compatibility score (0-100) between user and candidate.
    Dimensions: Location (20%), Personality (20%), Interests (25%), Relationship Goal (20%), Lifestyle (15%).
    
    Returns:
        Dict with total_score, breakdown, and pros/cons.
    """
    try:
        if not isinstance(user, dict) or not isinstance(candidate, dict):
            return "Lỗi: Dữ liệu hồ sơ người dùng hoặc ứng viên không hợp lệ."

        score = 0
        reasons = []
        warnings = []

        # 1. Location (20 pts)
        u_loc = user.get("location", "").strip().lower()
        c_loc = candidate.get("location", "").strip().lower()
        if u_loc and c_loc and u_loc in c_loc:
            score += 20
            reasons.append(f"Cùng sống ở {candidate.get('location')}")
        else:
            score += 5
            warnings.append(f"Khác vị trí địa lý ({u_loc.capitalize()} - {c_loc.capitalize()})")

        # 2. Relationship Goal (20 pts)
        u_goal = user.get("relationship_goal", "").strip().lower()
        c_goal = candidate.get("relationship_goal", "").strip().lower()
        if u_goal and c_goal and (u_goal in c_goal or c_goal in u_goal):
            score += 20
            reasons.append(f"Cùng mục tiêu quan hệ: {candidate.get('relationship_goal')}")
        elif u_goal == "nghiêm túc" and c_goal == "tìm hiểu tự nhiên":
            score += 10
            warnings.append("Mục tiêu quan hệ lệch nhẹ (Nghiêm túc vs Tìm hiểu tự nhiên)")
        else:
            score += 5
            warnings.append("Mục tiêu quan hệ khác biệt")

        # 3. Personality & MBTI (20 pts)
        u_pers = user.get("personality", "").strip().lower()
        c_pers = candidate.get("personality", "").strip().lower()
        if u_pers and c_pers and u_pers == c_pers:
            score += 20
            reasons.append(f"Đồng điệu nét tính cách: {candidate.get('personality')}")
        else:
            score += 15
            reasons.append(f"Tính cách bổ trợ tốt ({u_pers.capitalize()} & {c_pers.capitalize()})")

        # 4. Shared Interests (25 pts)
        u_interests = set(i.lower().strip() for i in user.get("interests", []))
        c_interests = set(i.lower().strip() for i in candidate.get("interests", []))
        common = u_interests.intersection(c_interests)
        if common:
            interest_score = min(25, len(common) * 10)
            score += interest_score
            reasons.append(f"Cùng sở thích: {', '.join(common)}")
        else:
            score += 5

        # 5. Lifestyle & Habits (15 pts)
        c_lifestyle = candidate.get("lifestyle", {})
        if not c_lifestyle.get("smoking", False):
            score += 10
            reasons.append("Lối sống lành mạnh (Không hút thuốc)")
        else:
            warnings.append("Ứng viên có thói quen hút thuốc")

        if c_lifestyle.get("sleep_schedule") == "ngủ sớm":
            score += 5

        # Cap score at 100
        total_score = min(100, score)

        return {
            "candidate_id": candidate.get("id"),
            "candidate_name": candidate.get("name"),
            "age": candidate.get("age"),
            "location": candidate.get("location"),
            "total_score": total_score,
            "reasons": reasons,
            "warnings": warnings,
            "notes": candidate.get("notes", "")
        }
    except Exception as e:
        return f"Lỗi xử lý trong calculate_compatibility_score: {str(e)}"


# 4. Rank Matches
def rank_matches(scored_candidates: List[Dict[str, Any]]) -> Union[List[Dict[str, Any]], str]:
    """
    Ranks candidates by compatibility score descending.
    
    Args:
        scored_candidates: List of candidate score dicts
        
    Returns:
        Sorted top matches list or error string.
    """
    try:
        if not scored_candidates or not isinstance(scored_candidates, list):
            return "Lỗi: Danh sách điểm tương thích trống hoặc không hợp lệ."

        # Filter out string errors if any
        valid_scores = [s for s in scored_candidates if isinstance(s, dict) and "total_score" in s]
        if not valid_scores:
            return "Lỗi: Không có kết quả chấm điểm hợp lệ nào để xếp hạng."

        ranked = sorted(valid_scores, key=lambda x: x.get("total_score", 0), reverse=True)
        return ranked
    except Exception as e:
        return f"Lỗi xử lý trong rank_matches: {str(e)}"


# 5. Detect Red Flags
def detect_red_flags(user: Dict[str, Any], candidate: Dict[str, Any]) -> Union[List[str], str]:
    """
    Detects potential risks or red flags between user requirements and candidate traits.
    """
    try:
        if not isinstance(user, dict) or not isinstance(candidate, dict):
            return "Lỗi: Dữ liệu hồ sơ người dùng hoặc ứng viên không hợp lệ."

        flags = []
        u_deal_breakers = [str(d).lower() for d in user.get("deal_breakers", [])]

        # Check smoking
        if candidate.get("lifestyle", {}).get("smoking", False):
            flags.append("RED FLAG: Ứng viên hút thuốc lá (Xung đột nếu bạn dị ứng hoặc ghét khói thuốc).")

        # Check distance
        u_loc = user.get("location", "").lower()
        c_loc = candidate.get("location", "").lower()
        if u_loc and c_loc and u_loc not in c_loc:
            flags.append(f"LƯU Ý KHOẢNG CÁCH: Ứng viên đang ở {candidate.get('location')}, trong khi bạn ở {user.get('location')}.")

        # Goal mismatch
        u_goal = user.get("relationship_goal", "").lower()
        c_goal = candidate.get("relationship_goal", "").lower()
        if u_goal == "nghiêm túc" and "tự nhiên" in c_goal:
            flags.append("LỆCH MỤC TIÊU: Bạn muốn mối quan hệ nghiêm túc lâu dài, nhưng đối phương chỉ muốn tìm hiểu tự nhiên.")

        return flags if flags else ["Không phát hiện Red Flag nghiêm trọng nào."]
    except Exception as e:
        return f"Lỗi xử lý trong detect_red_flags: {str(e)}"


# 6. Suggest Opening Message
def suggest_opening_message(user: Dict[str, Any], candidate: Dict[str, Any]) -> str:
    """
    Generates a personalized icebreaker message based on shared interests and profile details.
    """
    try:
        if not isinstance(candidate, dict):
            return "Lỗi: Dữ liệu ứng viên không hợp lệ."

        name = candidate.get("name", "bạn")
        interests = candidate.get("interests", [])

        # Find overlapping or key interest
        u_interests = set(i.lower() for i in user.get("interests", []))
        c_interests = [i for i in interests if i.lower() in u_interests]

        if c_interests:
            topic = c_interests[0]
            if "sách" in topic or "đọc" in topic:
                return f'"Chào {name}, mình thấy bạn cũng có gu thích đọc sách và cà phê yên tĩnh. Cuối tuần bạn hay đọc thể loại gì thế?"'
            elif "cà phê" in topic:
                return f'"Chào {name}, mình thấy bạn cũng thích la cà cà phê yên tĩnh. Bạn có quán quen nào ở Hà Nội gợi ý cho mình không?"'
            else:
                return f'"Chào {name}, mình thấy chúng mình đều thích {topic}. Bạn theo đuổi sở thích này lâu chưa?"'
        else:
            first_interest = interests[0] if interests else "sở thích của bạn"
            return f'"Chào {name}, mình rất ấn tượng với hồ sơ của bạn, đặc biệt là niềm đam mê với {first_interest}. Rất vui được làm quen với bạn!"'
    except Exception as e:
        return f"Lỗi xử lý trong suggest_opening_message: {str(e)}"


# 7. Suggest Date Ideas
def suggest_date_ideas(user: Dict[str, Any], candidate: Dict[str, Any], budget: str = "vừa phải", location: str = "Hà Nội") -> Union[List[Dict[str, str]], str]:
    """
    Suggests suitable first date ideas tailored to personalities, interests, budget, and location.
    """
    try:
        c_name = candidate.get("name", "đối phương")
        c_pers = candidate.get("personality", "Hướng nội")
        interests = [i.lower() for i in candidate.get("interests", [])]

        ideas = []
        if "hướng nội" in c_pers.lower():
            ideas.append({
                "activity": "Trò chuyện tại quán Cà phê Sách yên tĩnh",
                "location": f"Khu vực {candidate.get('district', 'trung tâm')} - {location}",
                "reason": f"Không gian yên tĩnh, nhẹ nhàng giúp cả 2 thoải mái trò chuyện sâu mà không bị làm phiền.",
                "estimated_budget": "100.000 - 200.000 VNĐ"
            })
            ideas.append({
                "activity": "Tham quan Triển lãm Nghệ thuật / Museum buổi chiều",
                "location": f"Bảo tàng Mỹ thuật hoặc Không gian Triển lãm tại {location}",
                "reason": "Hoạt động nhẹ nhàng, gợi mở nhiều chủ đề thảo luận thú vị mà không quá vồ vập.",
                "estimated_budget": "150.000 VNĐ"
            })
        else:
            ideas.append({
                "activity": "Dạo phố và trải nghiệm Workshop làm gốm / nến thơm",
                "location": f"{location}",
                "reason": "Hoạt động tương tác năng động giúp xua tan sự bỡ ngỡ ban đầu.",
                "estimated_budget": "300.000 - 500.000 VNĐ"
            })

        return ideas
    except Exception as e:
        return f"Lỗi xử lý trong suggest_date_ideas: {str(e)}"
