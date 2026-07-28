"""
Cupid Agent - Web UI (Streamlit)
Role 4: UI Mock để Role 2/3 cắm tools và prompts vào sau
"""

import streamlit as st
import json
import os
import sys

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import tools
try:
    from tools import (
        AVAILABLE_TOOLS,
        load_candidates,
        search_profiles,
        filter_candidates,
        calculate_compatibility_score,
        rank_matches,
        detect_red_flags,
        suggest_opening_message,
        suggest_date_ideas,
    )
except ImportError:
    st.error("Không thể import tools. Vui lòng kiểm tra đường dẫn.")
    AVAILABLE_TOOLS = {}

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
</style>
""", unsafe_allow_html=True)


def load_candidates_data():
    """Load candidates from JSON file"""
    try:
        candidates = load_candidates()
        return candidates if candidates else []
    except Exception:
        return []


def generate_mock_response(user_profile: dict, candidates: list) -> dict:
    """Generate response using tools"""
    # Filter candidates using tool
    search_criteria = f"{user_profile.get('location', '')}, {user_profile.get('personality', '')}, {', '.join(user_profile.get('interests', []))}"
    search_results = search_profiles(search_criteria)
    
    # If search returns wrapped results, extract candidates
    if search_results and isinstance(search_results[0], dict) and "candidate" in search_results[0]:
        search_candidates = [r["candidate"] for r in search_results]
    else:
        search_candidates = search_results if search_results else candidates
    
    # Filter candidates
    filtered = filter_candidates(user_profile, search_candidates if search_candidates else candidates)
    
    # Score and rank
    scored = []
    for c in filtered:
        score = calculate_compatibility_score(user_profile, c)
        warnings = detect_red_flags(user_profile, c)
        opening = suggest_opening_message(user_profile, c)
        scored.append({
            "candidate": c,
            "score": score,
            "warnings": warnings,
            "opening_message": opening
        })
    
    ranked = rank_matches(scored)
    top_3 = ranked[:3]
    
    # Generate results with reasons
    results = []
    for match in top_3:
        c = match["candidate"]
        
        # Find common interests
        user_interests = set(i.lower() for i in user_profile.get("interests", []))
        cand_interests = set(i.lower() if isinstance(i, str) else "" for i in c.get("interests", []))
        common = user_interests & cand_interests
        
        reasons = []
        if user_profile.get("location") == c.get("location"):
            reasons.append(f"Cùng sống ở {c.get('location', 'đây')}")
        if user_profile.get("goal") == c.get("relationship_goal"):
            reasons.append(f"Cùng mục tiêu: {c.get('relationship_goal', 'nghiêm túc')}")
        if common:
            reasons.append(f"Cùng thích: {', '.join(list(common)[:3])}")
        if c.get("age") and abs(user_profile.get("age", 25) - c.get("age", 25)) <= 5:
            reasons.append(f"Gần tuổi nhau")
        
        results.append({
            "candidate": c,
            "score": match["score"],
            "reasons": reasons,
            "warnings": match["warnings"],
            "opening_message": match["opening_message"]
        })
    
    return {
        "matches": results,
        "total_candidates": len(candidates),
        "filtered_count": len(filtered)
    }


def render_candidate_card(candidate: dict, score: int, reasons: list, warnings: list, opening: str):
    """Render a candidate card"""
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"### {candidate['name']}, {candidate['age']} tuổi")
            st.markdown(f"📍 {candidate.get('location', 'N/A')} | 👤 {candidate.get('gender', 'N/A')}")
            
            # Personality
            personality = candidate.get('personality', 'N/A')
            if isinstance(personality, list):
                personality = ', '.join(personality)
            st.markdown(f"**Tính cách:** {personality}")
            
            # Interests
            interests = candidate.get('interests', [])
            if isinstance(interests, list):
                interests_str = ", ".join(interests[:4])
            else:
                interests_str = str(interests)
            st.markdown(f"**Sở thích:** {interests_str}")
            
            # Goals
            st.markdown(f"**Mục tiêu:** {candidate.get('relationship_goal', 'N/A')}")
            
            # Bio
            bio = candidate.get('bio', '')
            if bio:
                with st.expander("📖 Xem giới thiệu"):
                    st.write(bio)
            
            # Reasons
            if reasons:
                st.markdown("**Lý do phù hợp:**")
                for reason in reasons:
                    st.markdown(f"- ✅ {reason}")
            
            # Warnings
            for warning in warnings:
                st.warning(f"⚠️ {warning}")
            
            # Opening message
            st.markdown("**Gợi ý mở lời:**")
            st.info(f"💬 {opening}")
            
            # Extra info from new schema
            with st.expander("📋 Thông tin thêm"):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"🚬 Hút thuốc: {'Có' if candidate.get('smoking') else 'Không'}")
                    st.markdown(f"🍺 Uống rượu: {candidate.get('drinking', 'N/A')}")
                    st.markdown(f"💰 Yêu xa: {'Được' if candidate.get('long_distance_ok') else 'Không'}")
                with col_b:
                    important = candidate.get('important_criteria', [])
                    if important:
                        st.markdown("**Tiêu chí quan trọng:**")
                        for c in important:
                            st.markdown(f"- {c}")
                
                notes = candidate.get('notes', '')
                if notes:
                    st.markdown(f"**Ghi chú:** {notes}")
        
        with col2:
            # Score circle
            score_color = "#4ECDC4" if score >= 70 else "#FFB347" if score >= 50 else "#FF6B6B"
            st.markdown(f"""
            <div style="text-align: center; padding: 1.5rem; background: {score_color}; border-radius: 50%; width: 120px; height: 120px; margin: 0 auto;">
                <div style="font-size: 2.5rem; font-weight: bold; color: white; line-height: 120px;">{score}</div>
            </div>
            <p style="text-align: center; font-weight: bold; margin-top: 0.5rem;">/100</p>
            """, unsafe_allow_html=True)
            
            # Quick match indicators
            st.markdown("---")
            st.markdown("### Đánh giá nhanh")
            
            # Smoking
            if not candidate.get('smoking', False):
                st.markdown("✅ Không hút thuốc")
            else:
                st.markdown("⚠️ Có hút thuốc")
            
            # Location
            if candidate.get('long_distance_ok', False):
                st.markdown("✅ Chấp nhận yêu xa")
            else:
                st.markdown("⚠️ Không yêu xa")


def main():
    # Header
    st.markdown('<h1 class="main-header">💕 Cupid Agent</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Trợ lý tìm kiếm và phân tích độ tương thích hẹn hò</p>', unsafe_allow_html=True)
    
    # Load candidates
    candidates = load_candidates_data()
    
    if not candidates:
        st.error("Không thể tải dữ liệu ứng viên. Vui lòng kiểm tra file config/candidate_profiles.json")
        return
    
    st.sidebar.success(f"✅ Da tai {len(candidates)} ho so ung vien")
    
    # Sidebar - User Profile Input
    st.sidebar.header("📝 Ho so cua ban")
    
    with st.sidebar.form("user_profile_form"):
        name = st.text_input("Ten cua ban", placeholder="VD: Minh")
        age = st.slider("Tuoi", 18, 60, 25)
        gender = st.selectbox("Gioi tinh", ["Nam", "Nu"])
        
        # Location options from data
        locations = list(set(c.get("location", "Hà Nội") for c in candidates))
        locations = sorted([loc for loc in locations if loc]) + ["Khác"]
        location = st.selectbox("Dia diem", locations)
        
        personality = st.text_area("Mo ta tinh cach", placeholder="VD: huong noi, thich doc sach, ca phe yen tinh")
        interests_input = st.text_input("So thich", placeholder="VD: Đọc sách, Du lịch, Âm nhạc (phan cach bang dau phay)")
        goal = st.selectbox("Muc tieu quan he", ["Nghiêm túc", "Tìm bạn", "Không rõ", "Khác"])
        no_smoking = st.checkbox("Khong muon nguoi hut thuoc")
        no_long_distance = st.checkbox("Khong muon yeu xa")
        
        submitted = st.form_submit_button("🔍 Tim kiem", use_container_width=True)
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["💕 Ket qua Match", "👥 Danh sach ung vien", "ℹ️ Huong dan su dung"])
    
    with tab1:
        if submitted and name:
            # Build user profile
            user_profile = {
                "name": name,
                "age": age,
                "gender": gender,
                "location": location if location != "Khác" else "",
                "personality": personality,
                "interests": [i.strip() for i in interests_input.split(",")] if interests_input else [],
                "goal": goal,
                "no_smoking": no_smoking,
                "no_long_distance": no_long_distance
            }
            
            # Generate response using tools
            with st.spinner("🔄 Dang phan tich..."):
                result = generate_mock_response(user_profile, candidates)
            
            # Display results
            st.success(f"Tim thay {result['filtered_count']} ung vien phu hop tu {result['total_candidates']} ho so")
            
            if result["matches"]:
                for i, match in enumerate(result["matches"]):
                    st.markdown(f"## 🏆 Top {i+1}: {match['candidate']['name']}")
                    render_candidate_card(
                        match["candidate"],
                        match["score"],
                        match["reasons"],
                        match["warnings"],
                        match["opening_message"]
                    )
                    st.markdown("---")
            else:
                st.warning("Khong tim thay ung vien phu hop. Thu mo rong tieu chi tim kiem.")
        
        elif submitted and not name:
            st.warning("⚠️ Vui long nhap ten cua ban de bat dau tim kiem")
        
        else:
            st.info("👆 Dien thong tin o thanh ben trai va nhan 'Tim kiem' de xem ket qua")
    
    with tab2:
        st.header("👥 Tat ca ung vien")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_location = st.selectbox("Loc theo dia diem", ["Tat ca"] + list(set(c.get("location", "") for c in candidates)))
        with col2:
            filter_goal = st.selectbox("Loc theo muc tieu", ["Tat ca"] + list(set(c.get("relationship_goal", "") for c in candidates)))
        with col3:
            filter_smoking = st.selectbox("Loc theo hut thuoc", ["Tat ca", "Khong hut", "Co hut"])
        
        # Apply filters
        filtered = candidates
        if filter_location != "Tat ca":
            filtered = [c for c in filtered if c.get("location") == filter_location]
        if filter_goal != "Tat ca":
            filtered = [c for c in filtered if c.get("relationship_goal") == filter_goal]
        if filter_smoking == "Khong hut":
            filtered = [c for c in filtered if not c.get("smoking")]
        elif filter_smoking == "Co hut":
            filtered = [c for c in filtered if c.get("smoking")]
        
        st.info(f"Hien thi {len(filtered)} / {len(candidates)} ung vien")
        
        # Display all candidates
        for candidate in filtered:
            personality = candidate.get('personality', 'N/A')
            if isinstance(personality, list):
                personality = ', '.join(personality)
            
            interests = candidate.get('interests', [])
            if isinstance(interests, list):
                interests_str = ", ".join(interests)
            else:
                interests_str = str(interests)
            
            with st.expander(f"👤 {candidate['name']} - {candidate['age']} tuoi - 📍 {candidate.get('location', 'N/A')}"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**Gioi tinh:** {candidate.get('gender', 'N/A')}")
                    st.markdown(f"**Tinh cach:** {personality}")
                    st.markdown(f"**So thich:** {interests_str}")
                    st.markdown(f"**Muc tieu:** {candidate.get('relationship_goal', 'N/A')}")
                    st.markdown(f"**Bio:** {candidate.get('bio', 'N/A')}")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown(f"🚬 Hut thuoc: {'Co' if candidate.get('smoking') else 'Khong'}")
                        st.markdown(f"🍺 Uong ruou: {candidate.get('drinking', 'N/A')}")
                    with col_b:
                        st.markdown(f"💰 Yeu xa: {'Duoc' if candidate.get('long_distance_ok') else 'Khong'}")
                    
                    important = candidate.get('important_criteria', [])
                    if important:
                        st.markdown("**Tieu chi quan trong:**")
                        for c in important:
                            st.markdown(f"- {c}")
                    
                    notes = candidate.get('notes', '')
                    if notes:
                        st.markdown(f"**Ghi chu:** {notes}")
                
                with col2:
                    st.markdown("### Thong tin nhanh")
                    st.markdown(f"📍 {candidate.get('location', 'N/A')}")
                    st.markdown(f"💕 {candidate.get('relationship_goal', 'N/A')}")
    
    with tab3:
        st.header("ℹ️ Huong dan su dung")
        
        st.markdown("""
        ### Cach su dung Cupid Agent
        
        1. **Dien thong tin ca nhan** o thanh ben trai
           - Tuoi, gioi tinh, dia diem
           - Mo ta tinh cach cua ban
           - So thich (phan cach bang dau phay)
           - Muc tieu quan he
        
        2. **Nhan "Tim kiem"** de Agent phan tich
        
        3. **Xem ket qua**:
           - Diem tuong thich (0-100)
           - Ly do phu hop
           - Canh bao (neu co)
           - Goi y mo loi
        
        ### Luu y
        - 💡 Dien cang nhieu thong tin, ket qua cang chinh xac
        - ⚠️ Agent chi dua ra goi y, quyet dinh cuoi cung la cua ban
        - 🔒 Thong tin cua ban duoc bao mat
        """)
        
        st.markdown("---")
        st.markdown("### 🔧 Cong nghe su dung")
        st.markdown("- **Streamlit** - Web UI Framework")
        st.markdown("- **ReAct Agent** - Reasoning + Action Loop")
        st.markdown(f"- **Mock Mode** - Dang chay voi {len(candidates)} ho so du lieu")


if __name__ == "__main__":
    main()
