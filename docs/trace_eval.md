# Cupid Agent - Lab Trace & Evaluation (Mốc 1)

## Mốc 1: Định hình & Scoring Matrix

### 1. Agentic Fit Scoring Matrix (Role 5)

| Tiêu chí Agentic Fit | Mức đánh giá | Phân tích chi tiết cho bài toán Cupid Agent |
| :--- | :---: | :--- |
| **Planning Complexity** | **Cao** | Agent cần lập kế hoạch qua nhiều bước suy luận: nhận diện yêu cầu -> lọc ứng viên trùng điều kiện cứng -> chấm điểm tương thích 6 chiều -> xếp hạng top matches -> tạo tin nhắn mở lời & gợi ý date. |
| **Tool Dependency** | **Rất cao** | Agent không thể tự bịa thông tin hồ sơ; bắt buộc phải gọi các công cụ chuyên biệt để truy vấn bộ dữ liệu candidate, lọc deal-breakers và tính toán tương thích. |
| **State Management** | **Trung bình** | Cần lưu trữ thông tin hồ sơ người dùng hiện tại, danh sách ứng viên còn lại sau khi lọc, và bộ vết Thought-Action-Observation để chuyển qua các bước tiếp theo. |
| **Error Recovery** | **Cao** | Khi input không rõ ràng, tiêu chí tìm kiếm phi thực tế hoặc xảy ra lỗi trong tool (ví dụ: rỗng dữ liệu, yêu cầu lộ SĐT/địa chỉ riêng tư), Agent cần có khả năng xử lý lỗi an toàn và thông báo tới người dùng mà không bị crash. |

---

### 2. Danh sách 7 Tools Đề xuất (Role 2)

1. `search_profiles(criteria: str) -> list`: Tìm kiếm hồ sơ ứng viên theo tiêu chí cơ bản.
2. `filter_candidates(user_profile: dict, candidate_profiles: list) -> list`: Loại các ứng viên không đáp ứng điều kiện cứng (tuổi, vị trí, hút thuốc, yêu xa).
3. `calculate_compatibility_score(user_profile: dict, candidate_profile: dict) -> dict`: Tính điểm tương thích chi tiết (0-100) theo 6 tiêu chí.
4. `rank_matches(scored_candidates: list) -> list`: Sắp xếp danh sách ứng viên theo thứ tự điểm tương thích giảm dần.
5. `detect_red_flags(user_profile: dict, candidate_profile: dict) -> list`: Phát hiện điểm rủi ro hoặc điểm lệch giữa 2 đối tượng.
6. `suggest_opening_message(user_profile: dict, candidate_profile: dict) -> str`: Gợi ý tin nhắn mở lời tinh tế để trò chuyện trực tiếp qua tính năng nhắn tin trong ứng dụng.
7. `suggest_date_ideas(user_profile: dict, candidate_profile: dict, budget: str, location: str) -> list`: Gợi ý địa điểm và hoạt động hẹn hò phù hợp.

---

### 3. Failure Modes & Phương án Xử lý Chi tiết (Role 3 - Cập nhật Privacy Guardrail)

| STT | Tool / Kịch bản | Trường hợp thất bại (Failure Mode) | Phương án xử lý An toàn (Error Recovery & Privacy Guardrail) |
| :---: | :--- | :--- | :--- |
| **1** | `search_profiles` | Từ khóa tìm kiếm phi thực tế *(Vd: "500 tuổi ở Atlantis")* hoặc từ khóa rỗng | Tool trả về danh sách rỗng `[]`. Agent kích hoạt Guardrail thông báo phạm vi dữ liệu thực tế hiện có. |
| **2** | `filter_candidates` | Tất cả ứng viên đều bị loại bởi điều kiện cứng *(Vd: deal-breakers quá hẹp)* | Tool trả về thông báo rỗng kèm nguyên nhân chi tiết (do khoảng cách hay lối sống) để tư vấn mở rộng tiêu chí. |
| **3** | `calculate_compatibility_score` | Hồ sơ ứng viên bị thiếu một số trường thông tin *(Vd: thiếu MBTI/thói quen)* | Tự động bù điểm trung bình cho trường thiếu và ghi chú trong phần cảnh báo thay vì gây ra exception crash. |
| **4** | `rank_matches` | Input danh sách rỗng hoặc dữ liệu chấm điểm bị lỗi | Trả về danh sách rỗng kèm error message dạng string an toàn. |
| **5** | `detect_red_flags` | Yêu cầu tìm kiếm xung đột với Deal-breakers của chính User *(Vd: ghét hút thuốc nhưng đòi tìm người hút thuốc)* | Engine phát hiện xung đột trước khi gọi tool, cảnh báo Guardrail và ưu tiên tiêu chuẩn bắt buộc của người dùng. |
| **6** | `privacy_guardrail` | **Yêu cầu lấy Số điện thoại, địa chỉ nhà riêng hoặc thông tin cá nhân nhạy cảm** | **TẬN DỤNG TÍNH NĂNG NHẮN TIN NỘI BỘ TRONG ỨNG DỤNG: Hệ thống tuyệt đối KHÔNG hiển thị/cung cấp số điện thoại hoặc thông tin nhạy cảm. Mọi tương tác và trò chuyện ban đầu sẽ được thực hiện trực tiếp qua tính năng Nhắn tin trên Ứng dụng (In-App Messaging) để đảm bảo an toàn tuyệt đối.** |
| **7** | `suggest_opening_message` | Không tìm thấy sở thích chung giữa 2 người | Fallback về mẫu tin nhắn chào hỏi lịch sự dựa trên thông tin bio ứng viên để gửi qua ứng dụng. |
| **8** | `suggest_date_ideas` | Không xác định được vị trí địa lý hoặc ngân sách | Tự động áp dụng giá trị mặc định (Hà Nội, ngân sách vừa phải) và đưa ra các địa điểm công cộng phổ biến. |
| **9** | `max_iterations_guardrail` | Chuỗi suy luận ReAct lặp lại quá 5 lần | Dừng vòng lặp tại `MAX_ITERATIONS = 5` và tổng hợp kết quả tốt nhất hiện có. |

---

### 4. Kiểm tra Môi trường & Sẵn sàng (Role 4)
- Bảng Scoring Matrix và Failure Modes đã cập nhật hoàn tất theo quy tắc Nhắn tin trực tiếp qua Ứng dụng (In-App Messaging) trong `docs/trace_eval.md`.
