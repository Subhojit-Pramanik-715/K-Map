from flask import Flask, render_template, request
from k_map_engine import solve_kmap


# CREATE THE FLASK APPLICATION

app = Flask(__name__)


# HOME PAGE

# Displays the main K-Map solver interface.

@app.route("/")
def home():
    return render_template("index.html")


# K-MAP SOLVER API

# Receives the minterms entered by the user, sends them to the
# K-Map solving engine, and returns the generated solution.

@app.route("/solve", methods=["POST"])
def solve():
    input_data = request.get_json()

    minterms = input_data["minterms"]

    solution = solve_kmap(minterms)

    return solution


# START THE APPLICATION

# Runs the Flask development server when this file is executed directly.

if __name__ == "__main__":
    app.run(debug=True)