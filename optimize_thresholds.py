"""Find optimal thresholds by brute-force search over the judge data"""
import csv
from cognitive import analyze_prompt
from complexity_score import cora_complexity_score

with open("judge_results.csv", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

TIER_ORDER = ["Tier 0", "Tier 1", "Tier 2", "Tier 3", "Tier 4"]

# Pre-compute scores for each prompt using the newly updated ALPHA values
scored = []
for r in rows:
    profile = analyze_prompt(r["prompt"])
    raw_score = cora_complexity_score(profile, r["prompt"])
    word_count = len(r["prompt"].split())
    
    # Apply the length boost
    boosted = raw_score
    if raw_score > 0 and word_count >= 20:
        boosted += 0.04
    
    # We will simulate different floor values
    scored.append({
        "raw_score": raw_score,
        "boosted_score": boosted,
        "word_count": word_count,
        "gt": r["ground_truth_tier"],
        "prompt": r["prompt"][:60],
    })

best = None
best_metrics = None

# Try different threshold combinations (expanded range because scores shifted)
for t0 in [x/100 for x in range(2, 25, 2)]:       # Tier 0/1
    for t1 in [x/100 for x in range(15, 45, 2)]:   # Tier 1/2
        if t1 <= t0: continue
        for t2 in [x/100 for x in range(35, 75, 2)]:   # Tier 2/3
            if t2 <= t1: continue
            for t3 in [x/100 for x in range(60, 110, 5)]:   # Tier 3/4
                if t3 <= t2: continue
                for floor in [0.0, t0]:  # try no floor vs floor at t0
                    thresholds = [t0, t1, t2, t3]
                    
                    correct = 0
                    under = 0
                    over = 0
                    within1 = 0
                    
                    for s in scored:
                        score = s["boosted_score"]
                        if score == 0.0 and s["word_count"] >= 6:
                            score = floor if floor > 0 else 0.0
                        
                        tier_idx = sum(1 for t in thresholds if score >= t)
                        tier_idx = max(0, min(4, tier_idx))
                        new_tier = f"Tier {tier_idx}"
                        
                        gt = s["gt"]
                        new_idx = tier_idx
                        gt_idx = TIER_ORDER.index(gt)
                        
                        if new_tier == gt:
                            correct += 1
                        elif new_idx < gt_idx:
                            under += 1
                        else:
                            over += 1
                        
                        if abs(new_idx - gt_idx) <= 1:
                            within1 += 1
                    
                    n = len(scored)
                    if within1 == n:  # must maintain 100% within-1
                        # Optimize for: max exact + min under
                        score_metric = correct - under * 2
                        if best is None or score_metric > best:
                            best = score_metric
                            best_metrics = {
                                "thresholds": thresholds,
                                "floor": floor,
                                "exact": correct/n*100,
                                "within1": within1/n*100,
                                "under": under/n*100,
                                "over": over/n*100,
                            }

if best_metrics:
    print("=== OPTIMAL THRESHOLDS (maintaining 100% within-1) ===")
    print(f"  Thresholds: {best_metrics['thresholds']}")
    print(f"  Floor: {best_metrics['floor']}")
    print(f"  Exact accuracy:  {best_metrics['exact']:5.1f}%")
    print(f"  Within-1:        {best_metrics['within1']:5.1f}%")
    print(f"  Under-routing:   {best_metrics['under']:5.1f}%")
    print(f"  Over-routing:    {best_metrics['over']:5.1f}%")
else:
    print("No combination maintains 100% within-1 accuracy!")
