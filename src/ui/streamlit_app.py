"""
Cupid Agent - Web UI (Streamlit) - Enhanced Chat Interface
Role 4: UI Mock để Role 2/3 cắm tools và prompts vào sau
"""

import streamlit as st
import json
import os
import sys
import traceback

# Path resolution
current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)  # src/ui
src_dir = os.path.dirname(current_dir)  # src
root_dir = os.path.dirname(src_dir)  # project root

# Debug logging setup
DEBUG_LOG_PATH = os.path.join(root_dir, "debug-0a4651.log")

def dbg_log(hypothesis_id, message, data=None):
    """Append NDJSON log to debug log file"""
    import time
    payload = {
        "sessionId": "0a4651",
        "runId": "initial",
        "hypothesisId": hypothesis_id,
        "location": "streamlit_app.py",
        "message": message,
        "data": data or {},
        "timestamp": int(time.time() * 1000)
    }
    try:
        with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception as e:
        sys.stderr.write(f"LOG_FAIL: {e}\n")

dbg_log("H1", "Path resolution", {
    "current_file": current_file,
    "current_dir": current_dir,
    "src_dir": src_dir,
    "root_dir": root_dir,
    "src_dir_exists": os.path.exists(src_dir),
    "tools_py_exists": os.path.exists(os.path.join(src_dir, "tools.py")),
    "prompts_py_exists": os.path.exists(os.path.join(src_dir, "prompts.py")),
    "candidate_profiles_exists": os.path.exists(os.path.join(root_dir, "config", "candidate_profiles.json")),
    "cwd": os.getcwd(),
    "sys_path_before": list(sys.path)[:5]
})

# Add src to path
sys.path.insert(0, src_dir)
sys.path.insert(0, root_dir)

dbg_log("H1", "sys.path after insert", {"sys_path": sys.path[:8]})

# Import tools
import tools as tools_module
dbg_log("H4", "tools import START", {"tools_file": tools_module.__file__})
dbg_log("H4", "tools module contents", {"has_load_candidates": "load_candidates" in dir(tools_module)})

try:
    from tools import (
        AVAILABLE_TOOLS,
        MOCK_CANDIDATES,
        load_candidates,
        search_profiles,
        filter_candidates,
        calculate_compatibility_score,
        rank_matches,
        detect_red_flags,
        suggest_opening_message,
        suggest_date_ideas,
        parse_user_profile,
    )
    dbg_log("H4", "Tools imported successfully", {"tools_count": len(AVAILABLE_TOOLS)})
    
    # Import from fixed app.py for routing logic
    import sys
    sys.path.insert(0, src_dir)
    from app import route_query, validate_input, is_safety_violation, is_simple_query
    HAS_ROUTING = True
except Exception as e:
    dbg_log("H4", "Import FAILED", {
        "error_type": type(e).__name__,
        "error_msg": str(e),
        "traceback": traceback.format_exc()
    })
    AVAILABLE_TOOLS = {}
    HAS_ROUTING = False

# Page config
st.set_page_config(
    page_title="Cupid Agent - Trợ lý hẹn hò",
    page_icon="💕",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 0;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .profile-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 16px;
        color: white;
        margin: 0.5rem 0;
    }
    .match-score {
        font-size: 2rem;
        font-weight: bold;
        color: #4ECDC4;
    }
    .stButton > button {
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 25px;
        font-weight: bold;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 0.75rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
    }
    /* Chat message styles */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 16px 16px 4px 16px;
        margin: 0.5rem 0;
    }
    .bot-message {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 16px 16px 16px 4px;
        margin: 0.5rem 0;
    }
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


def load_candidates_data():
    """Load candidates from JSON file"""
    try:
        candidates = load_candidates()
        dbg_log("H2", "load_candidates() returned", {
            "count": len(candidates) if candidates else 0,
            "type": type(candidates).__name__
        })
        return candidates if candidates else MOCK_CANDIDATES
    except Exception as e:
        dbg_log("H2", "load_candidates() FAILED", {
            "error_type": type(e).__name__,
            "error_msg": str(e),
            "traceback": traceback.format_exc()
        })
        return MOCK_CANDIDATES


