import logging
import time
from collections import defaultdict

from flask import Blueprint, jsonify, render_template, request

from .generator import generate_demo_plan, generate_meal_plan, regenerate_meal, swap_ingredient_in_meal
from .models import load_plan
from .scheduler import scheduler

# Simple in-process rate limiter: max 5 calls per IP per hour
_demo_calls: dict[str, list[float]] = defaultdict(list)
_DEMO_LIMIT = 5
_DEMO_WINDOW = 3600  # seconds

log = logging.getLogger("meal-planner")

bp = Blueprint("main", __name__)


def _normalize_ingredients(raw) -> dict:
    if isinstance(raw, dict):
        return raw
    return {"Other": raw or []}


@bp.route("/")
def index():
    data = load_plan()
    all_ingredients = _normalize_ingredients(data.get("all_ingredients"))
    return render_template(
        "index.html",
        week_of=data.get("week_of", "—"),
        cuisine_theme=data.get("cuisine_theme", ""),
        meals=data.get("meals", []),
        snacks=data.get("snacks", []),
        all_ingredients=all_ingredients,
    )


@bp.route("/generate", methods=["POST"])
def generate():
    """Manually trigger a new meal plan generation."""
    try:
        plan = generate_meal_plan()
        return jsonify({"status": "ok", "week_of": plan.get("week_of")})
    except Exception as e:
        log.error(f"generate failed: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@bp.route("/regenerate", methods=["POST"])
def regenerate():
    body = request.get_json()
    meal_index = body.get("meal_index")
    disliked = body.get("disliked", "").strip()

    try:
        new_meal = regenerate_meal(meal_index, disliked)
        return jsonify(new_meal)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        log.error(f"regenerate failed: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@bp.route("/swap-ingredient", methods=["POST"])
def swap_ingredient():
    body = request.get_json()
    meal_index = body.get("meal_index")
    ingredient = (body.get("ingredient") or "").strip()

    if not ingredient:
        return jsonify({"error": "No ingredient specified"}), 400

    try:
        updated_meal = swap_ingredient_in_meal(meal_index, ingredient)
        return jsonify(updated_meal)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        log.error(f"swap-ingredient failed: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@bp.route("/plan")
def get_plan():
    return jsonify(load_plan())


@bp.route("/demo")
def demo():
    return render_template("demo.html")


@bp.route("/demo/generate", methods=["POST"])
def demo_generate():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "unknown").split(",")[0].strip()
    now = time.time()
    window_start = now - _DEMO_WINDOW
    _demo_calls[ip] = [t for t in _demo_calls[ip] if t > window_start]

    if len(_demo_calls[ip]) >= _DEMO_LIMIT:
        retry_after = int(_demo_calls[ip][0] + _DEMO_WINDOW - now) + 1
        return jsonify({"error": f"Rate limit reached. Try again in {retry_after // 60} minutes."}), 429

    _demo_calls[ip].append(now)

    try:
        plan = generate_demo_plan()
        return jsonify(plan)
    except Exception as e:
        log.error(f"demo generate failed: {e}", exc_info=True)
        return jsonify({"error": "Generation failed. Please try again."}), 500


@bp.route("/health")
def health():
    return jsonify({"status": "ok", "jobs": [str(j) for j in scheduler.get_jobs()]})
