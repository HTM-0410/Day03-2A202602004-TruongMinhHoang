# MÔ TẢ BÀI TOÁN

## 1. Tên đề tài

**Cupid Agent: Trợ lý tìm kiếm, phân tích độ tương thích và gợi ý đối tượng hẹn hò phù hợp**

---

## 2. Bối cảnh bài toán

Trong các ứng dụng hẹn hò hoặc nền tảng kết nối xã hội, người dùng thường phải tự đọc nhiều hồ sơ khác nhau để tìm người phù hợp. Việc này tốn thời gian và dễ bị ảnh hưởng bởi cảm tính, ví dụ chỉ dựa vào ảnh đại diện, vài sở thích bề mặt hoặc mô tả ngắn trong hồ sơ.

Bên cạnh đó, việc xác định một người có phù hợp hay không không chỉ phụ thuộc vào sở thích giống nhau. Một mối quan hệ còn liên quan đến nhiều yếu tố khác như tính cách, mục tiêu quan hệ, phong cách sống, thói quen giao tiếp, vị trí địa lý, độ tuổi, giá trị cá nhân và các tiêu chí không thể thỏa hiệp của mỗi người.

Vì vậy, nhóm lựa chọn xây dựng **Cupid Agent** - một trợ lý AI có khả năng phân tích hồ sơ người dùng, tìm kiếm các hồ sơ ứng viên phù hợp, chấm điểm tương thích, xếp hạng top match và đưa ra lời giải thích rõ ràng.

---

## 3. Vấn đề cần giải quyết

Người dùng cần một hệ thống hỗ trợ trả lời câu hỏi:

> "Trong danh sách nhiều người dùng khác nhau, ai là người phù hợp nhất với tôi và vì sao?"

Hệ thống cần giải quyết các vấn đề cụ thể:

- Hiểu hồ sơ cá nhân của người dùng hiện tại.
- Hiểu tiêu chí tìm kiếm đối tượng phù hợp.
- Lọc các ứng viên không đáp ứng điều kiện cơ bản.
- So sánh người dùng với từng ứng viên.
- Chấm điểm tương thích dựa trên nhiều tiêu chí.
- Xếp hạng các ứng viên phù hợp nhất.
- Giải thích lý do vì sao một ứng viên được đề xuất.
- Cảnh báo các điểm lệch hoặc rủi ro trong mối quan hệ.
- Gợi ý cách mở lời hoặc ý tưởng đi date phù hợp.

---

## 4. Người dùng mục tiêu

Người dùng mục tiêu là những người muốn tìm kiếm một mối quan hệ phù hợp nhưng không muốn tự phân tích quá nhiều hồ sơ thủ công.

Ví dụ:

- Sinh viên muốn tìm người có cùng lối sống và sở thích.
- Người đi làm muốn tìm mối quan hệ nghiêm túc.
- Người mới tham gia ứng dụng hẹn hò muốn được hỗ trợ chọn đối tượng phù hợp.
- Người cần lời khuyên khách quan trước khi bắt đầu trò chuyện hoặc hẹn gặp.

---

## 5. Input đầu vào

Hệ thống nhận các thông tin sau:

### Hồ sơ người dùng hiện tại

Ví dụ:

```text
Tôi là nữ, 22 tuổi, sống ở Hà Nội.
Tôi hướng nội, thích đọc sách, cà phê yên tĩnh và nói chuyện sâu.
Tôi muốn tìm một mối quan hệ nghiêm túc.
Tôi không thích người hút thuốc và không muốn yêu xa.
```

### Tiêu chí tìm kiếm

Ví dụ:

```text
Tìm người từ 22-27 tuổi, sống ở Hà Nội, không hút thuốc,
có mục tiêu quan hệ nghiêm túc, thích hoạt động nhẹ nhàng.
```

### Danh sách hồ sơ ứng viên

Trong phạm vi bài lab, danh sách ứng viên có thể là dữ liệu mẫu trong file JSON, gồm khoảng 8-10 hồ sơ.