def parse_json_safe(json_str, fallback=None):
    """Parse JSON safely, return fallback on error"""
    try:
        result = json.loads(json_str)
        return result
    except (json.JSONDecodeError, TypeError):
        return fallback if fallback is not None else {}


def process_user_message(user_input: str, user_profile: dict, candidates: list, provider=None) -> tuple:
    """
    Process user message using fixed routing logic from app.py
    """
    # Use routing from app.py if available
    if HAS_ROUTING:
        try:
            response = route_query(user_input, provider)
            
            # Try to extract updated profile from response
            parsed = parse_user_profile(user_input)
            new_profile = parse_json_safe(parsed, None)
            if new_profile and isinstance(new_profile, dict) and not new_profile.get("error"):
                return (response, new_profile, None)
            return (response, user_profile, None)
        except Exception as e:
            dbg_log("H4", "route_query failed", {"error": str(e)})
    
    # Fallback to inline processing
    user_input_lower = user_input.lower()
    
    # Parse user profile from input
    parsed = parse_user_profile(user_input)
    profile = parse_json_safe(parsed, {})
    
    if profile and not profile.get("error"):
        user_profile = profile
    
    if not user_profile or profile.get("error"):
        return (
            "Xin chào! 💕 Tôi là Cupid - trợ lý hẹn hò thông minh.\n\n"
            "Hãy giới thiệu về bản thân bạn nhé - ví dụ:\n"
            "\"Tôi là nam, 25 tuổi, sống ở Hà Nội, thích đọc sách và du lịch, muốn tìm quan hệ nghiêm túc\"",
            {},
            None
        )
    
    # Intent detection
    intents = {
        "match": ["tìm", "tìm kiếm", "match", "phù hợp", "ghép đôi", "ai phù hợp", "gợi ý"],
        "list": ["danh sách", "list", "tất cả", "xem hết", "liệt kê"],
        "red_flags": ["red flag", "cảnh báo", "rủi ro", "lưu ý", "nguy hiểm", "phân tích"],
        "date_ideas": ["hẹn", "date", "đi chơi", "gặp mặt", "ý tưởng", "địa điểm"],
        "help": ["help", "hướng dẫn", "giúp", "làm gì", "có thể"],
    }
    
    detected_intent = None
    for intent_name, keywords in intents.items():
        if any(kw in user_input_lower for kw in keywords):
            detected_intent = intent_name
            break
    
    # Process based on intent
    user_profile_json = json.dumps(user_profile, ensure_ascii=False)
    
    # Intent: Find matches
    if detected_intent == "match" or detected_intent is None:
        # Search profiles
        criteria = f"{user_profile.get('location', '')}, {user_profile.get('relationship_goal', '')}, {', '.join(user_profile.get('hobbies', []))}"
        search_results = search_profiles(criteria)
        search_candidates = parse_json_safe(search_results, candidates)
        if not isinstance(search_candidates, list):
            search_candidates = candidates
        
        # Filter candidates
        filtered = filter_candidates(user_profile_json, json.dumps(search_candidates, ensure_ascii=False))
        filtered_list = parse_json_safe(filtered, [])
        if isinstance(filtered_list, dict) and filtered_list.get("error"):
            return (f"😔 {filtered_list.get('message', 'Không tìm thấy ai phù hợp')}", user_profile, None)
        
        if not filtered_list:
            return ("😔 Không tìm thấy ứng viên nào phù hợp với tiêu chí của bạn. Thử thay đổi một số điều kiện nhé!", user_profile, None)
        
        # Score candidates
        scored = []
        for cand in filtered_list[:10]:
            score_result = calculate_compatibility_score(user_profile_json, json.dumps(cand, ensure_ascii=False))
            scored_cand = parse_json_safe(score_result, {})
            if isinstance(scored_cand, dict) and "compatibility_score" in scored_cand:
                scored.append(scored_cand)
        
        # Rank
        if scored:
            ranked = rank_matches(json.dumps(scored, ensure_ascii=False))
            top_matches = parse_json_safe(ranked, scored[:3])
        else:
            top_matches = filtered_list[:3]
        
        # Build response
        response = f"🎉 Tôi đã tìm thấy {len(top_matches)} người phù hợp nhất với bạn!\n\n"
        
        suggestions = []
        for i, match in enumerate(top_matches[:5], 1):
            name = match.get('name', 'N/A')
            score = match.get('compatibility_score', 'N/A')
            reason = match.get('compatibility_reason', match.get('notes', 'Phù hợp'))
            age = match.get('age', 'N/A')
            location = match.get('location', 'N/A')
            hobbies = match.get('hobbies', [])
            if isinstance(hobbies, list):
                hobbies_str = ', '.join(hobbies[:3])
            else:
                hobbies_str = str(hobbies)
            
            response += f"**🏆 TOP {i}: {name}**, {age} tuổi\n"
            response += f"📍 {location} | 🎯 Điểm: {score}/100\n"
            response += f"💡 {reason}\n"
            response += f"❤️ {hobbies_str}\n\n"
            
            suggestions.append({
                "name": name,
                "age": age,
                "location": location,
                "score": score,
                "hobbies": hobbies,
                "full_profile": match
            })
        
        # Add opening message for top 1
        if top_matches:
            opening = suggest_opening_message(user_profile_json, json.dumps(top_matches[0], ensure_ascii=False))
            response += f"\n💬 **Gợi ý mở lời với {top_matches[0].get('name', 'người này')}:**\n{opening}"
        
        return (response, user_profile, suggestions)
    
    # Intent: List candidates
    elif detected_intent == "list":
        response = "📋 **DANH SÁCH ỨNG VIÊN HIỆN CÓ:**\n\n"
        for i, c in enumerate(candidates[:10], 1):
            name = c.get('name', 'N/A')
            age = c.get('age', 'N/A')
            location = c.get('location', 'N/A')
            goal = c.get('relationship_goal', 'N/A')
            hobbies = c.get('hobbies', [])
            hobbies_str = ', '.join(hobbies[:2]) if isinstance(hobbies, list) else str(hobbies)
            response += f"{i}. **{name}**, {age} tuổi - 📍{location}\n"
            response += f"   🎯 {goal} | ❤️ {hobbies_str}\n\n"
        return (response, user_profile, None)
    
    # Intent: Red flags
    elif detected_intent == "red_flags":
        candidate_name = None
        for c in candidates:
            if c['name'].lower() in user_input_lower:
                candidate_name = c['name']
                break
        
        if not candidate_name:
            return ("Bạn muốn phân tích red flags với ai? Hãy nêu tên người đó nhé!", user_profile, None)
        
        cand = next((c for c in candidates if c['name'] == candidate_name), None)
        if cand:
            red_flags = detect_red_flags(user_profile_json, json.dumps(cand, ensure_ascii=False))
            return (f"🔍 **Phân tích về {cand['name']}:**\n\n{red_flags}", user_profile, None)
        return (f"Không tìm thấy người tên '{candidate_name}'", user_profile, None)
    
    # Intent: Date ideas
    elif detected_intent == "date_ideas":
        candidate_name = None
        for c in candidates:
            if c['name'].lower() in user_input_lower:
                candidate_name = c['name']
                break
        
        if not candidate_name:
            return ("Bạn muốn gợi ý ý tưởng hẹn hò với ai? Hãy nêu tên người đó nhé!", user_profile, None)
        
        cand = next((c for c in candidates if c['name'] == candidate_name), None)
        if cand:
            date_ideas = suggest_date_ideas(user_profile_json, json.dumps(cand, ensure_ascii=False))
            return (date_ideas, user_profile, None)
        return (f"Không tìm thấy người tên '{candidate_name}'", user_profile, None)
    
    # Intent: Help
    elif detected_intent == "help":
        response = """🤖 **Tôi có thể giúp bạn:**

1️⃣ **Tìm người phù hợp** - Nói "tìm người phù hợp với tôi"
2️⃣ **Xem danh sách ứng viên** - Nói "xem danh sách"
3️⃣ **Phân tích red flags** - Nói "phân tích [tên] có gì cần lưu ý"
4️⃣ **Gợi ý hẹn hò** - Nói "gợi ý chỗ đi chơi với [tên]"

Bạn cứ trò chuyện tự nhiên với tôi nhé! 💕"""
        return (response, user_profile, None)
    
    # Default: show profile summary
    else:
        age = user_profile.get('age', 'N/A')
        gender = user_profile.get('gender', 'N/A')
        location = user_profile.get('location', 'N/A')
        hobbies = user_profile.get('hobbies', [])
        goal = user_profile.get('relationship_goal', 'N/A')
        hobbies_str = ', '.join(hobbies) if isinstance(hobbies, list) and hobbies else 'chưa rõ'
        
        response = f"""✨ **Hồ sơ của bạn đã được ghi nhận:**

• Giới tính: {gender}
• Tuổi: {age}
• Địa điểm: {location}
• Sở thích: {hobbies_str}
• Mục tiêu: {goal}

Bạn muốn tôi làm gì tiếp theo? 😊"""
        return (response, user_profile, None)


