import ast
import random
import json
import os

# Safe code execution for challenges
class SafeExecutor:
    def __init__(self, initial_vars):
        self.initial_vars = dict(initial_vars)
        self.allowed_builtins = {
            'print': print,
            'range': range,
            'len': len,
            'sum': sum,
            'min': min,
            'max': max,
            'abs': abs,
            'sorted': sorted,
        }

    def is_safe_code(self, code: str) -> (bool, str):
        try:
            tree = ast.parse(code, mode='exec')
        except SyntaxError as e:
            return False, f"SyntaxError: {e}"
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom, ast.Global, ast.Nonlocal)):
                return False, "Import/global statements are not allowed in challenges."
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id == '__import__':
                    return False, "Unsafe import via __import__ is blocked."
        return True, ""

    def run(self, code: str):
        safe, msg = self.is_safe_code(code)
        if not safe:
            return False, msg, None

        env = dict(self.initial_vars)  # fresh namespace each run
        restricted_env = {"__builtins__": self.allowed_builtins}
        try:
            exec(compile(code, "<user_code>", "exec"), restricted_env, env)
        except Exception as e:
            return False, f"RuntimeError: {e}", None
        return True, "Code executed.", env

# Progress persistence
PROGRESS_FILE = "coding_rpg_progress.json"

def load_progress():
    if not os.path.exists(PROGRESS_FILE):
        return {}
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_progress(progress: dict):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=2)

# UI and beginner-friendly flow
CHARACTERS = [
    {
        "id": "moss",
        "name": "Moss",
        "icon": "(^_^)",
        "intro": [
            "Hello, I'm Moss, your code guide. I love clean, precise steps.",
            "I'll help you understand the basics with friendly challenges."
        ],
    },
    {
        "id": "roy",
        "name": "Roy",
        "icon": "(ಠ_ಠ)",
        "intro": [
            "I'm Roy. I ask the hard questions to make sure you really understand.",
            "If something seems easy, I’ll push you to explain it further."
        ],
    },
    {
        "id": "jen",
        "name": "Jen",
        "icon": "(>_<)",
        "intro": [
            "Hi, I'm Jen. Let's get you coding basics on the fast track.",
            "Stay focused on fundamentals and practice regularly."
        ],
    },
]

CHALLENGES = [
    {
        "id": 1,
        "title": "Variables and Expressions",
        "desc": "Given a = 5 and b = 8, create a new variable c that equals a + b.",
        "starter_vars": {"a": 5, "b": 8},
        "expected_vars": {"c": 13},
        "hint": "Use the + operator to add a and b and assign to c.",
    },
    {
        "id": 2,
        "title": "Data Types and Aggregation",
        "desc": "With a list L = [1, 2, 3], compute the sum of its elements into total.",
        "starter_vars": {"L": [1, 2, 3]},
        "expected_vars": {"total": 6},
        "hint": "Use the sum() function on L and assign to total.",
    },
    {
        "id": 3,
        "title": "Conditionals",
        "desc": "Given n = 4, create a boolean is_even that is True if n is even, otherwise False.",
        "starter_vars": {"n": 4},
        "expected_vars": {"is_even": True},
        "hint": "Use n % 2 == 0 to test evenness.",
    },
    {
        "id": 4,
        "title": "Loops",
        "desc": "Create a list squares containing 1^2, 2^2, ..., 5^2.",
        "starter_vars": {"n": 5},
        "expected_vars": {"squares": [1, 4, 9, 16, 25]},
        "hint": "Fill a list by squaring indices from 1 to n inclusive.",
    },
    {
        "id": 5,
        "title": "Functions",
        "desc": "Define a function greet(name) that returns 'Hello, {name}!'. Call it with 'Ada' and store the result in greeting.",
        "starter_vars": {"name": None},
        "expected_vars": {"greeting": "Hello, Ada!"},
        "hint": "Define a function and then call: greeting = greet('Ada')",
    },
]

def print_banner():
    print("=========================================")
    print(" CodeQuest: IT Edition - Learn Python ")
    print("=========================================\n")

