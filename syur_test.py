
#твоей, какой
#pos and advb
#don't delete case_tag, add Fixd, etc

from pprint import pprint
from syur_classes import MyWord, morph
#устало, всегда
c = "такой"; w = MyWord(
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

#print("inflect", w.parse_chosen.inflect({"ADJS"}).word)

#TODO print(w.parse_chosen.inflect({"Patr", "Infr"}))
generated_sentence = generate_sentence(
        my_sentence="",
        word_source_id=2,
        sentence_source_id=2,
        sentence_length_min=7,
        sentence_length_max=15,
        unchangable_words_qty_max=3,
        fixed_words_qty_max=None,
        trash_words_qty_max=None,
        print_old_sentence=True
    )

print(generated_sentence)