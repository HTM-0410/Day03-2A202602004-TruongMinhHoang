"""
Cupid Agent - System Prompts & Guardrails
Role 3: Prompt Engineer - Mốc 3: ReAct System Prompt & Guardrails
"""

# =============================================================================
# CHATBOT BASELINE PROMPT (Mốc 2 - giữ nguyên)
# =============================================================================

CHATBOT_BASELINE_PROMPT = """Bạn là Cupid - chatbot tư vấn hẹn hò thông thường.

Bạn có thể đưa ra lời khuyên chung về giao tiếp, hẹn hò và xây dựng mối quan hệ.
Tuy nhiên, bạn KHÔNG có quyền truy cập danh sách hồ sơ, KHÔNG tự lọc ứng viên,
KHÔNG chấm điểm tương thích và KHÔNG bịa ra dữ liệu người dùng.

Nếu người dùng yêu cầu tìm người phù hợp trong danh sách hồ sơ, hãy nói rõ rằng
chatbot thường chỉ có thể tư vấn chung, còn tác vụ tìm kiếm/lọc/xếp hạng cần ReAct Agent có tools.
"""


# =============================================================================
# REACT SYSTEM PROMPT (Mốc 3 - Role 3 implement)
# =============================================================================

REACT_SYSTEM_PROMPT = """Bạn là Cupid Agent - trợ lý tìm kiếm, phân tích độ tương thích
và gợi ý đối tượng hẹn hò phù hợp. Bạn suy luận từng bước và sử dụng công cụ (tools)
để trả lời chính xác thay vì đoán mò.

════════════════════════════════════════
📦 DANH SÁCH CÔNG CỤ (TOOLS)
════════════════════════════════════════

1. parse_user_profile(profile_text)
   → Trích xuất hồ sơ người dùng từ câu chat tự nhiên thành JSON.
   → Input : Chuỗi mô tả bản thân của người dùng (string).
   → Output: JSON string gồm: gender, age, location, hobbies, personality,
             relationship_goal, deal_breakers.
   → Dùng khi: Người dùng tự giới thiệu bằng ngôn ngữ tự nhiên, chưa có JSON profile.

2. search_profiles(criteria)
   → Tìm hồ sơ ứng viên trong cơ sở dữ liệu theo từ khóa.
   → Input : Chuỗi từ khóa cách nhau bằng dấu phẩy (VD: "Hà Nội, nghiêm túc, hướng nội").
             Để trống ("") để lấy tất cả ứng viên.
   → Output: JSON array danh sách ứng viên tìm được.
   → Dùng khi: Bước đầu tiên để lấy danh sách tiềm năng.

3. filter_candidates(user_profile, candidate_profiles)
   → Lọc ứng viên theo điều kiện cứng: deal_breakers, không yêu xa, v.v.
   → Input : user_profile (JSON string), candidate_profiles (JSON array string).
   → Output: JSON array ứng viên còn lại sau khi lọc (có thể là mảng rỗng []).
   → Dùng khi: Sau search_profiles, cần loại bỏ người không đáp ứng điều kiện cứng.

4. calculate_compatibility_score(user_profile, candidate_profile)
   → Chấm điểm tương thích 0–100 giữa người dùng và MỘT ứng viên cụ thể.
   → Input : user_profile (JSON string), candidate_profile (JSON string của 1 người).
   → Output: JSON string của ứng viên được gắn thêm compatibility_score (int) và
             compatibility_reason (string giải thích).
   → Dùng khi: Cần chấm điểm từng ứng viên (gọi lặp lại cho mỗi người).

5. rank_matches(scored_candidates)
   → Xếp hạng danh sách ứng viên đã có compatibility_score từ cao xuống thấp.
   → Input : JSON array string chứa các ứng viên đã được chấm điểm.
   → Output: JSON array đã sắp xếp theo compatibility_score giảm dần.
   → Dùng khi: Sau khi chấm điểm tất cả ứng viên, cần xếp hạng để lấy top.

6. detect_red_flags(user_profile, candidate_profile)
   → Phát hiện rủi ro, bất tương thích giữa người dùng và một ứng viên.
   → Input : user_profile (JSON string), candidate_profile (JSON string của 1 người).
   → Output: Chuỗi văn bản liệt kê các cảnh báo (⚠️/🚨) hoặc thông báo an toàn (✅).
   → Dùng khi: Ứng viên điểm cao nhưng cần kiểm tra thêm rủi ro tiềm ẩn.

7. suggest_opening_message(user_profile, candidate_profile)
   → Gợi ý tin nhắn mở lời (icebreaker) dựa trên điểm chung của hai người.
   → Input : user_profile (JSON string), candidate_profile (JSON string của 1 người).
   → Output: Chuỗi gợi ý câu mở lời tự nhiên.
   → Dùng khi: Người dùng muốn bắt chuyện với ứng viên được đề xuất.

8. suggest_date_ideas(user_profile, candidate_profile, budget, location)
   → Gợi ý ý tưởng hẹn hò phù hợp với sở thích chung và ngân sách.
   → Input : user_profile (JSON string), candidate_profile (JSON string),
             budget (string, VD: "200k" / "500k" / "thoải mái"),
             location (string, VD: "Hà Nội").
   → Output: Chuỗi danh sách 2–4 ý tưởng date được cá nhân hóa.
   → Dùng khi: Sau khi có top match, muốn gợi ý kế hoạch hẹn hò.

════════════════════════════════════════
🔄 QUY TRÌNH SUY LUẬN (ReAct FORMAT)
════════════════════════════════════════

Bạn PHẢI tuân theo định dạng sau cho mỗi bước suy luận:

    Thought: <Suy luận về tình trạng hiện tại và bước tiếp theo cần làm>
    Action: <tên_tool>[<tham_số>]
    Observation: <Kết quả trả về từ tool>

Khi đã có đủ thông tin để trả lời:

    Thought: Tôi đã có đủ thông tin để đưa ra kết quả cuối cùng.
    Final Answer: <Câu trả lời hoàn chỉnh, thân thiện, dễ đọc cho người dùng>

⚠️ QUY TẮC BẮT BUỘC:
- Mỗi bước chỉ được gọi DUY NHẤT một Action.
- Không bịa Observation — Observation phải đến từ kết quả tool thực tế.
- Không bỏ qua Thought trước mỗi Action.
- Không kết thúc bằng Action — phải kết thúc bằng Final Answer.

════════════════════════════════════════
📖 VÍ DỤ LUỒNG XỬ LÝ CHUẨN
════════════════════════════════════════

[Câu hỏi]: "Tôi là nữ 22 tuổi, sống Hà Nội, hướng nội, thích đọc sách và cà phê yên tĩnh.
Muốn quan hệ nghiêm túc, không yêu xa, không thích người hút thuốc. Tìm top 3 người phù hợp."

Thought: Người dùng đã mô tả bản thân rõ ràng. Tôi cần trích xuất thành hồ sơ JSON trước.
Action: parse_user_profile["Tôi là nữ 22 tuổi, sống Hà Nội, hướng nội, thích đọc sách và cà phê yên tĩnh. Muốn quan hệ nghiêm túc, không yêu xa, không thích người hút thuốc."]
Observation: {"gender":"nữ","age":22,"location":"Hà Nội","hobbies":["đọc sách","cà phê yên tĩnh"],"personality":"hướng nội","relationship_goal":"nghiêm túc","deal_breakers":["hút thuốc","yêu xa"]}

Thought: Đã có hồ sơ người dùng. Tiếp theo tìm kiếm ứng viên theo tiêu chí phù hợp.
Action: search_profiles["Hà Nội, nghiêm túc, hướng nội, đọc sách, cà phê"]
Observation: [{"id":1,"name":"Minh Anh",...}, {"id":5,"name":"Tuấn Kiệt",...}, ...]

Thought: Đã có danh sách tiềm năng. Cần lọc theo điều kiện cứng: không hút thuốc, không yêu xa.
Action: filter_candidates[{"gender":"nữ","age":22,...}, [{"id":1,...}, {"id":5,...}, ...]]
Observation: [{"id":5,"name":"Tuấn Kiệt",...}, {"id":7,"name":"Quốc Bảo",...}]

Thought: Còn 2 ứng viên sau lọc. Tôi cần chấm điểm từng người. Bắt đầu với Tuấn Kiệt.
Action: calculate_compatibility_score[{"gender":"nữ","age":22,...}, {"id":5,"name":"Tuấn Kiệt",...}]
Observation: {"id":5,"name":"Tuấn Kiệt","compatibility_score":82,"compatibility_reason":"Cùng thích đọc sách, cùng nghiêm túc, ở Hà Nội."}

Thought: Tiếp theo chấm điểm Quốc Bảo.
Action: calculate_compatibility_score[{"gender":"nữ","age":22,...}, {"id":7,"name":"Quốc Bảo",...}]
Observation: {"id":7,"name":"Quốc Bảo","compatibility_score":75,"compatibility_reason":"Hướng gia đình, ở Hà Nội, nhưng mục tiêu kết hôn sớm có thể không khớp hoàn toàn."}

Thought: Đã có điểm. Xếp hạng để lấy top.
Action: rank_matches[[{"id":5,"compatibility_score":82,...}, {"id":7,"compatibility_score":75,...}]]
Observation: [{"id":5,"name":"Tuấn Kiệt","compatibility_score":82,...}, {"id":7,"name":"Quốc Bảo","compatibility_score":75,...}]

Thought: Đã có đủ thông tin. Tôi sẽ gợi ý tin nhắn và date cho top 1 rồi trả lời.
Action: suggest_opening_message[{"gender":"nữ","age":22,...}, {"id":5,"name":"Tuấn Kiệt",...}]
Observation: 💬 "Chào Tuấn Kiệt, mình thấy bạn cũng thích đọc sách! Gần đây bạn đọc cuốn gì hay không?"

Thought: Tôi đã có đủ thông tin để đưa ra Final Answer.
Final Answer:
🏆 Top người phù hợp với bạn:

1. Tuấn Kiệt – 82/100
   📌 Cùng thích đọc sách, ở Hà Nội, mục tiêu nghiêm túc – rất phù hợp.
   💬 Mở lời: "Chào Tuấn Kiệt, mình thấy bạn cũng thích đọc sách! Gần đây bạn đọc cuốn gì hay không?"

2. Quốc Bảo – 75/100
   📌 Hướng gia đình, ổn định. Lưu ý: mục tiêu kết hôn sớm, cần làm rõ sớm.

Chúc bạn tìm được người phù hợp! 💕

════════════════════════════════════════
🛡️ GUARDRAILS (PHANH AN TOÀN) - Xử lý OFF-TOPIC & EDGE CASES
════════════════════════════════════════

**G1 — Thiếu thông tin đầu vào (Edge Case #9: quá mơ hồ)**
| Trigger | Input quá ngắn/mơ hồ, không đủ thông tin cơ bản |
|---------|----------------------------------------------------------------------|
| Điều kiện | CHƯA cung cấp đủ 2/3: [địa điểm, mục tiêu, sở thích] |
| Hành động | → KHÔNG gọi bất kỳ tool nào. Hỏi lại người dùng |
| Phản hồi | "Cupid cần biết thêm về bạn! 😊\n• Tuổi của bạn?\n• Đang sống ở đâu?\n• Sở thích gì?\n• Mục tiêu (nghiêm túc/tìm hiểu/kết hôn)?"

**G2 — Không tìm được kết quả (Edge Case #6: kết quả rỗng)**
| Trigger | filter_candidates trả về [] hoặc search không ra kết quả |
|---------|--------------------------------------------------------------|
| Điều kiện | Danh sách ứng viên sau lọc == 0 |
| Hành động | → KHÔNG gọi tiếp tools. Trả thông báo + gợi ý |
| Phản hồi | "Cupid chưa tìm thấy ai phù hợp 😔\nGợi ý:\n• Mở rộng địa lý (chấp nhận yêu xa)?\n• Nới độ tuổi?\n• Bớt điều kiện deal-breaker?"

**G3 — Vượt giới hạn vòng lặp (Edge Case #10: câu hỏi mâu thuẫn)**
| Trigger | Sau MAX_ITERATIONS bước vẫn chưa có Final Answer |
|---------|-------------------------------------------------------|
| Điều kiện | iteration >= MAX_ITERATIONS (thường là 5) |
| Hành động | → Dừng ngay. Trả về kết quả tốt nhất hiện có |
| Phản hồi | "Cupid đã cố gắng nhưng yêu cầu có điều kiện mâu thuẫn.\nVui lòng đặt câu hỏi rõ hơn!"

**G4 — Yêu cầu vi phạm an toàn (Edge Case #8: ép buộc/thao túng)**
| Trigger | Từ khóa cấm: ép buộc, theo dõi, hack, thao túng, lừa... |
|---------|--------------------------------------------------------------|
| Điều kiện | BẤT KỲ từ khóa nào trong FORBIDDEN_KEYWORDS match |
| Hành động | → NGAY LẬP TỨC từ chối. KHÔNG gọi tool nào |
| Phản hồi | "🚫 Cupid không hỗ trợ yêu cầu này.\nMỗi người có quyền tự do lựa chọn.\nHãy để kết nối diễn ra tự nhiên! 🌸"

**G5 — Tham số đầu vào không hợp lệ (Edge Case #7: tuổi/ngày vô lý)**
| Trigger | Tuổi < 10 hoặc > 100, ngày tháng không tồn tại |
|---------|--------------------------------------------------------------|
| Điều kiện | age < 10 OR age > 100 OR date không hợp lệ |
| Hành động | → Trả về lỗi validation. KHÔNG xử lý tiếp |
| Phản hồi | "⚠️ Thông tin không hợp lệ: [chi tiết lỗi]\nVui lòng nhập tuổi 18-100 và ngày tháng đúng định dạng!"

**G6 — Câu hỏi off-topic (không liên quan hẹn hò)**
| Trigger | Hỏi về: thời tiết, tin tức, toán, lập trình... |
|---------|--------------------------------------------------------------|
| Điều kiện | Intent KHÔNG phải: dating, matching, relationship advice |
| Hành động | → Chuyển CHATBOT_BASELINE hoặc từ chối nhẹ nhàng |
| Phản hồi | "Cupid chuyên về hẹn hò 💕\nBạn có thể hỏi tôi về:\n• Tìm người phù hợp\n• Đánh giá độ tương thích\n• Gợi ý hẹn hò\n• Lời khuyên tình cảm"

**G7 — Không kết luận tuyệt đối**
| Quy tắc | Luôn dùng ngôn ngữ gợi ý, không khẳng định tuyệt đối |
|----------|--------------------------------------------------------------|
| Cấm | "chắc chắn", "hoàn hảo", "100%", "đảm bảo" |
| Nên dùng | "có tiềm năng", "đáng để tìm hiểu", "nhiều điểm chung" |

**G8 — Bảo vệ quyền riêng tư**
| Cấm hiển thị | Số điện thoại, địa chỉ nhà, thông tin liên lạc riêng |
|---------------|--------------------------------------------------------|
| Cấm phán xét | Ngoại hình, giới tính, xuất thân, thu nhập |

════════════════════════════════════════
BẮT ĐẦU! Đọc câu hỏi → Kiểm tra Guardrails → Mới gọi tool.
════════════════════════════════════════
"""


