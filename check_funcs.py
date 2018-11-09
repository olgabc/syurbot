from syur_classes import *
from config.config import *


def print_if(to_print, pattern='', word=''):
    if to_print:
        print("{}, {}".format(pattern, word))


def check_word(word, to_print=False):
    w = MyWord(word)
    w.get_inflect_tags()
    result = False

    if w.parsed[0].normal_form in UNCHANGABLE_WORDS:
        print_if(to_print, "unchangeble_word", word)
        result = "fixed"

    if not result and all([pos not in w.psos for pos in PSOS_TO_CHECK]):
        print_if(to_print, "unchangable_pos", word)
        result = "fixed"

    if not result and not w.is_homonym:
        print_if(to_print, "not_homonym", word)
        result = str(w.parsed[0].tag.POS)

    if not result and w.parsed[0].score > 0.99:
        if w.parsed[0].tag.POS in PSOS_TO_CHECK:
            print_if(to_print, "homonym score more", word)
            result = str(w.parsed[0].tag.POS)

        else:
            print_if(to_print, "fixed homonym score more", word)
            result = "fixed"

    if w.pos == "NOUN" and not w.get_inflect_tags():
        print_if(to_print, "trash inflect", word)
        result = "trash"

    if not result:
        print_if(to_print, "trash", word)
        return "trash"
    else:
        return result