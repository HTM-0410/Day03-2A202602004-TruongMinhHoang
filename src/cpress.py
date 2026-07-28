"""
💬 CUPRESS - Interactive Chatbot CLI
Trợ lý hẹn hò thông minh với ReAct Agent có khả năng:
- Trò chuyện tự nhiên bằng Tiếng Việt
- Sử dụng tools để tìm kiếm và phân tích độ tương thích
- Gợi ý mở lời và ý tưởng hẹn hò
"""

import os
import sys
import json
from datetime import datetime

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# UTF-8 support for Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

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


class CupidChatbot:
    """Interactive chatbot với ReAct Agent"""
    
    def __init__(self):
        self.provider = get_llm_provider()
        self.user_profile = None
        self.chat_history = []
        self.welcome_message = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║         💕  CHÀO MỪNG ĐẾN VỚI CUPRESS AGENT  💕            ║
║                                                              ║
║    Trợ lý hẹn hò thông minh - Tìm kiếm người phù hợp        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

Tôi là Cupid - trợ lý hẹn hò thông minh của bạn! 💘

Tôi có thể giúp bạn:
  🔍 Tìm kiếm người phù hợp dựa trên sở thích và tính cách
  💯 Đánh giá độ tương thích giữa hai người
  💬 Gợi ý câu mở lời hay nhất
  📅 Lên kế hoạch cho buổi hẹn hò hoàn hảo
  ⚠️ Cảnh báo các điểm cần lưu ý trong mối quan hệ