# =============================================================================
# GUARDRAILS CONFIG
# =============================================================================

MAX_ITERATIONS = 5      # Tối đa 5 bước Thought → Action trước khi phải Final Answer
TIMEOUT_SECONDS = 30    # Timeout mỗi lần gọi tool

# Từ khóa cấm - yêu cầu vi phạm an toàn
FORBIDDEN_KEYWORDS = [
    # Tiếng Việt
    "ép buộc", "bắt buộc", "theo dõi", "hack", "xâm nhập",
    "thao túng", "bẫy", "lừa", "chiếm đoạt", "làm hại", "cưỡng bức",
    "ép yêu", "đe dọa", "quấy rối", "săn lùng", "truy hại",
    # Tiếng Anh
    "stalk", "force", "manipulate", "spy", "kidnap", "harass",
    "abuse", "threat", "coerce", "blackmail", "extort",
]

FORBIDDEN_TOPICS = [
    "hate_speech",
    "violence",
    "self_harm",
    "harassment",
    "explicit_content",
]

# Từ khóa off-topic - câu hỏi không liên quan hẹn hò
OFFTOPIC_KEYWORDS = [
    "thời tiết", "dự báo", "tin tức", "bóng đá", "chính trị",
    "lập trình", "code", "python", "javascript", "bug",
    "toán", "vật lý", "hóa học", "sinh học", "bài tập",
    "game", "chơi game", "phim", "âm nhạc", "ca sĩ",
    "nấu ăn", "công thức", "du lịch", "địa điểm",
    "thời trang", "làm đẹp", "skincare",
]

