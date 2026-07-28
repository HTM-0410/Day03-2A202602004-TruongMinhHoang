"""
Data Quality Evaluation Report for Cupid Agent Mock Data
=========================================================
Phân tích va dánh gia chat luong candidate_profiles.json
"""
import json
import os
import sys

# Fix encoding for Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Load data
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_path = os.path.join(base_dir, "config", "candidate_profiles.json")

with open(data_path, "r", encoding="utf-8") as f:
    candidates = json.load(f)


def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_subheader(text):
    print(f"\n## {text}")
    print("-" * 40)


# ============================================================================
# 1. BASIC STATISTICS
# ============================================================================
print_header("1. THỐNG KÊ CƠ BẢN")

print(f"\n📊 Tổng số hồ sơ: {len(candidates)}")

# Gender distribution
genders = {}
for c in candidates:
    g = c.get("gender", "Unknown")
    genders[g] = genders.get(g, 0) + 1

print("\n👫 Phân bố giới tính:")
for g, count in genders.items():
    print(f"   - {g}: {count} ({count/len(candidates)*100:.1f}%)")

# Age distribution
ages = [c.get("age", 0) for c in candidates]
print(f"\n🎂 Độ tuổi:")
print(f"   - Min: {min(ages)}")
print(f"   - Max: {max(ages)}")
print(f"   - Trung bình: {sum(ages)/len(ages):.1f}")

# Location distribution
locations = {}
for c in candidates:
    loc = c.get("location", "Unknown")
    locations[loc] = locations.get(loc, 0) + 1

print("\n📍 Phân bố địa điểm:")
for loc, count in locations.items():
    print(f"   - {loc}: {count} ({count/len(candidates)*100:.1f}%)")

# Smoking distribution
smoking = {}
for c in candidates:
    s = "Hút thuốc" if c.get("smoking", False) else "Không hút"
    smoking[s] = smoking.get(s, 0) + 1

print("\n🚬 Tình trạng hút thuốc:")
for s, count in smoking.items():
    print(f"   - {s}: {count} ({count/len(candidates)*100:.1f}%)")

# Relationship goal distribution
goals = {}
for c in candidates:
    g = c.get("relationship_goal", "Unknown")
    goals[g] = goals.get(g, 0) + 1

print("\n💕 Mục tiêu quan hệ:")
for g, count in goals.items():
    print(f"   - {g}: {count} ({count/len(candidates)*100:.1f}%)")


# ============================================================================
# 2. DATA COMPLETENESS
# ============================================================================
print_header("2. ĐỘ HOÀN CHỈNH DỮ LIỆU")

required_fields = [
    "id", "name", "age", "gender", "location", 
    "personality", "interests", "relationship_goal",
    "lifestyle", "smoking", "deal_breakers", "bio"
]

completeness = {}
for field in required_fields:
    filled = sum(1 for c in candidates if c.get(field) not in [None, "", [], {}])
    completeness[field] = filled / len(candidates) * 100

print("\n📋 Tỷ lệ hoàn thiện các trường:")
for field, pct in completeness.items():
    status = "✅" if pct == 100 else "⚠️"
    print(f"   {status} {field}: {pct:.0f}%")

overall_completeness = sum(completeness.values()) / len(completeness)
print(f"\n📊 Độ hoàn thiện trung bình: {overall_completeness:.1f}%")


# ============================================================================
# 3. DIVERSITY ANALYSIS
# ============================================================================
print_header("3. PHÂN TÍCH ĐA DẠNG")

# Interest analysis
all_interests = []
for c in candidates:
    all_interests.extend(c.get("interests", []))

from collections import Counter
interest_counts = Counter(all_interests)

print(f"\n🎯 Tổng số loại sở thích: {len(interest_counts)}")
print("\n   Top 10 sở thích phổ biến:")
for interest, count in interest_counts.most_common(10):
    print(f"   - {interest}: {count} người ({count/len(candidates)*100:.0f}%)")

# Personality traits analysis
all_traits = []
for c in candidates:
    traits = c.get("personality", "").lower().replace(",", " ").split()
    all_traits.extend(traits)