Hãy giới thiệu về bản thân bạn nhé - ví dụ:
"Tôi là nam, 25 tuổi, sống ở Hà Nội, thích đọc sách và du lịch"
"""

    def print_welcome(self):
        """In thông báo chào mừng"""
        print(self.welcome_message)
        print("─" * 60)

    def print_bot(self, message: str):
        """In tin nhắn từ bot với định dạng đẹp"""
        print(f"\n💕 Cupid: {message}")

    def print_user(self, message: str):
        """In tin nhắn từ user"""
        print(f"\n👤 Bạn: {message}")

    def parse_user_input(self, text: str) -> dict:
        """Sử dụng Gemini để parse thông tin user"""
        result = parse_user_profile(text)
        try:
            profile = json.loads(result)
            if "error" not in profile:
                return profile
        except:
            pass
        return {}

    def process_match_request(self, user_profile: dict) -> str:
        """Xử lý yêu cầu tìm kiếm match"""
        user_profile_json = json.dumps(user_profile, ensure_ascii=False)
        
        # Step 1: Search profiles
        criteria = f"{user_profile.get('location', '')}, {user_profile.get('relationship_goal', '')}, {', '.join(user_profile.get('hobbies', []))}"
        search_results = search_profiles(criteria)
        try:
            candidates = json.loads(search_results)
        except:
            candidates = MOCK_CANDIDATES

        # Step 2: Filter candidates
        filtered = filter_candidates(user_profile_json, json.dumps(candidates, ensure_ascii=False))
        try:
            filtered_list = json.loads(filtered)
            if isinstance(filtered_list, dict) and "error" in filtered_list:
                return f"😔 {filtered_list.get('message', 'Không tìm thấy ai phù hợp')}"
        except:
            filtered_list = candidates

        if not filtered_list:
            return "😔 Không tìm thấy ứng viên nào phù hợp với tiêu chí của bạn. Thử thay đổi một số điều kiện nhé!"

        # Step 3: Calculate compatibility scores
        scored = []
        for cand in filtered_list[:10]:
            cand_json = json.dumps(cand, ensure_ascii=False)
            result = calculate_compatibility_score(user_profile_json, cand_json)
            try:
                scored_cand = json.loads(result)
                if isinstance(scored_cand, dict) and "compatibility_score" in scored_cand:
                    scored.append(scored_cand)
            except:
                pass

        # Step 4: Rank matches
        if scored:
            ranked_json = rank_matches(json.dumps(scored, ensure_ascii=False))
            try:
                top_matches = json.loads(ranked_json)
            except:
                top_matches = scored[:3]
        else:
            top_matches = filtered_list[:3]

        # Step 5: Build response
        response = f"🎉 Tôi đã tìm thấy {len(top_matches)} người phù hợp nhất với bạn!\n\n"

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

            response += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            response += f"🏆 TOP {i}: {name}, {age} tuổi\n"
            response += f"📍 Địa điểm: {location}\n"
            response += f"🎯 Điểm tương thích: {score}/100\n"
            response += f"💡 {reason}\n"
            response += f"❤️ Sở thích: {hobbies_str}\n"

        # Add opening message suggestion for top 1
        if top_matches:
            top = top_matches[0]
            opening = suggest_opening_message(user_profile_json, json.dumps(top, ensure_ascii=False))
            response += f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            response += f"\n💬 **Gợi ý mở lời với {top.get('name', 'người này')}:**\n{opening}"

        return response

    def process_red_flags(self, candidate_name: str) -> str:
        """Phân tích red flags cho một ứng viên cụ thể"""
        if not self.user_profile:
            return "Bạn chưa giới thiệu về bản thân. Hãy kể cho tôi nghe về bạn trước nhé!"

        # Tìm candidate
        candidate = None
        for c in MOCK_CANDIDATES:
            if c['name'].lower() == candidate_name.lower():
                candidate = c
                break

        if not candidate:
            return f"Không tìm thấy người tên '{candidate_name}' trong danh sách."

        user_json = json.dumps(self.user_profile, ensure_ascii=False)
        cand_json = json.dumps(candidate, ensure_ascii=False)

        red_flags = detect_red_flags(user_json, cand_json)
        return f"🔍 **Phân tích về {candidate['name']}:**\n\n{red_flags}"

    def process_date_ideas(self, candidate_name: str) -> str:
        """Gợi ý ý tưởng hẹn hò"""
        if not self.user_profile:
            return "Bạn chưa giới thiệu về bản thân. Hãy kể cho tôi nghe về bạn trước nhé!"

        candidate = None
        for c in MOCK_CANDIDATES:
            if c['name'].lower() == candidate_name.lower():
                candidate = c
                break

        if not candidate:
            return f"Không tìm thấy người tên '{candidate_name}' trong danh sách."

        user_json = json.dumps(self.user_profile, ensure_ascii=False)
        cand_json = json.dumps(candidate, ensure_ascii=False)

        date_ideas = suggest_date_ideas(user_json, cand_json)
        return date_ideas

    def get_candidates_list(self) -> str:
        """Liệt kê tất cả ứng viên"""
        result = "📋 **DANH SÁCH ỨNG VIÊN HIỆN CÓ:**\n\n"
        for i, c in enumerate(MOCK_CANDIDATES, 1):
            name = c.get('name', 'N/A')
            age = c.get('age', 'N/A')
            location = c.get('location', 'N/A')
            goal = c.get('relationship_goal', 'N/A')
            hobbies = c.get('hobbies', [])
            if isinstance(hobbies, list):
                hobbies_str = ', '.join(hobbies[:2])
            else:
                hobbies_str = str(hobbies)
            result += f"{i}. **{name}**, {age} tuổi - 📍{location}\n"
            result += f"   🎯 {goal} | ❤️ {hobbies_str}\n\n"
        return result

    def understand_intent(self, text: str) -> str:
        """Hiểu intent từ câu hỏi của user và trả lời phù hợp"""
        text_lower = text.lower()

        # Intent: Tìm người phù hợp
        match_keywords = ["tìm", "tìm kiếm", "match", "phù hợp", "ghép đôi", 
                         "ai phù hợp", "người phù hợp", "gợi ý", "recommend"]
        if any(kw in text_lower for kw in match_keywords):
            return "match"

        # Intent: Xem danh sách
        list_keywords = ["danh sách", "list", "tất cả", "xem hết", "liệt kê"]
        if any(kw in text_lower for kw in list_keywords):
            return "list"

        # Intent: Phân tích red flags
        red_keywords = ["red flag", "cảnh báo", "rủi ro", "lưu ý", "nguy hiểm", "bất đồng"]
        if any(kw in text_lower for kw in red_keywords):
            return "red_flags"

        # Intent: Ý tưởng hẹn hò
        date_keywords = ["hẹn", "date", "đi chơi", "gặp mặt", "ý tưởng", "địa điểm"]
        if any(kw in text_lower for kw in date_keywords):
            return "date_ideas"

        # Intent: Trợ giúp
        help_keywords = ["help", "hướng dẫn", "giúp", "làm gì", "có thể làm"]
        if any(kw in text_lower for kw in help_keywords):
            return "help"

        # Default: parse profile
        return "parse_profile"

    def run(self):
        """Chạy chatbot tương tác"""
        self.print_welcome()

        while True:
            try:
                print("\n" + "─" * 60)
                user_input = input("👤 Bạn: ").strip()

                if not user_input:
                    continue

                # Exit commands
                if user_input.lower() in ['exit', 'quit', 'thoát', 'q', 'bye']:
                    print("\n💕 Cảm ơn bạn đã trò chuyện cùng Cupid! Chúc bạn sớm tìm được người phù hợp! 💘")
                    break

                # Intent detection
                intent = self.understand_intent(user_input)

                if intent == "parse_profile" or self.user_profile is None:
                    # Parse user profile
                    with open(os.devnull, 'w') as devnull:
                        sys.stdout = devnull
                    profile = self.parse_user_input(user_input)
                    sys.stdout = sys.__stdout__

                    if profile and not profile.get("error"):
                        self.user_profile = profile
                        age = profile.get('age', 'N/A')
                        gender = profile.get('gender', 'N/A')
                        location = profile.get('location', 'N/A')
                        hobbies = profile.get('hobbies', [])
                        goal = profile.get('relationship_goal', 'N/A')

                        hobbies_str = ', '.join(hobbies) if isinstance(hobbies, list) and hobbies else 'chưa rõ'

                        response = f"""✨ Đã ghi nhận thông tin về bạn!