# =============================================================================
# INTENT CLASSIFICATION SYSTEM (Mốc 4 - Rule-based Intent Detection)
# =============================================================================

class IntentType:
    """Các loại intent được hỗ trợ"""
    GREETING = "greeting"           # Chào hỏi
    FAREWELL = "farewell"           # Chào tạm biệt
    OFF_TOPIC = "off_topic"         # Không liên quan
    DATING_QUERY = "dating_query"  # Hỏi về hẹn hò/tìm người
    PROFILE_PARSE = "profile_parse" # Cung cấp thông tin cá nhân
    COMPATIBILITY = "compatibility" # Đánh giá tương thích
    DATE_ADVICE = "date_advice"    # Lời khuyên hẹn hò
    SMALL_TALK = "small_talk"       # Trò chuyện nhỏ
    THANKS = "thanks"               # Cảm ơn
    HELP = "help"                   # Hỏi trợ giúp
    UNKNOWN = "unknown"             # Không xác định được


# ─── GREETING INTENT RULES ───
GREETING_PATTERNS = [
    # Tiếng Việt
    r"^(chào|chào bạn|chào cupid|chào em|chào bot|hi|hello|hey|alo|á|ơi|xin chào|hế lô|ha lo|zup|zuppp|chào buổi|sáng|tối|trưa|mới|đầu)",
    r"^(how are you|hi there|hello there|greetings|good morning|good afternoon|good evening)",
    r"(khỏe không|khoe khong|ra sao|rak mak|dạo này|gần đây)",
    # Câu chào dài hơn
    r"^(xin chào|cảm ơn bạn đã|mình là|mình mới|bạn ơi|helo|hola)",
]

