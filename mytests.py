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


for file in os.listdir("books"): #
    #split_book_by_sentences(file[:-4])
    #get_dict_from_source(file[:-4])
    #choose_sentences(file[:-4], delete_na=False)
    #get_psos_base(file[:-4])
    pass

#get_psos_base("dol_sta_vet") score=0.2, obj <class 'pymorphy2.analyzer.Parse'>
##asdf юродствовать ('futr',) INFN
#d = "ван"; x = MyWord(d, "VERB"); print("d", x.get_required_tags())

c = "паша"; w = MyWord(
    c,
    tags=["NOUN"],
    word_register={},
    #is_normal_form=True
) #print("obj", w.parse_chosen.tag.number, w.parse_chosen.tag.case), pprint(w.parses)
print("morph_parse:")
pprint(morph.parse(c))
pprint(w.__dict__)

#print("check_word", check_word(c))
#print(check_sentence("Для Зои Карловны был чудом"))
#print(generate_word(pos="VERB", required_tags=["perf", "intr"], inflect_tags=("futr","2per"), freq=None, source="freq"))
#print(generate_sentence("ann_kar", to_print=False))
#print(generate_sentence("ann_kar", to_print=False))
#print(generate_sentence(my_sentence="Никогда не надоест"))