def select_character():
    print("Choose your guide:")
    for i, c in enumerate(CHARACTERS, start=1):
        print(f"  {i}. {c['name']} {c['icon']}")
    choice = input("Enter number (1-3): ")
    idx = int(choice) - 1 if choice.isdigit() else 0
    if idx < 0 or idx >= len(CHARACTERS):
        idx = 0
    return CHARACTERS[idx]

def show_character_intro(ch):
    print(f"\n{ch['name']} says:")
    for line in ch['intro']:
        print(f"  {line}")

def beginner_intro():
    print("\nBeginner Tutorial Path:")
    print("- We'll pace you through the very basics with clear, plain language.")
    print("- You'll be asked to write tiny snippets, then the game will check them.")
    print("- If you get stuck, ask the guide for a hint or switch guides.")

def get_user_code():
    print("Enter your code. End with a line that contains only END on its own.")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip() == "END":
            break
        lines.append(line)
    return "\n".join(lines)

def verify_env(env, expected_vars):
    for key, expected in expected_vars.items():
        if key not in env:
            return False, f"Missing variable: {key}"
        if env[key] != expected:
            return False, f"Wrong value for {key}: got {env[key]!r}, expected {expected!r}"
    return True, "All good."

def run_challenge(ch, beginner_mode=False, seed=None):
    print(f"\nCHALLENGE {ch['id']}: {ch['title']}")
    print(ch['desc'])
    if ch.get("starter_vars"):
        print("Starter variables:")
        for k, v in ch["starter_vars"].items():
            print(f"  {k} = {v!r}")
    if beginner_mode:
        print("Hint: ", ch.get("hint", "Do your best."))
        print("Tip: Try to write the minimal line that satisfies the requirement.")
    else:
        print("Hint:", ch.get("hint", "Do your best."))
    if seed is not None:
        random.seed(seed)
    code = get_user_code()
    execr = SafeExecutor(ch.get("starter_vars", {}))
    ok, msg, env = execr.run(code)
    if not ok:
        print("Feedback:", msg)
        print("Try again or ask for a hint by typing 'hint' as a command (in-game).")
        return False
    ok2, note = verify_env(env, ch["expected_vars"])
    print("Feedback:", note)
    return ok2

def load_progress_for_user(name: str):
    progress = load_progress()
    return progress.get(name, {"completed": [], "score": 0})

def save_progress_for_user(name: str, data: dict):
    progress = load_progress()
    progress[name] = data
    save_progress(progress)

def main():
    print_banner()
    name = input("What is your name, coder? ").strip() or "Adventurer"
    print(f"Greetings, {name}! Learn Python by solving coding challenges in a roguish RPG.\n")

    guide = select_character()
    show_character_intro(guide)

    beginner = input("Would you like the Beginner Tutorial Path? (yes/no): ").strip().lower() in ("yes", "y")
    beginner_intro()

    user_progress = load_progress_for_user(name)
    completed = set(user_progress.get("completed", []))
    score = user_progress.get("score", 0)
    total = len(CHALLENGES)

    for ch in CHALLENGES:
        if ch["id"] in completed:
            continue
        success = run_challenge(ch, beginner_mode=beginner, seed=42)
        if success:
            completed.add(ch["id"])
            score += 1
            user_progress["completed"] = sorted(list(completed))
            user_progress["score"] = score
            save_progress_for_user(name, user_progress)
            print("You earned 20 XP!")
            print(f"Current Score: {score}/{total}\n")
        else:
            print("Challenge not completed. You can retry later in this playthrough.\n")

    print("Adventure complete!")
    print(f"Final score for {name}: {score}/{total} challenges completed.")
    if score == total:
        print("Legendary coder! You clearly understand the basics.")
    elif score >= total // 2:
        print("Nice work! You’ve built a solid foundation.")
    else:
        print("Keep practicing. The path to mastery is paved with practice.")
    print("Would you like to retry? (yes/no)")
    again = input("> ").strip().lower()
    if again in ("yes", "y"):
        main()
    else:
        print("Thanks for playing CodeQuest. Happy coding!")

if __name__ == "__main__":
    main()