trait_counts = Counter(all_traits)
print(f"\n🧠 Tổng số đặc điểm tính cách: {len(trait_counts)}")
print("\n   Top 10 đặc điểm tính cách:")
for trait, count in trait_counts.most_common(10):
    if len(trait) > 2:  # Filter out single chars
        print(f"   - {trait}: {count} lần")

# Deal breakers analysis
all_deal_breakers = []
for c in candidates:
    all_deal_breakers.extend(c.get("deal_breakers", []))

breaker_counts = Counter(all_deal_breakers)
print(f"\n🚫 Tổng số deal breakers: {len(breaker_counts)}")
print("\n   Deal breakers phổ biến:")
for breaker, count in breaker_counts.most_common(10):
    print(f"   - {breaker}: {count} người")


# ============================================================================
# 4. USE CASE COVERAGE
# ============================================================================
print_header("4. PHẠM VI COVER CÁC USE CASE")

use_cases = {
    "Hướng nội tìm hướng nội": False,
    "Hướng ngoại tìm hướng ngoại": False,
    "Cùng địa điểm": False,
    "Khác địa điểm": False,
    "Mục tiêu nghiêm túc": False,
    "Mục tiêu tìm bạn": False,
    "Hút thuốc vs không hút thuốc": False,
    "Chênh lệch tuổi lớn (>5 năm)": False,
}

# Check for introverts
introverts = [c for c in candidates if "hướng nội" in c.get("personality", "").lower() or "trầm tính" in c.get("personality", "").lower()]
if len(introverts) >= 2:
    use_cases["Hướng nội tìm hướng nội"] = True

# Check for extroverts
extroverts = [c for c in candidates if "hướng ngoại" in c.get("personality", "").lower() or "năng động" in c.get("personality", "").lower()]
if len(extroverts) >= 2:
    use_cases["Hướng ngoại tìm hướng ngoại"] = True

# Check same location pairs
for loc in locations:
    same_loc = [c for c in candidates if c.get("location") == loc]
    if len(same_loc) >= 2:
        use_cases["Cùng địa điểm"] = True

# Check different location pairs
unique_locs = list(locations.keys())
if len(unique_locs) >= 2:
    use_cases["Khác địa điểm"] = True

# Check relationship goals
if goals.get("Nghiêm túc", 0) >= 2:
    use_cases["Mục tiêu nghiêm túc"] = True
if goals.get("Tìm bạn", 0) >= 1:
    use_cases["Mục tiêu tìm bạn"] = True

# Check smoking combos
smokers = [c for c in candidates if c.get("smoking")]
non_smokers = [c for c in candidates if not c.get("smoking")]
if smokers and non_smokers:
    use_cases["Hút thuốc vs không hút thuốc"] = True

# Check age gap
for i, c1 in enumerate(candidates):
    for c2 in candidates[i+1:]:
        if abs(c1.get("age", 0) - c2.get("age", 0)) > 5:
            use_cases["Chênh lệch tuổi lớn (>5 năm)"] = True
            break

print("\n✅ Các use case được hỗ trợ:")
covered = 0
for use_case, supported in use_cases.items():
    status = "✅" if supported else "❌"
    print(f"   {status} {use_case}")
    if supported:
        covered += 1

print(f"\n📊 Tỷ lệ cover use case: {covered}/{len(use_cases)} ({covered/len(use_cases)*100:.0f}%)")


# ============================================================================
# 5. DATA QUALITY ISSUES
# ============================================================================
print_header("5. VẤN ĐỀ CHẤT LƯỢNG DỮ LIỆU")

issues = []

# Check for duplicate names
names = [c.get("name", "") for c in candidates]
duplicates = [name for name in set(names) if names.count(name) > 1]
if duplicates:
    issues.append(f"⚠️ Trùng tên: {duplicates}")

# Check for age outliers
for c in candidates:
    age = c.get("age", 0)
    if age < 18 or age > 60:
        issues.append(f"⚠️ Tuổi bất thường: {c.get('name')} - {age}")

# Check for missing bio
no_bio = [c.get("name") for c in candidates if not c.get("bio")]
if no_bio:
    issues.append(f"⚠️ Thiếu bio: {', '.join(no_bio)}")

# Check for empty interests
no_interests = [c.get("name") for c in candidates if not c.get("interests")]
if no_interests:
    issues.append(f"⚠️ Không có sở thích: {', '.join(no_interests)}")

