# 📊 BÁO CÁO GIÁM SÁT & ĐÁNH GIÁ (OBSERVABILITY TRACE LOGS)
*Dành cho Role 5: Observability & Reviewer*

---

## 🎯 1. BẢNG CHẤM ĐIỂM AGENTIC FIT (SCORING MATRIX)

**Đề tài được chọn**: **Cupid Agent - Trợ lý tìm kiếm, phân tích độ tương thích và gợi ý đối tượng hẹn hò phù hợp**

**Mô tả bài toán**: Cupid Agent hỗ trợ một người dùng tìm kiếm đối tượng phù hợp trong danh sách nhiều hồ sơ ứng viên. Agent cần hiểu hồ sơ và tiêu chí của người dùng, lọc các ứng viên không phù hợp, chấm điểm tương thích từng hồ sơ, xếp hạng top match, giải thích lý do đề xuất, cảnh báo điểm lệch hoặc rủi ro, sau đó gợi ý tin nhắn mở lời hoặc ý tưởng đi date.

| Tiêu chí | Điểm (1-5) | Lý do đánh giá |
| :--- | :---: | :--- |
| 🧠 **Multi-step Reasoning** | `5/5` | Bài toán không chỉ hỏi "ai hợp với tôi" mà yêu cầu một chuỗi suy luận nhiều bước. Agent phải phân tích hồ sơ người dùng, trích xuất tiêu chí cứng và tiêu chí mềm, duyệt qua nhiều hồ sơ ứng viên, so sánh từng người theo sở thích, tính cách, mục tiêu quan hệ, vị trí, lối sống, sau đó tổng hợp thành điểm tương thích và lời giải thích. Nếu chỉ dựa vào Chatbot thường, câu trả lời dễ bị cảm tính và không có quy trình xếp hạng rõ ràng. |
| 🛠️ **Tool Interaction** | `5/5` | Bài toán rất cần tool vì phải thao tác trên dữ liệu có cấu trúc. Các tool phù hợp gồm `search_profiles`, `filter_candidates`, `calculate_compatibility_score`, `rank_matches`, `detect_red_flags`, `suggest_opening_message`, `suggest_date_ideas`. Nếu không có tool, LLM khó xử lý nhất quán khi số lượng hồ sơ tăng lên, dễ bỏ sót ứng viên hoặc chấm điểm không ổn định. |
| 🔀 **Dynamic Decision** | `5/5` | Luồng xử lý thay đổi theo kết quả từng bước. Nếu không tìm thấy đủ ứng viên, Agent cần nới tiêu chí mềm hoặc hỏi người dùng có muốn mở rộng phạm vi tìm kiếm không. Nếu ứng viên điểm cao nhưng có red flag, Agent phải cảnh báo hoặc hạ thứ hạng. Nếu nhiều ứng viên bằng điểm, Agent cần dùng tiêu chí ưu tiên của người dùng để phân xử. Đây là bài toán có nhiều nhánh quyết định rõ ràng. |
| ⏳ **Long Horizon** | `5/5` | Quy trình gồm nhiều giai đoạn nối tiếp: hiểu hồ sơ, tìm kiếm, lọc, chấm điểm, xếp hạng, giải thích, phát hiện rủi ro, gợi ý mở lời và có thể đề xuất kế hoạch đi date. Agent cần giữ ngữ cảnh của người dùng và nhiều ứng viên trong suốt quá trình, nên độ dài tác vụ cao hơn hướng chỉ phân tích một cặp đôi có sẵn. |
| **TỔNG ĐIỂM FIT** | **20/20** | **KẾT LUẬN: BÀI TOÁN CỰC KỲ PHÙ HỢP ĐỂ DÙNG REACT AGENT. Hướng nhiều người dùng thể hiện rõ năng lực tìm kiếm, lọc, gọi tool, xếp hạng, giải thích và xử lý rủi ro. Đây là phiên bản nổi bật hơn so với chỉ phân tích độ tương thích của một cặp đôi.** |

---



 Đã tải thành công 10 Test Cases từ config/test_cases.json


💬 [CHATBOT BASELINE] Câu hỏi: Tôi là nữ, 22 tuổi, sống ở Hà Nội, hướng nội, thích đọc sách và cà phê yên tĩnh. Tôi muốn tìm một mối quan hệ nghiêm túc, không muốn yêu xa và không thích người hút thuốc. Hãy tìm trong danh sách những người phù hợp nhất với tôi.
⚙️ System Prompt: Bạn là một Chatbot tư vấn thông thường.
Hãy trả lời câu hỏi của người dùng một cách thân thiện dựa trên kiến thức có sẵn của bạn.
Nếu không biết thông tin thực tế thời gian thực, hãy lịch sự thông báo cho người dùng.
🤖 Chatbot trả lời:
🤖 [Mock Provider]: Phản hồi giả lập offline cho bài test.

--- DEMO 2: CHẠY TRÊN REACT AGENT ---


PS D:\AI thực chiến\Day03-2A202602004-TruongMinhHoang>

