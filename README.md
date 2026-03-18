# Meal Planner 🍽️

An AI-powered weekly meal planner that generates 7 dinners, builds a grocery list, and emails the plan every Sunday. Includes a web UI for viewing meals, regenerating individual days, and checking off groceries. Deployed on Railway.

**Live app:** [meal-planner.up.railway.app](https://meal-planner.up.railway.app)

## How it works

1. **Every Sunday at 9am ET**, the bot calls Claude to generate 7 dinners + snack ideas
2. **Emails the plan** with a styled HTML summary via Resend
3. **Web UI** lets you view the plan, regenerate any meal, and build your grocery list
4. **Regenerate** individual days — tell it what you don't like and it swaps in something new

## Meal preferences

| Rule | Details |
|------|---------|
| Servings | 2 people |
| Structure | 1 protein + 2 vegetable sides |
| Style | Flavorful, bold seasoning, not too complicated |
| Veggies | Must be well-seasoned — roasted, charred, glazed (no plain steamed) |
| Grocery strategy | Minimise total items, reuse ingredients across meals, use full pack sizes |
| Salads | Use salad kits, not plain lettuce |

### Dislikes (never included)

- Arugula
- Tuna salad
- Pickled anything
- Raw/uncooked onions
- Feta cheese
- Bone-in chicken (always boneless thighs or breasts)

## Features

- **Auto-generated weekly plan** — Claude creates 7 dinners + snacks every Sunday
- **Email digest** — styled HTML email with meals and full grocery list
- **Web dashboard** — browse the week's meals from any device
- **Regenerate any day** — click "Regenerate" on a meal card, optionally specify what to avoid
- **Generate New Plan** button — create a fresh plan on demand
- **Grocery list builder** — check off what you already have, see what you need to buy
- **Copy to clipboard** — one-click copy of your shopping list
- **Print view** — clean printable layout for the meal plan

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Web UI — meal plan + grocery list |
| `GET /plan` | Current meal plan as JSON |
| `POST /generate` | Generate a new weekly plan |
| `POST /regenerate` | Swap one meal (body: `{"meal_index": 0, "disliked": "salmon"}`) |
| `GET /health` | Server status + scheduler info |

