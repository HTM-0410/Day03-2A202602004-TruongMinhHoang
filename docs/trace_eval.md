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

**Câu hỏi**: *"Thời tiết ở Hà Nội hôm nay thế nào và tôi nên mặc gì đi chơi?"*

### 🤖 Chatbot Baseline:
* **Phản hồi**: *"Tôi không có truy cập Internet thời gian thực nên không biết thời tiết hôm nay ở Hà Nội."*
* **Nhận xét**: An toàn nhưng không giải quyết được nhu cầu thực tế của người dùng.

### 🧠 ReAct Agent:
* **Thought 1**: Cần tra cứu thời tiết Hà Nội.
* **Action 1**: `get_weather['Hà Nội']`
* **Observation 1**: `Thời tiết Hà Nội: 28°C, Nắng nhẹ, Độ ẩm 65%.`
* **Thought 2**: Đã có thông tin 28°C nắng nhẹ, đưa ra lời khuyên trang phục.
* **Final Answer**: *"Thời tiết Hà Nội hôm nay 28°C, nắng nhẹ. Bạn nên mặc quần áo thoáng mát!"*
* **Nhận xét**: Hoàn thành xuất sắc nhiệm vụ nhờ sự kết hợp giữa suy luận và công cụ.
