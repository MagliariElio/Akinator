import json
import math
from collections import deque

# ------------------ CONFIG ------------------

ANSWER_MAP = {
    "s": 0.9,
    "ps": 0.7,
    "pn": 0.3,
    "n": 0.1,
    "non so": 0.5
}

VALID_ANSWERS = ["s", "ps", "pn", "n", "non so"]

STABILITY_WINDOW = 3

# ------------------ DATA ------------------

def load_data():
    try:
        with open("../resources/data.json", "r") as f:
            return json.load(f)
    except:
        return {"characters": {}, "questions": [], "stats": {}}


def save_data(data):
    with open("../resources/data.json", "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def ask_valid(prompt, valid):
    while True:
        ans = input(prompt).strip().lower()
        if ans in valid:
            return ans
        print(f"Opzioni valide: {valid}")


# ------------------ PROBABILITY ------------------

def get_prob_yes(counts):
    total = counts["yes"] + counts["no"] + counts["unknown"]
    return (counts["yes"] + 1) / (total + 2)


def initialize_priors(data):
    priors = {}
    total = 0

    for char in data["characters"]:
        stats = data["stats"].get(char, {"times_seen": 1})
        score = stats["times_seen"]
        priors[char] = score
        total += score

    return {c: v / total for c, v in priors.items()}


# ------------------ BAYES UPDATE ------------------

def update_probabilities(probs, question_idx, answer, data):
    new_scores = {}

    for char, prior in probs.items():
        counts = data["characters"][char][question_idx]
        prob_yes = get_prob_yes(counts)

        target = ANSWER_MAP[answer]

        likelihood = 1 - abs(prob_yes - target)
        likelihood = max(likelihood, 1e-6)

        new_scores[char] = math.log(prior) + math.log(likelihood)

    max_log = max(new_scores.values())
    exp_scores = {c: math.exp(v - max_log) for c, v in new_scores.items()}
    total = sum(exp_scores.values())

    return {c: v / total for c, v in exp_scores.items()}


# ------------------ ENTROPY ------------------

def entropy(probabilities):
    return -sum(p * math.log2(p) for p in probabilities if p > 0)


def expected_entropy(probs, question_idx, data):
    yes_branch = []
    no_branch = []

    for char, p in probs.items():
        prob_yes = get_prob_yes(data["characters"][char][question_idx])

        yes_branch.append(p * prob_yes)
        no_branch.append(p * (1 - prob_yes))

    total_yes = sum(yes_branch)
    total_no = sum(no_branch)

    def normalize(branch):
        s = sum(branch)
        return [p / s for p in branch] if s > 0 else []

    yes_entropy = entropy(normalize(yes_branch)) if total_yes > 0 else 0
    no_entropy = entropy(normalize(no_branch)) if total_no > 0 else 0

    return total_yes * yes_entropy + total_no * no_entropy


def select_best_question(probs, asked, data):
    best_q = None
    best_score = float("inf")

    for i in range(len(data["questions"])):
        if i in asked:
            continue

        score = expected_entropy(probs, i, data)

        if score < best_score:
            best_score = score
            best_q = i

    return best_q


# ------------------ LEARNING ------------------

def create_empty_vector(n):
    return [{"yes": 1, "no": 1, "unknown": 1} for _ in range(n)]


def update_character(data, character, answers):
    for q_idx, ans in answers.items():
        counts = data["characters"][character][q_idx]

        if ans == "s":
            counts["yes"] += 1
        elif ans == "n":
            counts["no"] += 1
        else:
            counts["unknown"] += 1


def update_stats(data, character, correct):
    if character not in data["stats"]:
        data["stats"][character] = {"times_seen": 0, "times_correct": 0}

    data["stats"][character]["times_seen"] += 1

    if correct:
        data["stats"][character]["times_correct"] += 1


def learn_new_character(data, answers):
    print("\nChi era il personaggio?")
    name = input(">> ").strip()

    if name == "":
        print("Nome non valido")
        return

    if name not in data["characters"]:
        vec = create_empty_vector(len(data["questions"]))
        data["characters"][name] = vec

    update_character(data, name, answers)
    update_stats(data, name, True)

    print(f"Ho imparato '{name}'!")


# ------------------ UTILS -----------------

def debug_fun(probs):
    print("\n📊 DEBUG - Top 10 probabilità aggiornate:")

    top10 = sorted(probs.items(), key=lambda x: -x[1])[:10]

    for i, (char, p) in enumerate(top10, 1):
        print(f"{i:2d}. {char:<20} -> {p:.4f}")


# ------------------ GAME ------------------

def run_game():
    while True:
        data = load_data()

        if not data["questions"]:
            print("Inserisci almeno una domanda in data.json")
            return

        if not data["characters"]:
            print("Nessun personaggio. Creane uno.")
            learn_new_character(data, {})
            save_data(data)
            continue

        probs = initialize_priors(data)

        asked = set()
        answers = {}
        leader_history = deque(maxlen=STABILITY_WINDOW)

        for _ in range(20):
            q_idx = select_best_question(probs, asked, data)
            if q_idx is None:
                break

            print("\n" + data["questions"][q_idx])
            ans = ask_valid("(s/ps/ns/n/non so): ", VALID_ANSWERS)

            asked.add(q_idx)
            answers[q_idx] = ans

            probs = update_probabilities(probs, q_idx, ans, data)
            debug_fun(probs)

            sorted_chars = sorted(probs.items(), key=lambda x: -x[1])
            best_char, best_prob = sorted_chars[0]
            second_prob = sorted_chars[1][1] if len(sorted_chars) > 1 else 0

            confidence = best_prob - second_prob
            leader_history.append(best_char)

            if best_prob > 0.75 and confidence > 0.2:
                print(f"\nSto pensando a: {best_char}")
                guess = ask_valid("Ho indovinato? (s/n): ", ["s", "n"])

                if guess == "s":
                    update_character(data, best_char, answers)
                    update_stats(data, best_char, True)
                    print("Preso!")
                else:
                    update_stats(data, best_char, False)
                    learn_new_character(data, answers)

                break

            if (len(leader_history) == STABILITY_WINDOW and
                len(set(leader_history)) == 1 and
                best_prob > 0.4):

                print(f"\nSto convergendo su: {best_char}")
                guess = ask_valid("Ho indovinato? (s/n): ", ["s", "n"])

                if guess == "s":
                    update_character(data, best_char, answers)
                    update_stats(data, best_char, True)
                else:
                    update_stats(data, best_char, False)
                    learn_new_character(data, answers)

                break

        else:
            best_char = max(probs, key=probs.get)

            print(f"\nDirei: {best_char}")
            guess = ask_valid("Ho indovinato? (s/n): ", ["s", "n"])

            if guess == "s":
                update_character(data, best_char, answers)
                update_stats(data, best_char, True)
            else:
                update_stats(data, best_char, False)

                choice = ask_valid(
                    "\nVuoi continuare la partita o rivelare il personaggio? (continua/rivela): ",
                    ["continua", "rivela"]
                )

                if choice == "continua":
                    print("\nContinuiamo allora...")

                    # reset ciclo con nuove domande
                    extra_rounds = 10

                    for _ in range(extra_rounds):
                        q_idx = select_best_question(probs, asked, data)
                        if q_idx is None:
                            break

                        print("\n" + data["questions"][q_idx])
                        ans = ask_valid("(s/ps/ns/n/non so): ", VALID_ANSWERS)

                        asked.add(q_idx)
                        answers[q_idx] = ans

                        probs = update_probabilities(probs, q_idx, ans, data)
                        debug_fun(probs)

                        sorted_chars = sorted(probs.items(), key=lambda x: -x[1])
                        best_char, best_prob = sorted_chars[0]

                        if best_prob > 0.85:
                            print(f"\nOra penso sia: {best_char}")
                            guess = ask_valid("Ho indovinato? (s/n): ", ["s", "n"])

                            if guess == "s":
                                update_character(data, best_char, answers)
                                update_stats(data, best_char, True)
                            else:
                                update_stats(data, best_char, False)
                                learn_new_character(data, answers)

                            break

                else:
                    learn_new_character(data, answers)

        save_data(data)

        again = input("\nVuoi giocare ancora? (s/n): ").lower()
        if again != "s":
            print("\n\nÈ stato bello giocare insieme!")
            print("By Elio Magliari ;)\n")
            break


# ------------------ START ------------------

if __name__ == "__main__":
    run_game()