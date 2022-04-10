from collections import Counter


class Clues:
    def __init__(self, not_in_word, at_not_index, at_index, guess=None, round_id=None):
        """
        not_in_word : dict
            Letters that are not in word and their known maximum occurance
            {<letter, str>: <max count, int>}
        at_not_index : dict
            Letters in word that are NOT at given index
            {<index, int>: <letters, list>}
        at_index : dict
            Letters in word that are at given index
            {<index, int>: <letter, str>}
        guess : str or None
            A five-letter word (if clue corresponds to a user submission)
        round_id : int or None
            The number of rounds completed (if clue corresponds to a historical summary)
        """
        
        self.not_in_word = not_in_word
        self.at_not_index = at_not_index
        self.at_index = at_index
        self.guess = guess
        self.round_id = round_id


def process_submission(submission):
    """
    Process form submission data so that it can be ingested into the WordleSolver.

    Parameters
    ----------
    submission : dict
        {<index>: {"letter": <letter>, "color": <color>}}

    Returns
    -------
    Clues
    """

    # Process green and yellow clues
    greens = []
    yellows = []
    at_index = {}
    at_not_index = {}
    for i, data in submission.items():
        if data["color"] == "green":
            at_index.update({i: data["letter"]})
            greens.append(data["letter"])
        elif data["color"] == "yellow":
            at_not_index.update({i: [data["letter"]]})
            yellows.append(data["letter"])

    # Grey clues are tricky due to letter multiplicity
    not_in_word = {}
    counts = Counter(yellows + greens)
    for i, data in submission.items():
        if data["color"] == "grey":
            max_count = counts.get(data["letter"], 0)
            not_in_word.update({data["letter"]: max_count})

    guess = "".join(submission[f"{i}"]["letter"] for i in range(5))

    return Clues(not_in_word, at_not_index, at_index, guess=guess)


def update_clues(new_clues, historical_clues):
    """
    Join new clues with historical clues.
    """

    updated_at_index = historical_clues.at_index
    updated_at_index.update(new_clues.at_index)

    updated_at_not_index = historical_clues.at_not_index
    for i, letters in new_clues.at_not_index.items():
        updated_at_not_index[i] = letters + historical_clues.at_not_index.get(i, [])

    updated_not_in_word = {}
    not_letters = set().union(*[new_clues.not_in_word, historical_clues.not_in_word])
    for letter in not_letters:
        updated_not_in_word[letter] = max(
            int(new_clues.not_in_word.get(letter, 0)),
            int(historical_clues.not_in_word.get(letter, 0)),
        )

    return Clues(updated_not_in_word, updated_at_not_index, updated_at_index)
