
#TODO len sen in gen_sen ?
#TODO check capital letter TODO if try_case: for i in try
#TODO add type sign or word
#TODO add score for first variant of parsed TODO implement. find same multiparsed
#TODO multianim
#pos and advb
#don't delete case_tag, add Fixd, etc

from pprint import pprint
from syur_classes import MyWord, morph

c = "атипичный"; w = MyWord(
    c,
    #is_normal_form=True
    tags=[],
    #word_register="get_register",
    tagset_is_full=True

)

print("morph_parse:")
pprint(morph.parse(c))
pprint(w.__dict__)

#print(w.parse_chosen.inflect({"loct"}))