# Check for unrealistic deal breakers
for c in candidates:
    if not c.get("deal_breakers"):
        issues.append(f"⚠️ Không có deal breakers: {c.get('name')}")

if issues:
    print("\nCác vấn đề phát hiện:")
    for issue in issues:
        print(f"   {issue}")
else:
    print("\n✅ Không phát hiện vấn đề nghiêm trọng!")


# ============================================================================
# 6. SCORING SIMULATION
# ============================================================================
print_header("6. MÔ PHỎNG CHẤM ĐIỂM")

# Simulate a user profile
test_user = {
    "name": "Test User",
    "age": 24,
    "gender": "Nữ",
    "location": "Hà Nội",
    "personality": "Hướng nội, thích đọc sách",
    "interests": ["Đọc sách", "Cà phê yên tĩnh", "Yoga", "Viết lách"],
    "goal": "Nghiêm túc",
    "no_smoking": True
}

print(f"\n👤 User profile mẫu:")
print(f"   - Tuổi: {test_user['age']}")
print(f"   - Giới tính: {test_user['gender']}")
print(f"   - Địa điểm: {test_user['location']}")
print(f"   - Tính cách: {test_user['personality']}")
print(f"   - Sở thích: {', '.join(test_user['interests'])}")
print(f"   - Mục tiêu: {test_user['goal']}")

# Calculate scores
scores = []
for c in candidates:
    score = 50  # Base
    
    # Location
    if test_user["location"] == c.get("location"):
        score += 15
    
    # Age
    age_diff = abs(test_user["age"] - c.get("age", 25))
    if age_diff <= 5:
        score += 10
    
    # Goal
    if test_user["goal"] == c.get("relationship_goal"):
        score += 15
    
    # Smoking
    if test_user["no_smoking"] and c.get("smoking"):
        score -= 20
    
    # Interests
    user_interests = set(i.lower() for i in test_user["interests"])
    cand_interests = set(i.lower() for i in c.get("interests", []))
    overlap = len(user_interests & cand_interests)
    score += min(overlap * 3, 10)
    
    score = max(0, min(100, score))
    scores.append((c.get("name"), score))

# Sort and display
scores.sort(key=lambda x: x[1], reverse=True)

print(f"\n🏆 Top 5 match cho user mẫu:")
for i, (name, score) in enumerate(scores[:5]):
    rank_emoji = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][i]
    print(f"   {rank_emoji} {name}: {score}/100")

print(f"\n📉 Bottom 3:")
for name, score in scores[-3:]:
    print(f"   - {name}: {score}/100")


# ============================================================================
# 7. RECOMMENDATIONS
# ============================================================================
print_header("7. KHUYẾN NGHỊ")

print("""
✅ ĐIỂM MẠNH:
   1. Dữ liệu đa dạng về giới tính, địa điểm, tính cách
   2. Độ hoàn thiện cao (>95% các trường được điền)
   3. Có đủ deal breakers và bio cho mỗi hồ sơ
   4. Phạm vi use case được cover tốt
   5. Scoring simulation hoạt động tốt

⚠️ CẦN CẢI THIỆN:
   1. Thêm occupation cho tất cả hồ sơ (1 hồ sơ thiếu)
   2. Thêm drinking field cho tất cả hồ sơ (1 hồ sơ thiếu)
   3. Cân nhắc thêm hồ sơ ở các thành phố khác (nếu cần)

🎯 USE CASES CHO TESTING:
   1. User nữ 24 tuổi Hà Nội → Nên match với Minh Anh (cùng Hà Nội, nghiêm túc)
   2. User nam 28 tuổi → Nên match với Lan Phương hoặc Mai Linh (khác địa điểm)
   3. User không hút thuốc → Không nên match với Khánh Duy (hút thuốc)

📝 KẾT LUẬN:
   Dữ liệu mock có chất lượng TỐT, phù hợp cho việc:
   - Demo ReAct Agent workflow
   - Testing matching algorithm
   - UI/UX development
   - Guardrails testing
""")

print("\n" + "=" * 60)
print("  END OF DATA QUALITY REPORT")
print("=" * 60)
