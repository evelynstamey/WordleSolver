from collections import Counter
import Levenshtein as lev
import pandas as pd
import string


def get_suggestions(corpus, clues):

    filtered_corpus = filter_words(corpus, clues)
    df = get_word_frequencies(filtered_corpus)
    candidate_words_df = get_candidate_words(
        corpus=filtered_corpus, word_frequency_df=df,
    )

    return candidate_words_df


def filter_words(corpus, clues):
    """
    Filter a list of words based on supplied criteria.
    """

    if not any([clues.not_in_word, clues.at_not_index, clues.at_index]):
        return corpus

    filtered_corpus = []
    for word in corpus:
        counts = Counter(word)
        criterion_1 = [word[int(i)] == letter for i, letter in clues.at_index.items()]
        criterion_2 = [
            word[int(i)] != letter and letter in word
            for i, letters in clues.at_not_index.items()
            for letter in letters
        ]
        criterion_3 = [
            (int(counts.get(k, 0)) - int(clues.not_in_word.get(k, 0))) <= 0
            for k in clues.not_in_word
        ]
        if all(criterion_1 + criterion_2 + criterion_3):
            filtered_corpus.append(word)

    return filtered_corpus


def get_word_frequencies(corpus):

    d_0 = dict.fromkeys(string.ascii_lowercase, 0)
    d_1 = dict.fromkeys(string.ascii_lowercase, 0)
    d_2 = dict.fromkeys(string.ascii_lowercase, 0)
    d_3 = dict.fromkeys(string.ascii_lowercase, 0)
    d_4 = dict.fromkeys(string.ascii_lowercase, 0)

    for word in corpus:
        for i, letter in enumerate(word):
            if i == 0:
                d_0[letter] += 1
            elif i == 1:
                d_1[letter] += 1
            elif i == 2:
                d_2[letter] += 1
            elif i == 3:
                d_3[letter] += 1
            elif i == 4:
                d_4[letter] += 1
            else:
                raise

    df = pd.DataFrame([d_0, d_1, d_2, d_3, d_4]).transpose()
    df["sum"] = df.sum(axis=1)

    return df


def get_candidate_words(corpus, word_frequency_df):

    seed_word = "".join(word_frequency_df[range(5)].idxmax())

    lev_r = {}
    lev_d = {}
    for word in corpus:
        lev_d[word] = lev.distance(seed_word, word)
        lev_r[word] = lev.ratio(seed_word, word)

    df = (
        pd.DataFrame([lev_d, lev_r])
        .transpose()
        .reset_index(drop=False)
        .rename(
            columns={0: "Levenshtein Distance", 1: "Levenshtein Ratio", "index": "Word"}
        )
    )

    # TODO: consider word usage to break ties (e.g. METAL > KETAL)
    def _weight_1(x):
        val = 0
        counts = Counter(x)
        for i, letter in enumerate(x):
            val += (
                word_frequency_df.loc[letter][i]
                / (word_frequency_df.loc[letter]["sum"]) ** 0.5
            ) / counts[letter] ** 3
        return val

    df["Weight"] = df["Word"].apply(lambda x: _weight_1(x))
    df["Weighted Distance"] = df["Weight"] / df["Levenshtein Distance"]
    df["Score"] = df["Weight"] * df["Levenshtein Ratio"]

    df = df.sort_values(["Score"], ascending=False).reset_index()

    return df[
        [
            "Word",
            "Levenshtein Distance",
            "Levenshtein Ratio",
            "Weighted Distance",
            "Score",
        ]
    ]