def render_match_cards(suggestions: list):
    """Render match cards in sidebar or main area"""
    if not suggestions:
        return
    
    for i, sugg in enumerate(suggestions[:3], 1):
        with st.expander(f"🏆 Top {i}: {sugg['name']}, {sugg['age']} tuổi - Score: {sugg['score']}"):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**📍 Địa điểm:** {sugg['location']}")
                hobbies = sugg.get('hobbies', [])
                hobbies_str = ', '.join(hobbies[:4]) if isinstance(hobbies, list) else str(hobbies)
                st.markdown(f"**❤️ Sở thích:** {hobbies_str}")
                
                # Red flags
                if st.session_state.get('user_profile_chat'):
                    user_json = json.dumps(st.session_state.user_profile_chat, ensure_ascii=False)
                    cand_json = json.dumps(sugg['full_profile'], ensure_ascii=False)
                    flags = detect_red_flags(user_json, cand_json)
                    st.markdown(f"\n{flags}")
            
            with col2:
                score_color = "#4ECDC4" if sugg['score'] >= 70 else "#FFB347" if sugg['score'] >= 50 else "#FF6B6B"
                st.markdown(f"""
                <div style="text-align: center; padding: 1rem; background: {score_color}; border-radius: 50%; width: 80px; height: 80px; margin: 0 auto;">
                    <div style="font-size: 1.8rem; font-weight: bold; color: white; line-height: 80px;">{sugg['score']}</div>
                </div>
                """, unsafe_allow_html=True)