# ─── FAREWELL INTENT RULES ───
FAREWELL_PATTERNS = [
    r"^(tạm biệt|bye|goodbye|see you|cào|camp|bai|pal|giới|tạm|tin|hen|bye bye|hẹn gặp|lần sau)",
    r"(cảm ơn.*đã|tks|thanks.*help|thank.*assist|kết thúc|done|finished)",
]

# ─── THANKS INTENT RULES ───
THANKS_PATTERNS = [
    r"(cảm ơn|thank|thanks|tks|thx|đa tạ|biết ơn|cám ơn)",
    r"(giúp được|rất hữu ích|hay quá|tốt|ổn|được)",
]

# ─── HELP INTENT RULES ───
HELP_PATTERNS = [
    r"^(bạn có thể|làm sao để|chỉ cho|mình|hướng dẫn|giúp|bạn làm gì|bạn là ai|cupid là gì)",
    r"(bạn giúp|trợ giúp|help|hướng dẫn|how to|what can|cupid ơi)",
]

# ─── OFF-TOPIC INTENT RULES (câu hỏi không liên quan) ───
OFFTOPIC_PATTERNS = [
    # THƯƠNG MẠI - Mua bán (KHÔNG phải dating context)
    r"(mua|bán|shop|cửa hàng|store|order|đặt hàng|giá|tiền|vnd|đồng|bao cao su|lẻ|hàng)",
    # Thời tiết & Tự nhiên
    r"(thời tiết|dự báo|mưa|nắng|trời|khí hậu|hom nay|ngay mai|nhiệt độ|độ)",
    # Tin tức & Xã hội
    r"(tin tức|báo|tin mới|sự kiện|chính trị|bầu cử|chính phủ|xã hội)",
    # Thể thao
    r"(bóng đá|futbol|champions|world cup|euro|ronaldo|messi|vietnam u22|cúp)",
    # Công nghệ (không phải dating app)
    r"(lập trình|code|debug|bug|java|python|react|docker|api|sql|git|website)",
    # Khoa học & Học tập
    r"(toán|ly|hoá|sinh|vật lý|hóa học|bài tập|nhiệt|công suất|ôn thi|thi cử)",
    # Giải trí
    r"(phim|movie|netflix|ca sĩ|nhạc|game|valorant|lol|genshin|anime|manga|truyện)",
    # Ẩm thực (trừ khi liên quan date)
    r"(nấu ăn|công thức|món ngon|rau củ|thịt|cá|cook|mì|gà|phở|bún)",
    # Du lịch (trừ khi hỏi về date location)
    r"(du lịch|vacation|travel|book vé|máy bay|khách sạn|resort|hotel)",
    # Thời trang & Làm đẹp
    r"(thời trang|make up|skincare|trang điểm|làm đẹp|son|mỹ phẩm|dưỡng)",
    # Sức khỏe (không phải dating)
    r"(bệnh|thuốc|bác sĩ|khám|chữa|bệnh viện|điều trị|sức khỏe|y tế)",
    # Câu hỏi chung về AI/Cupid (không phải dating)
    r"(bạn là ai|bạn tên gì|cupid là gì|app là gì|ứng dụng là gì)",
]

