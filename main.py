from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)

# -----------------------------
# Backend data (in-memory)
# Resets every time server restarts
# -----------------------------
teams = {f"Team{i}": {"questions": [], "score": 0} for i in range(1, 6)}

# -----------------------------
# Routes
# -----------------------------

@app.route("/")
def index():
    return render_template("index.html", teams=teams)

@app.route("/reset")
def reset():
    """Reset all backend data"""
    global teams
    teams = {f"Team{i}": {"questions": [], "score": 0} for i in range(1, 6)}
    return redirect(url_for("index"))

@app.route("/login/<team_name>")
def login(team_name):
    if team_name not in teams:
        return "Invalid team!", 404
    return render_template("team.html", team=team_name, questions=teams[team_name]["questions"])

@app.route("/add_question/<team_name>", methods=["POST"])
def add_question(team_name):
    if team_name not in teams:
        return "Invalid team!", 404

    question = request.form.get("question")
    options = [request.form.get(f"opt{i}") for i in range(1, 5)]
    answer = request.form.get("answer")

    if not question or not all(options) or not answer:
        return "Missing input", 400

    # Convert answer to uppercase and map to 0-based index
    answer = answer.upper()
    if answer not in ["A", "B", "C", "D"]:
        return "Answer must be A, B, C, or D", 400

    answer_index = {"A":0, "B":1, "C":2, "D":3}[answer]

    teams[team_name]["questions"].append({
        "question": question,
        "options": options,
        "answer": answer_index,
      "answered_by":[]
    })

    return redirect(url_for("login", team_name=team_name))

@app.route("/quiz/<team_name>")
def quiz(team_name):
    if team_name not in teams:
        return "Invalid team!", 404
    return render_template(
        "quiz.html",
        team=team_name,
        questions=teams[team_name]["questions"],
        teams=teams
    )

@app.route("/answer/<team_name>/<int:q_index>", methods=["POST"])
def answer(team_name, q_index):
    if team_name not in teams:
        return "Invalid team!", 404

    answering_team = request.form.get("team")
    answer_value = request.form.get("answer")

    if not answering_team or answer_value is None:
        return "Missing input", 400

    question = teams[team_name]["questions"][q_index]

    # Prevent answering again
    if answering_team in question["answered_by"]:
        return "This team has already answered this question!", 400

    ans = int(answer_value)
    correct = question["answer"]

    # Update score if correct
    if ans == correct and answering_team in teams:
        teams[answering_team]["score"] += 1

    # Mark this team as having answered
    question["answered_by"].append(answering_team)

    return redirect(url_for("quiz", team_name=team_name))


@app.route("/leaderboard")
def leaderboard():
    return render_template("leaderboard.html", teams=teams)

# -----------------------------
# Start the server
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