def main():
    # Header
    st.markdown('<h1 class="main-header">💕 Cupid Agent</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Trợ lý tìm kiếm và phân tích độ tương thích hẹn hò</p>', unsafe_allow_html=True)
    
    # Load candidates
    candidates = load_candidates_data()
    st.sidebar.success(f"✅ Đã tải {len(candidates)} hồ sơ ứng viên")
    
    # Initialize chat history
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    
    if "user_profile_chat" not in st.session_state:
        st.session_state.user_profile_chat = None
    
    if "last_suggestions" not in st.session_state:
        st.session_state.last_suggestions = None
    
    # Sidebar - Quick actions
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🚀 Thao tác nhanh")
        
        if st.button("📋 Xem tất cả ứng viên", use_container_width=True):
            response, _, _ = process_user_message("xem danh sách", st.session_state.user_profile_chat, candidates)
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
            st.rerun()
        
        if st.button("💕 Tìm người phù hợp", use_container_width=True):
            response, profile, suggestions = process_user_message("tìm người phù hợp", st.session_state.user_profile_chat, candidates)
            if profile:
                st.session_state.user_profile_chat = profile
            st.session_state.last_suggestions = suggestions
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
            st.rerun()
        
        # Show match cards if available
        if st.session_state.last_suggestions:
            st.markdown("---")
            st.markdown("### 🏆 Top Matches")
            render_match_cards(st.session_state.last_suggestions)
        
        # User profile summary
        if st.session_state.user_profile_chat:
            st.markdown("---")
            st.markdown("### 📋 Hồ sơ của bạn")
            profile = st.session_state.user_profile_chat
            st.markdown(f"- **Giới tính:** {profile.get('gender', 'N/A')}")
            st.markdown(f"- **Tuổi:** {profile.get('age', 'N/A')}")
            st.markdown(f"- **Địa điểm:** {profile.get('location', 'N/A')}")
            hobbies = profile.get('hobbies', [])
            st.markdown(f"- **Sở thích:** {', '.join(hobbies[:3]) if hobbies else 'N/A'}")
            st.markdown(f"- **Mục tiêu:** {profile.get('relationship_goal', 'N/A')}")
        
        st.markdown("---")
        if st.button("🗑️ Xóa cuộc trò chuyện", use_container_width=True):
            st.session_state.chat_messages = []
            st.session_state.user_profile_chat = None
            st.session_state.last_suggestions = None
            st.rerun()
    
    # Main chat area
    st.markdown("### 💬 Trò chuyện với Cupid")
    
    # Welcome message if empty
    if not st.session_state.chat_messages:
        welcome = """👋 **Chào mừng bạn đến với Cupid Agent!**

Tôi là trợ lý hẹn hò thông minh. Hãy giới thiệu về bản thân bạn nhé!

**Ví dụ:** *"Tôi là nam, 25 tuổi, sống ở Hà Nội, thích đọc sách và du lịch, muốn tìm quan hệ nghiêm túc"*

Tôi có thể giúp bạn:
- 🔍 Tìm người phù hợp
- 💯 Đánh giá độ tương thích
- 💬 Gợi ý mở lời
- 📅 Lên kế hoạch hẹn hò
- ⚠️ Cảnh báo red flags
"""
        st.session_state.chat_messages.append({"role": "assistant", "content": welcome})
    
    # Display chat messages with proper markdown
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_messages:
            if msg["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.markdown(msg["content"])
            else:
                with st.chat_message("assistant", avatar="💕"):
                    st.markdown(msg["content"])
    
    # Chat input - using Streamlit's native chat_input
    if prompt := st.chat_input("Nhắn tin cho Cupid..."):
        user_msg = prompt
        
        # Add user message
        st.session_state.chat_messages.append({"role": "user", "content": user_msg})
        
        # Process and get response
        with st.spinner("💕 Cupid đang suy nghĩ..."):
            try:
                from providers import get_llm_provider
                provider = get_llm_provider()
                response, profile, suggestions = process_user_message(
                    user_msg, 
                    st.session_state.user_profile_chat, 
                    candidates,
                    provider
                )
            except Exception as e:
                dbg_log("H4", "process_user_message error", {"error": str(e)})
                response = f"Xin lỗi, có lỗi xảy ra: {str(e)}"
                profile = st.session_state.user_profile_chat
                suggestions = None
        
        # Update profile
        if profile:
            st.session_state.user_profile_chat = profile
        
        # Update suggestions
        if suggestions:
            st.session_state.last_suggestions = suggestions
        
        # Add response
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        
        # Rerun to show new messages
        st.rerun()


if __name__ == "__main__":
    main()
