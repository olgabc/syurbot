#!/usr/bin/python
# # -*- coding: utf-8 -*-

from libs.text_funcs import get_word_register
import pymorphy2
from syurbot_db.db_session import SESSION
from syurbot_db.db_models.freq_dict import FrequencyModel
from sqlalchemy import and_
from config.config import PSOS_TO_CHECK, UNCHANGABLE_WORDS

morph = pymorphy2.MorphAnalyzer()
freq_dict_query = SESSION.query(FrequencyModel)


class MyWordParamsError(Exception):
    pass


class MyWord:
    custom_tags = ["3_ii", "3_only", "refl", "multianim"]
    purpose = ""

    def __init__(
            self,
            word,
            tags=None,
            score=0,
            word_register=None,
            is_normal_form=False,
            tagset_is_full=False
    ):
        """

        :param word:
        :param tags: pymorphy2 tags
        :param score: float in [0,1]
        :param word_register: {None, "get_register", "lower", "title", "upper"}
        :param is_normal_form [False, True]
        :param tagset_is_full [False, True]
        """
        self.word = word
        self.parses = morph.parse(self.word)
        self.psos = list(set([str(p.tag.POS) for p in self.parses]))
        self.info = ""
        self.score = score
        self.word_register = word_register
        self.tagset_is_full = tagset_is_full
        self.pos = None
        self.is_homonym = False
        self.parse_chosen = None
        self.tags_passed = tags
        self.extra_tags = []
        self.custom_tags = []
        self.all_tags = []
        self.required_tags = []
        self.inflect_tags = []
        self.capitalized_tags = []
        self.db_tags = []

        if [parse for parse in self.parses if "UNKN" in parse.tag]:
            self.parses = None
            return

        if self._check_all_psos_fixed():
            self.info = "fixed"
            return
        if not self._check_changable():
            self.info = "unchangable"
            return

        if not self.tags_passed:
            self.tags_passed = []

        if isinstance(self.tags_passed, str):
            self.tags_passed = [self.tags_passed, ]

        if self.tags_passed:
            self.tags_passed = [str(tag) for tag in self.tags_passed]
            self._try_tags_passed()

        if is_normal_form:
            self._try_normal_form()
        if self._check_all_psos_fixed():
            self.info = "fixed"
            return

        if self.word_register:
            self._try_register()
        if self._check_all_psos_fixed():
            self.info = "fixed"
            return

        if self.score:
            self._try_score()
        if self._check_all_psos_fixed():
            self.info = "fixed"
            return

        self.pos = self._get_pos()

        if self.pos:
            self._try_pos()

        self._check_if_homonym()

        if self.is_homonym and self.pos == "NOUN":
            self._try_score(0.1)
            self._check_if_homonym()

        if self.is_homonym and MyWord.purpose != "add_db_freq_dict":
            #self._try_freq_dict() todo param for not freq dict
            self._check_if_homonym()

            if not self.is_homonym and not self.pos:
                self.pos = self._get_pos()

        self._choose_parse()

        if self.parse_chosen:
            self.info = "changable"
            self._get_capitalized_tags()
            self._get_custom_tags()
            self._get_all_tags()
            self.required_tags = self.get_required_tags()
            self.db_tags = list(set(self.required_tags + self.custom_tags + self.extra_tags + self.capitalized_tags))

            if MyWord.purpose in ["add_db_source", "add_db_freq_dict"]:
                return

            self.inflect_tags = self.get_inflect_tags()
        else:
            self.info = "trash"

    def _try_tags_passed(self):
        non_custom_tags = []

        if "multianim" in self.tags_passed and "inan" in self.tags_passed:
            self.extra_tags.append("inan")

        if "multianim" in self.tags_passed and "anim" in self.tags_passed:
            self.extra_tags.append("anim")

        for tag in self.tags_passed:

            if tag in MyWord.custom_tags:
                self.custom_tags.append(tag)
            else:
                non_custom_tags.append(tag)

        tags_set = set(non_custom_tags)

        parses = [parse for parse in self.parses if tags_set in parse.tag]

        if self.tagset_is_full:
            parses = [parse for parse in parses if set(str(parse.tag).replace(" ",",").split(",")) == tags_set]

        if parses:
            self.parses = parses
            self.psos = list(set([str(p.tag.POS) for p in self.parses]))
        else:
            raise MyWordParamsError("no such tags in parses")

    def _try_normal_form(self):
        parses = [
            parse for parse in self.parses if parse.normal_form == self.word.lower() and not any([
                not_nomn_case in str(parse.tag) for not_nomn_case in ["gent", "accs", "datv", "ablt", "loct"]
            ])
        ]

        if parses:
            self.parses = parses
            self.psos = list(set([str(p.tag.POS) for p in self.parses]))
        else:
            raise MyWordParamsError("not a normal form")

    def _try_score(self, score=None):
        if not score:
            score = self.score

        parses = [parse for parse in self.parses if parse.score > score]

        if parses:
            self.parses = parses
            self.psos = list(set([str(p.tag.POS) for p in self.parses]))
        else:
            raise MyWordParamsError("score is too high")

    def _try_register(self):

        passed_register = self.word_register in ["lower", "upper", "title"]

        if self.word_register == "get_register":
            self.word_register = get_word_register(self.word)

        title_tags = []

        if self.word_register == "lower":
            title_tags = ["Abbr", "Name", "Patr", "Surn", "Geox", "Orgn", "Trad"]
            parses = [
                parse for parse in self.parses if all([
                    title_tag not in parse.tag for title_tag in title_tags
                ])
            ]

        else:
            if self.word_register == "title":
                title_tags = ["Name", "Patr", "Surn", "Geox", "Orgn", "Trad"]

            elif self.word_register == "upper":
                title_tags = ["Abbr", ]

            parses = [parse for parse in self.parses if any([title_tag in parse.tag for title_tag in title_tags])]

        if parses:

            if self.word_register == "lower":
                self.parses = parses
                self.psos = list(set([str(p.tag.POS) for p in self.parses]))

            for tag in title_tags:
                for p in parses:
                    if tag in p.tag:
                        self.parses = parses
                        self.psos = list(set([str(p.tag.POS) for p in self.parses]))
                        break
        else:
            if passed_register:
                raise MyWordParamsError("check word's passed register")

    def _get_pos(self):

        if self.tags_passed:
            for i in self.tags_passed:
                if i == i.upper():
                    return i

        if len(set(self.psos)) == 1 and "UNKN" not in self.parses[0].tag:
            return self.parses[0].tag.POS

        elif "PRTS" in self.psos:
            return "PRTS"

        elif set(self.psos) == {"ADVB", "ADJS"} and len(set([w.normal_form for w in self.parses])) == 1:
            return "ADVB"

        elif set(self.psos) == {"ADJF", "NOUN"} and len(set([w.normal_form for w in self.parses])) == 1:
            return "ADJF"

        elif set(self.psos) == {"PRTF", "NOUN"}:
            return "PRTF"

        elif set(self.psos) == {"PRTF", "ADJF"}:
            return "PRTF"

    def _try_pos(self):
        parses = [parse for parse in self.parses if parse.tag.POS == self.pos]

        if parses:
            self.parses = parses
            self.psos = list(set([str(p.tag.POS) for p in self.parses]))

    def _check_if_homonym(self):

        if len(set(self.psos)) > 1:
            self.is_homonym = "psos"
            return

        elif len(set([parse.normal_form for parse in self.parses])) > 1:
            self.is_homonym = "normal_form"
            return

        else:
            self.is_homonym = False
            return

    def _choose_parse(self):

        if not self.pos or self.is_homonym:
            return

        tags_list = [tag for tag in self.tags_passed if tag not in MyWord.custom_tags]
        tags_set = set(tags_list)

        for w in self.parses:
            if tags_set in w.tag:
                self.parse_chosen = w
                return

    def _get_capitalized_tags(self):
        splited_tags = str(self.parse_chosen.tag).replace(" ", ",").split(",")
        capitalized_tags = [tag for tag in splited_tags if get_word_register(tag) not in ["upper", "lower"]]
        self.capitalized_tags = capitalized_tags

    def _get_custom_tags(self):

        if self.pos == "NOUN":
            declension_tags = []

            if self.parse_chosen.tag.gender == "femn" and self.parse_chosen.normal_form[-1] == "ь":
                declension_tags = ["3_ii", "3_only"]

            elif self.parse_chosen.normal_form[-2:] in ["ия", "ие", "ий"]:
                declension_tags = ["3_ii", ]

            self.custom_tags += declension_tags

            animacies = [a.tag.animacy for a in self.parses if a.tag.animacy and a.tag.POS == self.pos]

            if "inan" not in self.tags_passed or "anim" not in self.tags_passed:

                if len(set(animacies)) > 1:
                    self.custom_tags.append("multianim")

        elif self.pos in ["VERB", "INFN", "GRND", "PRTF", "PRTF"] and self.word[-2:] in ["сь", "ся"]:

            refl_tags = ["refl", ]
            self.custom_tags += refl_tags

        self.custom_tags = list(set(self.custom_tags))
        return

    def _get_all_tags(self):

        tags = str(self.parse_chosen.tag).replace(" ", ",").split(",")
        tags += self.custom_tags
        tags += self.extra_tags

        self.all_tags = list(set(tags))
        return

    def get_required_tags(self):

        required_tags = []
        required_pos = self.pos

        if self.pos == "NOUN":  # or self.word in ["он", "она", "оно", "они"]
            required_tags = [self.parse_chosen.tag.animacy, self.parse_chosen.tag.gender]

        if self.pos in ["VERB", "INFN", "PRTS", "PRTF", "GRND"]:
            required_pos = "INFN"
            required_tags = [self.parse_chosen.tag.transitivity, self.parse_chosen.tag.aspect]

            if self.pos == "PRTS":
                required_tags = ["tran", self.parse_chosen.tag.aspect]

        if self.pos in ["ADJS", "COMP"]:
            required_pos = "ADJF"

        required_tags = [str(tag_r) for tag_r in required_tags if tag_r is not None]

        if self.custom_tags:

            required_tags += self.custom_tags

            if self.word[-1:] != "ь" and "3_only" in self.custom_tags:
                required_tags.remove("3_only")

            if "refl" in self.custom_tags:
                required_tags.remove("refl")

            if "multianim" in required_tags and "inan" in required_tags:
                required_tags.remove("inan")

            if "multianim" in required_tags and "anim" in required_tags:
                required_tags.remove("anim")

        required_tags.append(required_pos)
        required_tags = list(set(required_tags))
        return [str(tag) for tag in required_tags]

    def get_excluded_tags(self):
        if self.word_register == "lower":
            return ["Abbr", "Name", "Patr", "Surn", "Geox", "Orgn", "Trad"]

    def get_inflect_tags(self):

        if not self.parse_chosen:
            return

        if self.pos == "NOUN" or self.word in ["он", "она", "оно", "они"]:
            return self._get_noun_tags()

        if self.pos in ["VERB", "INFN", "PRTS", "PRTF", "GRND"]:
            return self._get_verb_tags()

        if self.pos in ["ADJF", "ADJS", "COMP"]:
            return self._get_adjf_tags()

    def _get_noun_tags(self):
        cases_numbers = [[cn.tag.case, cn.tag.number] for cn in self.parses]

        if "Fixd" in self.parse_chosen.tag:
            return []

        elif "femn" in self.parse_chosen.tag:
            if not (
                    (
                            ["gent", "sing"] in cases_numbers and
                            ["datv", "sing"] in cases_numbers and
                            ["loct", "sing"] in cases_numbers
                    ) or
                    (
                            ["nomn", "sing"] in cases_numbers and
                            ["accs", "sing"] in cases_numbers
                    )
            ):

                return cases_numbers[0]

        elif "masc" in self.parse_chosen.tag or "neut" in self.parse_chosen.tag:
            strange_cases = ["voct", "gen1", "gen2", "acc2", "loc1", "loc2"]

            for sc in strange_cases:
                if sc in [c.tag.case for c in self.parses]:
                    return

            if not (
                    ["gent", "sing"] in cases_numbers and
                    ["datv", "sing"] in cases_numbers and
                    ["loct", "sing"] in cases_numbers and
                    ["nomn", "plur"] in cases_numbers
            ):
                return cases_numbers[0]

        if "3_ii" in self.custom_tags:
            if self.word[-1:] == "ь":
                return ['nomn', 'sing']
            else:
                return cases_numbers[0]

    def _get_verb_tags(self):
        tags_verb_infn = [
            self.parse_chosen.tag.POS,
            self.parse_chosen.tag.person,
            self.parse_chosen.tag.tense,
            self.parse_chosen.tag.gender,
            self.parse_chosen.tag.number,
            self.parse_chosen.tag.mood,
            self.parse_chosen.tag.animacy,
            self.parse_chosen.tag.case,
            self.parse_chosen.tag.involvement,
            self.parse_chosen.tag.transitivity,
            self.parse_chosen.tag.aspect
        ]

        verb_tags = [tag_vi for tag_vi in tags_verb_infn if tag_vi is not None]

        if "refl" in self.custom_tags:
            verb_tags.append("refl")
        return verb_tags

    def _get_adjf_tags(self):

        tags_adjf = [
            self.parse_chosen.tag.POS,
            self.parse_chosen.tag.gender,
            self.parse_chosen.tag.number,
            self.parse_chosen.tag.case,
            self.parse_chosen.tag.animacy
        ]

        return [tag_a for tag_a in tags_adjf if tag_a is not None]

    def _try_freq_dict(self):
        print("freq_dict")
        parses = self.parses
        in_freq_dict_parses = []

        for parse in parses:
            parse_normal_form = str(parse.normal_form)
            parse_pos = str(parse.tag.POS)

            if parse_pos in ["VERB", "GRND"]:
                parse_pos = "INFN"

            elif parse_pos in ["ADJS", "COMP", "PRTS", "PRTF"]:
                parse_pos = "ADJF"

            freq_dict_lemms = freq_dict_query.filter(
                and_(FrequencyModel.lemma == parse_normal_form, FrequencyModel.pos == parse_pos)
            )
            fd_list = [fd_parse for fd_parse in freq_dict_lemms]

            if fd_list:
                in_freq_dict_parses.append(parse)

        if in_freq_dict_parses:
            self.parses = in_freq_dict_parses
            self.psos = list(set([str(p.tag.POS) for p in self.parses]))

    def _check_changable(
            self,
            unchangable_words=UNCHANGABLE_WORDS
    ):
        if not any([str(parse.normal_form) in unchangable_words for parse in self.parses]):
            return True

    def _check_all_psos_fixed(self):
        if not any([str(parse.tag.POS) in PSOS_TO_CHECK for parse in self.parses]):
            return True

    def _check_any_pos_fixed(self):
        if any([str(parse.tag.POS) not in PSOS_TO_CHECK for parse in self.parses]):
            return True


# animacy - одушевленность
# aspect - вид (совершенный не совершенный)
# case - падеж
# gender - род
# involvment - включенность говорящего в действие
# mood - наклонение (повелительное, изъявительное)
# number - число (единственное, множественное
# person - лицо (1-е, 2-е, 3-е)
# tense - время (настоящее, прошедшее, будущее)
# transitivity - переходность (переходный, непереходный)
# voice - залог (действительный, страдательный)