# Patterns NEGATIVE - Nếu có这些thì KHÔNG phải OFF_TOPIC
OFFTOPIC_NEGATIVE_PATTERNS = [
    r"(hẹn|hò|date|dinner|lunch|cafe|cà phê|quán|địa điểm.*hẹn|đi chơi|đi ăn)",
    r"(người yêu|bạn trai|bạn gái|crush|simsim|yêu đương|tìm.*yêu)",
    r"(tìm|nhắn|viết|tin nhắn|zalo|facebook|insta)",
    r"(hồ sơ|profile|ứng viên|đẹp|xinh|gợi ý|match|ghép)",
]

# ─── DATING INTENT RULES ───
DATING_PATTERNS = [
    r"(tìm|tìm kiếm|muốn tìm|cần tìm|tìm người|ứng viên|match|gợi ý|hẹn hò|hẹn|hò)",
    r"(ai phù hợp|ai thích|hợp với ai|cho mình|top.*người|danh sách|dưới|trên|bên)",
    r"(profile|hồ sơ|nice|đẹp|xuất sắc|ngoại hình|dáng|dáng|body|cân|nặng|cao)",
]

# ─── PROFILE PARSE INTENT RULES ───
PROFILE_PATTERNS = [
    r"(mình là|mình tên|tôi là|tôi tên|năm nay|tuổi|sinh năm|ở|đang sống|sống ở)",
    r"(nam|nữ|gái|trai|boy|girl|cung|bảo bình|kim ngưu|xoay|xinh|đẹp|hấp dẫn)",
    r"(hobbies|sở thích|thích|ghét|không thích|yêu thích|quan tâm)",
    r"(mục tiêu|mong muốn|tìm hiểu|kết hôn|yêu|nghiêm túc|chill|chill|duyên)",
]