Mỗi hồ sơ có thể gồm:

- Tên
- Tuổi
- Vị trí
- Sở thích
- Tính cách
- Mục tiêu quan hệ
- Thói quen sống
- Tiêu chí quan trọng
- Các điểm cần lưu ý

---

## 6. Output mong muốn

Cupid Agent trả về danh sách ứng viên phù hợp nhất, ví dụ top 3:

```text
Top 3 đối tượng phù hợp:

1. Minh Anh - 86/100
Lý do phù hợp:
- Cùng sống ở Hà Nội.
- Cùng muốn mối quan hệ nghiêm túc.
- Cùng thích cà phê yên tĩnh và trò chuyện sâu.
- Phong cách sống ổn định, phù hợp với người hướng nội.

Điểm cần lưu ý:
- Minh Anh khá bận vào cuối tuần, nên cần hẹn lịch trước.

Gợi ý mở lời:
"Mình thấy bạn cũng thích cà phê sách. Cuối tuần bạn hay đọc thể loại gì?"

2. Hoàng Nam - 78/100
...
```

Ngoài kết quả xếp hạng, Agent có thể đưa ra:

- Lý do từng ứng viên phù hợp.
- Điểm mạnh của cặp đôi.
- Điểm khác biệt cần cân nhắc.
- Red flags nếu có.
- Gợi ý tin nhắn mở đầu.
- Gợi ý buổi date đầu tiên.

---

## 7. Vì sao bài toán cần ReAct Agent

Bài toán này không phù hợp nếu chỉ dùng Chatbot thông thường, vì Chatbot thường chỉ đưa ra lời khuyên chung chung và không có quy trình phân tích rõ ràng.

Cupid Agent cần thực hiện nhiều bước:

1. Phân tích hồ sơ người dùng.
2. Trích xuất tiêu chí tìm kiếm.
3. Tìm kiếm các hồ sơ ứng viên.
4. Lọc theo điều kiện cứng.
5. Chấm điểm tương thích từng ứng viên.
6. Xếp hạng kết quả.
7. Phát hiện điểm lệch hoặc rủi ro.
8. Sinh lời giải thích và gợi ý hành động tiếp theo.

Các bước này phù hợp với mô hình **ReAct Agent**, trong đó Agent suy luận theo chuỗi:

```text
Thought -> Action -> Observation -> Thought -> Final Answer
```

---

## 8. Các công cụ dự kiến

Các tool có thể xây dựng trong bài lab:

```text
search_profiles(criteria)
filter_candidates(user_profile, candidate_profiles)
calculate_compatibility_score(user_profile, candidate_profile)
rank_matches(scored_candidates)
detect_red_flags(user_profile, candidate_profile)
suggest_opening_message(user_profile, candidate_profile)
suggest_date_ideas(user_profile, candidate_profile, budget, location)
```

Ý nghĩa từng tool:

| Tool | Mục đích |
| :--- | :--- |
| `search_profiles` | Tìm hồ sơ ứng viên theo tiêu chí cơ bản. |
| `filter_candidates` | Loại các ứng viên không đáp ứng điều kiện cứng như tuổi, vị trí, hút thuốc, mục tiêu quan hệ. |
| `calculate_compatibility_score` | Tính điểm tương thích giữa người dùng và từng ứng viên. |
| `rank_matches` | Sắp xếp danh sách ứng viên theo điểm phù hợp. |
| `detect_red_flags` | Phát hiện điểm rủi ro như mục tiêu quan hệ không khớp, thiếu tôn trọng ranh giới, thói quen sống xung đột. |
| `suggest_opening_message` | Gợi ý tin nhắn mở lời dựa trên điểm chung. |
| `suggest_date_ideas` | Gợi ý hoạt động hẹn hò phù hợp với tính cách, sở thích, ngân sách và vị trí. |

---

## 9. Luồng xử lý mẫu

Ví dụ người dùng hỏi:

