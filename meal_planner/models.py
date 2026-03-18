import json

from .config import MEAL_PLAN_FILE, PLACEHOLDER


def load_plan():
    if MEAL_PLAN_FILE.exists():
        with open(MEAL_PLAN_FILE) as f:
            return json.load(f)
    return PLACEHOLDER


def save_plan(plan):
    MEAL_PLAN_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(MEAL_PLAN_FILE, "w") as f:
        json.dump(plan, f, indent=2)


def rebuild_all_ingredients(meals):
    """Deduplicate and consolidate ingredients across all meals."""
    seen = {}
    for meal in meals:
        for ing in meal.get("ingredients", []):
            key = ing.lower().split("x")[0].split("×")[0].strip()
            if key not in seen:
                seen[key] = ing
    return list(seen.values())


def parse_ai_json(raw: str) -> dict:
    """Strip markdown fences from AI response and parse JSON."""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())
