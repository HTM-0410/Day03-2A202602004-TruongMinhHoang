"""
Data Transformer - Convert from new format to existing schema
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


def transform_candidate(candidate: dict) -> dict:
    """Transform a single candidate from new format to existing schema"""
    
    # Parse personality from list to string
    personality_list = candidate.get("personality", [])
    personality = ", ".join(personality_list) if isinstance(personality_list, list) else personality_list
    
    # Parse interests from list
    interests = candidate.get("interests", [])
    if isinstance(interests, str):
        interests = [i.strip() for i in interests.split(",")]
    
    # Map relationship_goal
    goal_mapping = {
        "nghiêm túc": "Nghiêm túc",
        "tìm hiểu": "Tìm bạn",
        "không ràng buộc": "Không rõ",
        "nghiêm túc, hướng tới hôn nhân": "Nghiêm túc",
    }
    original_goal = candidate.get("relationship_goal", "")
    relationship_goal = goal_mapping.get(original_goal.lower(), original_goal.title())
    
    # Extract lifestyle fields
    lifestyle = candidate.get("lifestyle", {})
    smoking = lifestyle.get("smoking", False)
    drinking = lifestyle.get("drinking", "Không")
    
    # Map drinking frequency
    drinking_mapping = {
        "không": "Không",
        "hiếm khi": "Hiếm khi",
        "thỉnh thoảng": "Xã giao",
        "thường xuyên": "Thường xuyên",
    }
    drinking = drinking_mapping.get(drinking.lower(), drinking)
    
    # Generate deal_breakers from important_criteria
    important_criteria = candidate.get("important_criteria", [])
    deal_breakers = []
    
    for criteria in important_criteria:
        criteria_lower = criteria.lower()
        if "không hút thuốc" in criteria_lower:
            deal_breakers.append("Hút thuốc")
        if "yêu xa" in criteria_lower or "long distance" in criteria_lower:
            deal_breakers.append("Yêu xa")
        if "chung thủy" in criteria_lower:
            deal_breakers.append("Không chung thủy")
    
    # Add default deal breakers if none
    if not deal_breakers:
        deal_breakers = ["Hút thuốc", "Không chung thủy"]
    
    # Build transformed candidate
    transformed = {
        "id": candidate.get("id"),
        "name": candidate.get("name"),
        "age": candidate.get("age"),
        "gender": candidate.get("gender", "").capitalize(),  # nam -> Nam, nữ -> Nữ
        "location": candidate.get("location", ""),
        "personality": personality,
        "interests": interests,
        "relationship_goal": relationship_goal,
        "lifestyle": f"{candidate.get('lifestyle', {}).get('schedule', '')}, {'Chấp nhận yêu xa' if lifestyle.get('long_distance_ok') else 'Không yêu xa'}",
        "occupation": "N/A",  # Not in source data
        "smoking": smoking,
        "drinking": drinking,
        "deal_breakers": deal_breakers,
        "bio": candidate.get("bio", ""),
        # Extra fields from new schema
        "important_criteria": candidate.get("important_criteria", []),
        "notes": candidate.get("notes", ""),
        "long_distance_ok": lifestyle.get("long_distance_ok", False)
    }
    
    return transformed


def main():
    # Paths - use raw string for Windows paths
    source_path = r"C:\Users\Admin\Downloads\candidates_dataset.json"
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_path = os.path.join(base_dir, "config", "candidate_profiles.json")
    
    # Check source exists
    if not os.path.exists(source_path):
        print(f"❌ Source file not found: {source_path}")
        return
    
    # Load source data
    with open(source_path, "r", encoding="utf-8") as f:
        source_data = json.load(f)
    
    print(f"📥 Loaded {len(source_data)} candidates from source")
    
    # Transform all candidates
    transformed_data = []
    for candidate in source_data:
        transformed = transform_candidate(candidate)
        transformed_data.append(transformed)
    
    # Save to target
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(transformed_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Saved {len(transformed_data)} candidates to target")
    
    # Print summary
    print("\n📊 Transformation Summary:")
    print(f"   - Total candidates: {len(transformed_data)}")
    
    # Gender distribution
    genders = {}
    for c in transformed_data:
        g = c.get("gender", "Unknown")
        genders[g] = genders.get(g, 0) + 1
    print(f"   - Gender: {dict(genders)}")
    
    # Smoking distribution
    smokers = sum(1 for c in transformed_data if c.get("smoking"))
    print(f"   - Smokers: {smokers}/{len(transformed_data)}")
    
    # Relationship goals
    goals = {}
    for c in transformed_data:
        g = c.get("relationship_goal", "Unknown")
        goals[g] = goals.get(g, 0) + 1
    print(f"   - Goals: {dict(goals)}")
    
    # Locations
    locations = {}
    for c in transformed_data:
        loc = c.get("location", "Unknown")
        locations[loc] = locations.get(loc, 0) + 1
    print(f"   - Locations: {dict(locations)}")
    
    print("\n🎉 Transformation complete!")


if __name__ == "__main__":
    main()