📋 **Hồ sơ của bạn:**
• Giới tính: {gender}
• Tuổi: {age}
• Địa điểm: {location}
• Sở thích: {hobbies_str}
• Mục tiêu: {goal}

Bạn muốn tôi tìm người phù hợp với tiêu chí trên không? Hay bạn muốn tôi làm gì khác? 😊"""

                        if intent == "match":
                            response += "\n\n" + self.process_match_request(profile)
                    else:
                        response = f"""😕 Tôi chưa hiểu rõ về bạn lắm. Bạn có thể cho tôi biết thêm không?

Ví dụ: "Tôi là nam, 25 tuổi, sống ở Hà Nội, thích đọc sách và du lịch, muốn tìm mối quan hệ nghiêm túc"
"""
                    self.print_bot(response)

                elif intent == "match":
                    self.print_bot(self.process_match_request(self.user_profile))

                elif intent == "list":
                    self.print_bot(self.get_candidates_list())

                elif intent == "red_flags":
                    # Extract candidate name from input
                    for name in MOCK_CANDIDATES:
                        if name['name'].lower() in user_input.lower():
                            self.print_bot(self.process_red_flags(name['name']))
                            break
                    else:
                        self.print_bot("Bạn muốn phân tích red flags với ai? Hãy nêu tên người đó nhé!")

                elif intent == "date_ideas":
                    for name in MOCK_CANDIDATES:
                        if name['name'].lower() in user_input.lower():
                            self.print_bot(self.process_date_ideas(name['name']))
                            break
                    else:
                        self.print_bot("Bạn muốn gợi ý ý tưởng hẹn hò với ai? Hãy nêu tên người đó nhé!")

                elif intent == "help":
                    self.print_bot("""🤖 **Tôi có thể giúp bạn:**

1️⃣ **Tìm người phù hợp** - Nói "tìm người phù hợp với tôi"
2️⃣ **Xem danh sách ứng viên** - Nói "xem danh sách"
3️⃣ **Phân tích red flags** - Nói "phân tích [tên] có gì cần lưu ý"
4️⃣ **Gợi ý hẹn hò** - Nói "gợi ý chỗ đi chơi với [tên]"
5️⃣ **Trợ giúp** - Nói "help" hoặc "hướng dẫn"

Bạn cứ trò chuyện tự nhiên với tôi nhé! 💕""")

            except KeyboardInterrupt:
                print("\n\n💕 Cảm ơn bạn đã trò chuyện cùng Cupid! Chúc bạn sớm tìm được người phù hợp! 💘")
                break
            except Exception as e:
                print(f"\n💕 Có lỗi xảy ra: {str(e)}")
                print("Bạn có thể thử lại được không?")


def main():
    """Entry point"""
    print("=" * 60)
    print("   💕  CUPRESS - INTERACTIVE CHATBOT  💕")
    print("=" * 60)

    chatbot = CupidChatbot()
    chatbot.run()


if __name__ == "__main__":
    main()
