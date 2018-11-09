def get_word_register(word):
    if word.islower():
        return "lower"

    elif word.istitle():
        return "title"

    elif word.isupper():
        return "upper"


def replace_with_case(word_f, word_r):
    if word_f.islower():
        return word_f.replace(word_f, word_r.lower())

    elif word_f.istitle():
        return word_f.replace(word_f, word_r.capitalize())

    elif word_f.isupper():
        return word_f.replace(word_f, word_r.upper())