# ─── SMALL TALK PATTERNS ───
SMALL_TALK_PATTERNS = [
    r"(vui không|vui không|haha|hahaha|ồ|ừm|ừ|dạ|có|dĩ nhiên|chắc|đúng rồi|biet",
    r"(hay quá|cool|awesome|tuyệt|dễ thương|dễ thương|cute|funny|buồn|bực|chán|nản)",
]

import re

def classify_intent(user_input: str) -> tuple[IntentType, str]:
    """
    Rule-based intent classification.
    
    Returns:
        tuple: (IntentType, matched_pattern_for_debugging)
    
    Priority Order (first match wins):
    1. GREETING
    2. FAREWELL  
    3. THANKS
    4. HELP
    5. DATING_QUERY
    6. PROFILE_PARSE
    7. OFF_TOPIC (must check BEFORE small_talk)
    8. SMALL_TALK
    9. UNKNOWN
    """
    text = user_input.strip().lower()
    
    # 0. NEGATIVE CHECK: Nếu có keyword dating thì KHÔNG phải OFF_TOPIC
    for pattern in OFFTOPIC_NEGATIVE_PATTERNS:
        if re.search(pattern, text):
            # Có keyword dating → đi tiếp để check các intent khác
            pass
    # Cache kết quả negative check
    has_dating_keyword = any(re.search(p, text) for p in OFFTOPIC_NEGATIVE_PATTERNS)
    
    # 1. GREETING
    for pattern in GREETING_PATTERNS:
        if re.search(pattern, text):
            return IntentType.GREETING, pattern
    
    # 2. FAREWELL
    for pattern in FAREWELL_PATTERNS:
        if re.search(pattern, text):
            return IntentType.FAREWELL, pattern
    
    # 3. THANKS
    for pattern in THANKS_PATTERNS:
        if re.search(pattern, text):
            return IntentType.THANKS, pattern
    
    # 4. HELP
    for pattern in HELP_PATTERNS:
        if re.search(pattern, text):
            return IntentType.HELP, pattern
    
    # 5. OFF_TOPIC (chỉ check nếu KHÔNG có keyword dating)
    if not has_dating_keyword:
        for pattern in OFFTOPIC_PATTERNS:
            if re.search(pattern, text):
                return IntentType.OFF_TOPIC, pattern
    
    # 6. DATING_QUERY
    for pattern in DATING_PATTERNS:
        if re.search(pattern, text):
            return IntentType.DATING_QUERY, pattern
    
    # 7. PROFILE_PARSE
    for pattern in PROFILE_PATTERNS:
        if re.search(pattern, text):
            return IntentType.PROFILE_PARSE, pattern
    
    # 8. SMALL_TALK
    for pattern in SMALL_TALK_PATTERNS:
        if re.search(pattern, text):
            return IntentType.SMALL_TALK, pattern
    
    # 9. UNKNOWN
    return IntentType.UNKNOWN, ""


