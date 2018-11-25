
#TODO len sen in gen_sen ?
#TODO check capital letter TODO if try_case: for i in try
#TODO add type sign or word
#TODO add score for first variant of parsed TODO implement. find same multiparsed
#TODO multianim
#pos and advb
#don't delete case_tag, add Fixd, etc

from pprint import pprint
from syur_classes import MyWord, morph

import os
#import pandas as pd
from generation_funcs import generate_word, check_sentence, replace_word, generate_sentence, choose_sentences
import re

c = "и"; w = MyWord(
    c,
    tags="",
    word_register="get_register",
    is_normal_form=True
)
print("morph_parse:")
pprint(morph.parse(c))
pprint(w.__dict__)
print(w.parse_chosen.inflect({"sing"}))




