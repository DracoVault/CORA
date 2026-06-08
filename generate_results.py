import csv
import json
from cognitive import analyze_prompt
from complexity_score import score_to_tier, get_score_breakdown

with open("alpaca_data.json", encoding="utf-8") as f:
    data = json.load(f)

results = []
for item in data[:300]:
    prompt = item["instruction"]
    profile = analyze_prompt(prompt)
    tier, score, budget = score_to_tier(profile, prompt)
    results.append({
        "prompt": prompt[:100].replace('\n', ' '),
        "task_type": profile.task_type.value,
        "tier": tier,
        "score": round(score, 3),
        "budget": budget,
        "reasoning": profile.reasoning_depth,
        "domain": profile.domain_specificity,
        "code": profile.code_complexity,
    })

with open("calibration_results.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

print("Done — check calibration_results.csv")
