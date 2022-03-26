from flask import Flask, request, render_template, session
from flask_mysqldb import MySQL
import uuid

import suggest
import database
import clues

app = Flask(__name__)
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "WordleSolver"
app.secret_key = "xyz"  # is this needed?

mysql = MySQL()
mysql.init_app(app)


@app.route("/", methods=["GET", "POST"])
def main():

    if request.method == "POST":

        if request.form["submit-button"] == "GET STARTED":
            session["game_id"] = str(uuid.uuid1())
            print(f"Game ID: {session['game_id']}")
            return render_template("form.html", letter_index=list(range(5)))

        elif request.form["submit-button"] == "NEXT GUESS":

            # Get clues from latest user submission
            game_id = session["game_id"]
            submission = _standardize_inputs()
            new_clues = clues.process_submission(submission)

            # Get clues and corpus from database
            historical_clues = database.get_historical_clues(mysql, game_id)
            corpus = database.get_corpus(mysql, game_id, historical_clues.round_id)

            # Join new clues with historical clues
            updated_clues = clues.update_clues(new_clues, historical_clues)

            # Log updated clues
            database.log_clues_round(
                mysql,
                game_id=game_id,
                round_id=historical_clues.round_id + 1,
                new_clues=new_clues,
                updated_clues=updated_clues,
            )

            # Get WordleSolver suggestions
            df = suggest.get_suggestions(corpus, updated_clues)
            words = df["Word"].tolist()
            top_word = df["Word"][df.index == 0].get(0)

            # Log updated corpus
            database.log_corpus_round(
                mysql,
                game_id=game_id,
                round_id=historical_clues.round_id + 1,
                corpus=words,
            )
            # Surface WordleSolver suggestions to user
            rendered_templates = render_template(
                "form.html",
                letter_index=list(range(5)),
                default_0="" if not top_word else top_word[0],
                default_1="" if not top_word else top_word[1],
                default_2="" if not top_word else top_word[2],
                default_3="" if not top_word else top_word[3],
                default_4="" if not top_word else top_word[4],
            ) + df[["Word", "Score"]].head(5).to_html(index=False)

            return rendered_templates

    return render_template("get_started.html")


def _standardize_inputs():
    submission = {
        f"{i}": {
            "letter": request.form.get(f"cell-{i}", "").lower(),
            "color": request.form.get(f"group-{i}", "").lower(),
        }
        for i in range(5)
    }
    return submission


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1")
