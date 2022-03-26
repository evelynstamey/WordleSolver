import json
import nltk

import constants
from clues import Clues


def get_historical_clues(mysql, game_id):
    """
    Get historical clues (if any).
    """

    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute(
        f"""
        SELECT not_in_word, at_not_index, at_index, round_id
        FROM `WordleSolver`.`clues`
        WHERE game_id = "{game_id}"
        ORDER BY round_id DESC
        LIMIT 1
        """
    )
    row = cursor.fetchone()

    not_in_word = {} if not row else json.loads(row[0])
    at_not_index = {} if not row else json.loads(row[1])
    at_index = {} if not row else json.loads(row[2])
    round_id = 0 if not row else row[3]

    return Clues(not_in_word, at_not_index, at_index, round_id=round_id,)


def get_corpus(mysql, game_id, round_id, excluded_words=constants.EXCLUDED_WORDS):
    """Get list of all 5-letter words in English language (according to
    nltk.corpus.words). Exclude words that are known to not be in Wordle
    dictionary.
    """

    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute(
        f"""
        SELECT corpus
        FROM `WordleSolver`.`corpus`
        WHERE game_id = "{game_id}" AND round_id = "{round_id}"
        LIMIT 1
        """
    )
    row = cursor.fetchone()

    if row:
        corpus = json.loads(row[0])
    else:  # If no corpus exists in database, initialize corpus

        # TODO: This data should always exist in database
        nltk.download("words")
        words_corpus = nltk.corpus.words
        all_words = words_corpus.words()
        corpus = [
            w.lower()
            for w in all_words
            if len(w) == 5 and w.lower() not in excluded_words
        ]
        log_corpus_round(mysql, game_id, round_id, corpus)

    return corpus


def log_corpus_round(mysql, game_id, round_id, corpus):

    conn = mysql.connection
    cursor = conn.cursor()
    cursor.callproc("sp_WriteCorpus", (game_id, round_id, json.dumps(corpus)))
    conn.commit()


def log_clues_round(
    mysql, game_id, round_id, new_clues, updated_clues,
):

    conn = mysql.connection
    cursor = conn.cursor()
    cursor.callproc(
        "sp_WriteClues",
        (
            game_id,
            round_id,
            new_clues.guess,
            json.dumps(new_clues.not_in_word),
            json.dumps(new_clues.at_not_index),
            json.dumps(new_clues.at_index),
            json.dumps(updated_clues.not_in_word),
            json.dumps(updated_clues.at_not_index),
            json.dumps(updated_clues.at_index),
        ),
    )
    conn.commit()