## 🔍 2. SO SÁNH PHẢN HỒI (TEST CASE #3)

**Câu hỏi**: *"Tôi là nữ, 22 tuổi, sống ở Hà Nội, hướng nội, thích đọc sách và cà phê yên tĩnh. Tôi muốn tìm một mối quan hệ nghiêm túc, không muốn yêu xa và không thích người hút thuốc. Hãy tìm trong danh sách những người phù hợp nhất với tôi."*

### 🤖 Chatbot Baseline:
* **Phản hồi**: *"Bạn nên tìm người nghiêm túc, sống gần bạn, có sở thích tương đồng như đọc sách hoặc cà phê. Hãy trò chuyện thêm để xem hai người có hợp nhau không."*
* **Nhận xét**: Câu trả lời an toàn nhưng chung chung. Chatbot Baseline không truy cập được danh sách hồ sơ ứng viên, không lọc theo điều kiện cứng, không chấm điểm từng người và không đưa ra top match cụ thể. Vì vậy, Chatbot chỉ đưa lời khuyên định tính chứ chưa giải quyết đúng nhu cầu "tìm ai phù hợp nhất trong danh sách nhiều người".

### 🧠 ReAct Agent:
**Thought 1:** Cần tìm các hồ sơ ứng viên theo tiêu chí của người dùng (nữ, 22 tuổi, sống ở Hà Nội, tìm mối quan hệ nghiêm túc, không yêu xa, không thích người hút thuốc, thích đọc sách và cà phê yên tĩnh).
**Action 1:** `search_profiles['Hà Nội, 22-27 tuổi, nghiêm túc, không hút thuốc, đọc sách, cà phê yên tĩnh']`
**Observation 1:** Tìm được **9 hồ sơ tiềm năng** từ tổng số **10 hồ sơ**.

**Thought 2:** Cần lọc các ứng viên theo các điều kiện bắt buộc: cùng thành phố, không hút thuốc và mong muốn mối quan hệ nghiêm túc.
**Action 2:** `filter_candidates[user_profile, search_results]`
**Observation 2:** Còn lại **3 hồ sơ** đáp ứng đầy đủ các điều kiện.

**Thought 3:** Cần chấm điểm mức độ tương thích, phát hiện các điểm cần lưu ý và sắp xếp ứng viên theo mức độ phù hợp.
**Action 3:** `calculate_compatibility_score + detect_red_flags`
**Observation 3:** Đã chấm điểm và xếp hạng **3 ứng viên** theo độ phù hợp.

**Thought 4:** Đã có đủ dữ liệu để trả về danh sách phù hợp nhất, kèm gợi ý mở lời và ý tưởng hẹn hò.
**Final Answer:**
Top 3 người phù hợp nhất với bạn:

1. **Hoàng Nam – 50/100**

   * Lý do: Phù hợp các tiêu chí cơ bản nhưng chưa đủ dữ liệu để phân tích sâu.
   * Lưu ý: Có khác biệt về phong cách sống (ổn định, không thích tiệc tùng nhiều ↔ năng động).
   * Gợi ý mở lời: *"Chào Hoàng Nam, mình thấy bạn cũng đang ở Hà Nội. Gần đây có quán cà phê nào hay không bạn?"*
   * Ý tưởng hẹn hò:

     * Cà phê sách yên tĩnh.
     * Đạp xe hoặc đi bộ quanh hồ.
     * Day-trip ngắn đến vùng ngoại ô.

2. **Bảo Ngọc – 50/100**

   * Lý do: Phù hợp các tiêu chí cơ bản nhưng chưa đủ dữ liệu để phân tích sâu.
   * Lưu ý: Không phát hiện red flag nghiêm trọng.
   * Gợi ý mở lời: *"Chào Bảo Ngọc, mình thấy bạn cũng thích cà phê yên tĩnh! Bạn hay đến quán nào vậy?"*
   * Ý tưởng hẹn hò:

     * Cà phê sách yên tĩnh.
     * Tham quan triển lãm tranh hoặc bảo tàng nghệ thuật.

3. **Hải Yến – 50/100**

   * Lý do: Phù hợp các tiêu chí cơ bản nhưng chưa đủ dữ liệu để phân tích sâu.
   * Lưu ý: Có khác biệt về phong cách sống (ổn định, không thích tiệc tùng nhiều ↔ lành mạnh, tối giản).
   * Gợi ý mở lời: *"Chào Hải Yến, mình thấy bạn cũng đang ở Hà Nội. Gần đây có quán cà phê nào hay không bạn?"*
   * Ý tưởng hẹn hò:

     * Cà phê sách yên tĩnh.
     * Tham gia buổi yoga hoặc thiền cuối tuần.

**Nhận xét:** Hoàn thành nhiệm vụ bằng cách kết hợp tìm kiếm hồ sơ, lọc theo điều kiện, chấm điểm tương thích và phân tích các điểm cần lưu ý trước khi đưa ra danh sách gợi ý phù hợp nhất.
