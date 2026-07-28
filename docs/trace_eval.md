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

## 🔍 2. SO SÁNH PHẢN HỒI (TEST CASE #3)

**Câu hỏi**: *"Tôi là nữ, 22 tuổi, sống ở Hà Nội, hướng nội, thích đọc sách và cà phê yên tĩnh. Tôi muốn tìm một mối quan hệ nghiêm túc, không muốn yêu xa và không thích người hút thuốc. Hãy tìm trong danh sách những người phù hợp nhất với tôi."*

### 🤖 Chatbot Baseline:
* **Phản hồi dự kiến**: *"Bạn nên tìm người nghiêm túc, sống gần bạn, có sở thích tương đồng như đọc sách hoặc cà phê. Hãy trò chuyện thêm để xem hai người có hợp nhau không."*
* **Nhận xét**: Câu trả lời an toàn nhưng chung chung. Chatbot Baseline không truy cập được danh sách hồ sơ ứng viên, không lọc theo điều kiện cứng, không chấm điểm từng người và không đưa ra top match cụ thể. Vì vậy, Chatbot chỉ đưa lời khuyên định tính chứ chưa giải quyết đúng nhu cầu "tìm ai phù hợp nhất trong danh sách nhiều người".

### 🧠 ReAct Agent:
* **Thought 1**: Cần trích xuất tiêu chí tìm kiếm từ hồ sơ người dùng: nữ 22 tuổi, Hà Nội, hướng nội, thích đọc sách/cà phê yên tĩnh, muốn quan hệ nghiêm túc, không yêu xa, không hút thuốc.
* **Action 1**: `search_profiles["Hà Nội, 22-27 tuổi, quan hệ nghiêm túc, không hút thuốc, thích hoạt động nhẹ nhàng"]`
* **Observation 1**: `Tìm được 5 hồ sơ tiềm năng: Minh Anh, Hoàng Nam, Gia Huy, Tuấn Kiệt, Đức Minh.`
* **Thought 2**: Cần lọc theo điều kiện cứng: cùng thành phố, không hút thuốc, mục tiêu quan hệ nghiêm túc.
* **Action 2**: `filter_candidates["same_city=Hà Nội, non_smoker=true, relationship_goal=serious"]`
* **Observation 2**: `Còn lại 3 hồ sơ: Minh Anh, Hoàng Nam, Gia Huy. Loại Tuấn Kiệt vì hút thuốc. Loại Đức Minh vì muốn quan hệ casual.`
* **Thought 3**: Cần chấm điểm tương thích cho 3 hồ sơ còn lại và xếp hạng.
* **Action 3**: `calculate_compatibility_score["user_profile", "Minh Anh, Hoàng Nam, Gia Huy"]`
* **Observation 3**: `Minh Anh: 88/100; Hoàng Nam: 79/100; Gia Huy: 72/100. Minh Anh hợp nhất vì cùng thích đọc sách, cà phê yên tĩnh, nghiêm túc và tôn trọng không gian riêng.`
* **Thought 4**: Đã có đủ dữ liệu để trả lời top match, giải thích lý do và gợi ý mở lời.
* **Final Answer**: *"Top phù hợp nhất là Minh Anh với 88/100 vì cùng sống ở Hà Nội, cùng muốn mối quan hệ nghiêm túc, cùng thích đọc sách và cà phê yên tĩnh. Hoàng Nam đứng thứ hai với 79/100 vì có mục tiêu nghiêm túc và lối sống ổn định, nhưng sở thích xã hội nhiều hơn bạn một chút. Gia Huy đạt 72/100, phù hợp ở mục tiêu quan hệ nhưng cần cân nhắc vì lịch sinh hoạt khá bận. Mình gợi ý bạn mở lời với Minh Anh bằng câu: 'Mình thấy bạn cũng thích cà phê sách. Cuối tuần bạn hay đọc thể loại gì?'"*
* **Nhận xét**: ReAct Agent xử lý tốt hơn vì có thể thao tác trực tiếp trên danh sách hồ sơ: tìm kiếm, lọc điều kiện cứng, chấm điểm, xếp hạng và giải thích. Kết quả cụ thể hơn, có căn cứ hơn và phù hợp đúng nhu cầu tìm đối tượng trong nhiều người dùng.