```text
Tôi là người hướng nội, thích đọc sách, muốn mối quan hệ nghiêm túc.
Hãy tìm trong danh sách những người phù hợp nhất với tôi.
```

Luồng ReAct Agent:

```text
Thought: Cần phân tích hồ sơ và tiêu chí tìm kiếm của người dùng.
Action: search_profiles["nghiêm túc, hướng nội hoặc tôn trọng không gian riêng, thích hoạt động nhẹ nhàng"]

Observation: Tìm được 5 hồ sơ tiềm năng.

Thought: Cần lọc ứng viên theo điều kiện cứng.
Action: filter_candidates[user_profile, candidate_profiles]

Observation: Còn lại 3 hồ sơ phù hợp.

Thought: Cần chấm điểm tương thích cho từng hồ sơ.
Action: calculate_compatibility_score[user_profile, top_candidates]

Observation: Minh Anh 86/100, Hoàng Nam 78/100, Gia Huy 71/100.

Thought: Đã có đủ thông tin để xếp hạng và giải thích.
Final Answer: Top 3 người phù hợp nhất là...
```

---

## 10. Guardrails cần có

Vì đây là bài toán liên quan đến con người và quan hệ cá nhân, Agent cần có các phanh an toàn:

- Không đưa ra kết luận tuyệt đối như "hai người chắc chắn sẽ yêu nhau".
- Không đánh giá ngoại hình, giới tính, xuất thân hoặc hoàn cảnh cá nhân theo hướng kỳ thị.
- Không khuyến khích theo dõi, ép buộc hoặc thao túng cảm xúc người khác.
- Khi dữ liệu thiếu, cần hỏi thêm thay vì tự bịa thông tin.
- Nếu phát hiện dấu hiệu không an toàn, cần khuyên người dùng giữ ranh giới và cân nhắc kỹ.
- Nếu quá số vòng lặp, Agent phải dừng và trả lời lịch sự.

---

## 11. Phạm vi MVP cho bài lab

Để phù hợp thời gian bài lab, nhóm nên triển khai phiên bản MVP:

- Có một file dữ liệu mẫu gồm 8-10 hồ sơ ứng viên.
- Người dùng nhập hồ sơ và tiêu chí tìm kiếm.
- Agent lọc ứng viên theo điều kiện cơ bản.
- Agent tính điểm tương thích.
- Agent trả về top 3 người phù hợp nhất.
- Agent giải thích lý do đề xuất.
- Agent gợi ý một tin nhắn mở lời hoặc một ý tưởng đi date.

Các phần nâng cao có thể làm sau:

- Tích hợp lịch để kiểm tra thời gian rảnh.
- Tích hợp bản đồ để tìm địa điểm đi date.
- Thêm memory để ghi nhớ gu của người dùng.
- Cho phép người dùng phản hồi để Agent cải thiện đề xuất.

---

## 12. Đánh giá độ khả thi

| Tiêu chí | Mức đánh giá | Giải thích |
| :--- | :---: | :--- |
| Dữ liệu đầu vào | Cao | Có thể dùng dữ liệu mẫu tự tạo, không phụ thuộc API bên ngoài. |
| Độ phức tạp kỹ thuật | Trung bình | Cần viết logic lọc, chấm điểm và xếp hạng, nhưng có thể làm bằng Python cơ bản. |
| Độ phù hợp với ReAct Agent | Rất cao | Bài toán có nhiều bước, nhiều tool, cần quan sát kết quả từng bước. |
| Khả năng demo | Cao | Có thể demo bằng một câu hỏi và danh sách hồ sơ mẫu. |
| Rủi ro | Trung bình | Cần guardrails để tránh kết luận cảm tính, thiên vị hoặc lời khuyên không phù hợp. |

**Kết luận**: Bài toán này rất khả thi trong phạm vi bài lab. Hướng nhiều người dùng giúp đề tài nổi bật hơn so với chỉ phân tích một cặp đôi, vì thể hiện rõ khả năng tìm kiếm, lọc, xếp hạng và giải thích của ReAct Agent.
