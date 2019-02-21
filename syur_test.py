
#твоей, какой
#pos and advb
#don't delete case_tag, add Fixd, etc

from pprint import pprint
from syur_classes import MyWord, morph
#устало, всегда
c = "слепой"; w = MyWord(
    c,
    #is_normal_form=True,
    #tags=["Name"],
    #word_register="get_register",
    #tagset_is_full=Trueб
    #excluded_tags=["femn", "gent"]
)

print("morph_parse:")
pprint(morph.parse(c))
pprint(w.__dict__)

print("inflect", w.parse_chosen.inflect({"Patr", "Infr"}))
rows = []
rows.append(None)
print(rows)
#TODO print(w.parse_chosen.inflect({"Patr", "Infr"}))