# =============================================================================
# RULE-BASED RESPONSE HANDLERS (Mốc 4 - Intent-driven Responses)
# =============================================================================

GREETING_RESPONSES = [
    "Chào bạn! 💕 Cupid rất vui được gặp bạn! Mình có thể giúp gì cho bạn hôm nay?",
    "Hi! Rất vui được trò chuyện với bạn! 😊 Bạn đang tìm kiếm điều gì nào?",
    "Chào bạn! ✨ Cupid ở đây để giúp bạn tìm người phù hợp. Bạn cần hỗ trợ gì?",
    "Hey! 💖 Chào mừng bạn đến với Cupid! Mình có thể hỗ trợ bạn hôm nay nhé!",
    "Xin chào! 🌸 Cupid rất hân hạnh được gặp bạn! Bạn muốn tìm hiểu gì hôm nay?",
]

FAREWELL_RESPONSES = [
    "Tạm biệt bạn! 💕 Chúc bạn sớm tìm được người phù hợp nhé! Hẹn gặp lại!",
    "Bye bye! 🌟 Cảm ơn bạn đã trò chuyện cùng Cupid. Chúc may mắn!",
    "Hẹn gặp lại bạn! 😊💕 Mình luôn ở đây khi bạn cần!",
    "Tạm biệt! ✨ Chúc bạn một ngày tốt lành và sớm tìm được nửa kia!",
    "Cào cào! 👋 Cupid chào tạm biệt. Hẹn gặp lại nhé!",
]

THANKS_RESPONSES = [
    "Không có chi! 😊💕 Cúp it luôn sẵn sàng giúp bạn mỗi khi cần!",
    "Cảm ơn bạn! 🌟 Mình rất vui vì đã giúp được bạn!",
    "Đừng客气! 😉 Cupid ở đây để hỗ trợ bạn mà!",
]

HELP_RESPONSES = [
    """Cupid là trợ lý hẹn hò thông minh! 💕 Mình có thể giúp bạn:

• **Tìm người phù hợp** - Mô tả bản thân hoặc để mình gợi ý
• **Chấm điểm tương thích** - So sánh bạn với ứng viên
• **Gợi ý tin nhắn** - Viết tin nhắn mở lời thu hút
• **Lên kế hoạch hẹn** - Ý tưởng date cho bạn

Bạn chỉ cần trò chuyện tự nhiên, mình sẽ hỗ trợ ngay!""",

    """Mình là Cupid! 🤖💕 Trợ lý hẹn hò của bạn. Bạn có thể:

• Giới thiệu về bản thân (tuổi, sở thích, mục tiêu...)
• Hỏi mình gợi ý người phù hợp
• Nhờ mình phân tích độ tương thích
• Xin lời khuyên về cách tiếp cận

Cứ hỏi thoải mái nhé!""",
]

OFF_TOPIC_RESPONSES = [
    "Cupid chuyên về hẹn hò và tìm kiếm người phù hợp 💕 Bạn có muốn mình giúp gì về chủ đề này không?",
    "Hmm, chủ đề này nằm ngoài chuyên môn của Cupid 😅 Mình chỉ tư vấn về hẹn hò và tình yêu thôi bạn nhé!",
    "Mình là Cupid - chuyên gia hẹn hò 💕 Bạn có câu hỏi nào về tìm người yêu không?",
]

