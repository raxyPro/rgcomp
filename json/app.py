from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    sample_data = {
        "name": "Rampal",
        "age": 50,
        "skills": ["Python", "Flask", "SQL"]
    }

    empty_data = {}  # or None

    return render_template("index.html", data=sample_data, blank=empty_data)

if __name__ == "__main__":
    app.run(debug=True)