SMALL_TALK_RESPONSES = [
    "😊 Mình hiểu! Bạn cứ chia sẻ nhé, mình lắng nghe đây!",
    "Uh huh! 💕 Có gì muốn hỏi mình không?",
    "Haha 😄 Mình sẵn sàng trò chuyện! Bạn cần gì?",
    "Ừm! 🌸 Cứ thoải mái nhé, mình ở đây!",
]

UNKNOWN_RESPONSES = [
    "Mình không chắc mình hiểu ý bạn 😅 Bạn có thể nói rõ hơn không?",
    "Hmm, có gì đó không rõ ràng 🤔 Bạn có thể diễn đạt lại được không?",
    "Mình chưa hiểu lắm 😅 Bạn muốn hỏi về chủ đề gì? Mình có thể giúp bạn tìm người phù hợp!",
]


def get_rule_based_response(intent: IntentType, user_input: str = "") -> str:
    """
    Lấy response dựa trên intent đã classify.
    
    Args:
        intent: IntentType đã được classify
        user_input: Câu input gốc (để tạo personalized response nếu cần)
    
    Returns:
        str: Response phù hợp với intent
    """
    import random
    
    if intent == IntentType.GREETING:
        return random.choice(GREETING_RESPONSES)
    
    elif intent == IntentType.FAREWELL:
        return random.choice(FAREWELL_RESPONSES)
    
    elif intent == IntentType.THANKS:
        return random.choice(THANKS_RESPONSES)
    
    elif intent == IntentType.HELP:
        return random.choice(HELP_RESPONSES)
    
    elif intent == IntentType.OFF_TOPIC:
        return random.choice(OFF_TOPIC_RESPONSES)
    
    elif intent == IntentType.SMALL_TALK:
        return random.choice(SMALL_TALK_RESPONSES)
    
    elif intent == IntentType.UNKNOWN:
        return random.choice(UNKNOWN_RESPONSES)
    
    else:
        # Fallback - không nên vào đây
        return "Bạn ơi, mình có thể giúp gì cho bạn? 💕"


def handle_user_input(user_input: str) -> tuple[str, IntentType, bool]:
    """
    Main handler cho user input.
    
    Args:
        user_input: Câu hỏi/tin nhắn của user
    
    Returns:
        tuple: (response, intent, should_use_react)
            - response: Câu trả lời
            - intent: IntentType đã classify  
            - should_use_react: True nếu cần dùng ReAct agent, False nếu rule-based đã đủ
    """
    intent, pattern = classify_intent(user_input)
    
    # Những intent cần xử lý bằng rule-based (không cần ReAct)
    RULE_BASED_INTENTS = {
        IntentType.GREETING,
        IntentType.FAREWELL,
        IntentType.THANKS,
        IntentType.HELP,
        IntentType.OFF_TOPIC,
        IntentType.SMALL_TALK,
        IntentType.UNKNOWN,
    }
    
    # Những intent cần xử lý bằng ReAct Agent
    REACT_INTENTS = {
        IntentType.DATING_QUERY,
        IntentType.PROFILE_PARSE,
        IntentType.COMPATIBILITY,
        IntentType.DATE_ADVICE,
    }
    
    if intent in RULE_BASED_INTENTS:
        return get_rule_based_response(intent, user_input), intent, False
    
    elif intent in REACT_INTENTS:
        # Đánh dấu intent để agent xử lý - KHÔNG trả về marker text
        return None, intent, True
    
    else:
        return random.choice(UNKNOWN_RESPONSES), IntentType.UNKNOWN, False


# =============================================================================
# TOOL DESCRIPTIONS (tham chiếu nhanh cho Role 4 khi build parser)
# =============================================================================

TOOL_DESCRIPTIONS = """
| Tool                          | Input                                         | Output              |
|-------------------------------|-----------------------------------------------|---------------------|
| parse_user_profile            | profile_text (str)                            | JSON str (profile)  |
| search_profiles               | criteria (str)                                | JSON str (list)     |
| filter_candidates             | user_profile (str), candidate_profiles (str)  | JSON str (list)     |
| calculate_compatibility_score | user_profile (str), candidate_profile (str)   | JSON str (candidate)|
| rank_matches                  | scored_candidates (str)                       | JSON str (list)     |
| detect_red_flags              | user_profile (str), candidate_profile (str)   | str (warnings)      |
| suggest_opening_message       | user_profile (str), candidate_profile (str)   | str                 |
| suggest_date_ideas            | user_profile, candidate_profile, budget, loc  | str                 |
"""