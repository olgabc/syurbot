import pymorphy2

morph = pymorphy2.MorphAnalyzer()


class MyWord:

    def __init__(
            self,
            word,
            tags=None,
            score=None,
            word_register=None
    ):
        """

        :param word:
        :param tags: pymorphy2 tags
        :param score: float in [0,1]
        :param word_register: {None, "lower", "title", "upper"}
        """
        self.word = word
        self.parses = morph.parse(self.word)
        self.score = score
        self.word_register = word_register
        self.register_tag = []
        self.pos = None
        self.is_homonym = False
        self.parse_chosen = None
        self.tags_passed = tags
        self.extra_tags = []

        if not self.tags_passed:
            self.tags_passed = []

        if isinstance(self.tags_passed, str):
            self.tags_passed = [self.tags_passed, ]

        if self.score:
            self.parses = [parse for parse in self.parses if parse.score > self.score]

        if self.word_register:
            self.parses = self._try_register()["parses"]
            self.register_tag = self._try_register()["tag"]

            if self.register_tag:
                self.extra_tags += self.register_tag

        self.psos = [str(p.tag.POS) for p in self.parses]
        self.pos = self._get_pos()
        self.is_homonym = self._check_if_homonym()
        self.parse_chosen = self._choose_parse()
        self.extra_tags = self._get_extra_tags()
        self.all_tags = self._actualize_tags()

    def _check_if_homonym(self):

        if self.is_homonym:
            return True

        elif len(set(self.psos)) > 1:
            return True
        
        elif self.pos == "NOUN":

            if "inan" not in self.tags_passed or "anim" not in self.tags_passed:
                animacies = [a.tag.animacy for a in self.parses if a.tag.animacy and a.tag.POS == self.pos]

                if len(set(animacies)) > 1:
                    return True

            elif "masc" not in self.tags_passed or "neut" not in self.tags_passed or "femn" not in self.tags_passed:
                genders = [ge.tag.gender for ge in self.parses if ge.tag.gender and ge.tag.POS == self.pos]

                if len(set(genders)) > 1:
                    return True  

        else:
            return False

    def _get_pos(self):

        if self.tags_passed:
            for i in self.tags_passed:
                if i == i.upper():
                    return i

        elif "PRTS" in self.psos:
            return "PRTS"

        elif "PRTF" in self.psos:
            return "PRTF"

        elif "ADVB" in self.psos:
            return "ADVB"

        elif len(set(self.psos)) == 1 and "UNKN" not in self.parses[0].tag:
            return self.parses[0].tag.POS        

    def _choose_parse(self):

        if not self.pos or self.is_homonym:
            return

        tags_set = set(self.tags_passed)

        for w in self.parses:
            if tags_set in w.tag:
                return w

    def _get_extra_tags(self):

        declension_tags = []

        if self.pos == "NOUN" and not self.is_homonym:

            if self.parse_chosen.tag.gender == "femn" and self.word[-1] == "ь":
                declension_tags = ["3_ii", "3_only"]

            elif self.parse_chosen.tag.gender == "femn" and self.parse_chosen.normal_form[-1] == "ь":
                declension_tags = ["3_ii", "3_only"]

            elif self.parse_chosen.normal_form[-2:] in ["ия", "ие", "ий"]:
                declension_tags = ["3_ii", ]

        elif self.pos in ["VERB", "INFN"] and self.word[-2:] in ["сь", "ся"]:

            declension_tags = ["refl", ]

        declension_tags += self.register_tag

        return declension_tags

    def _actualize_tags(self):

        if not self.parse_chosen:
            return

        tags = str(self.parse_chosen.tag).split(",")

        if self.extra_tags:
            tags += self.extra_tags

        return ','.join(tags)

    def get_required_tags(self):

        required_tags = []
        required_pos = self.pos

        if self.pos == "NOUN":  # or self.word in ["он", "она", "оно", "они"]
            required_tags = [self.parse_chosen.tag.animacy, self.parse_chosen.tag.gender]
            if "Fixd" in self.parse_chosen.tag:
                required_tags.append("Fixd")

        if self.pos in ["VERB", "INFN", "PRTS", "PRTF", "GRND"]:
            required_pos = "INFN"
            required_tags = [self.parse_chosen.tag.transitivity, self.parse_chosen.tag.aspect]
            if self.pos == "PRTS":
                required_tags = ["tran", self.parse_chosen.tag.aspect]

        if self.pos in ["ADJS", "COMP"]:
            required_pos = "ADJF"

        required_tags = [str(tag_r) for tag_r in required_tags if tag_r is not None]

        if self.extra_tags:
            required_tags += self.extra_tags

            if self.word[-1:] != "ь" and "3_only" in self.extra_tags:
                required_tags.remove("3_only")

            if "refl" in self.extra_tags:
                required_tags.remove("refl")

        required_tags.append(required_pos)

        return required_tags

    def get_excluded_tags(self):  #
        if self.word_register == "lower":
            return ["Abbr", "Name", "Patr", "Surn", "Geox", "Orgn", "Trad"]

    def get_inflect_tags(self):

        if self.pos == "NOUN" or self.word in ["он", "она", "оно", "они"]:
            return self._get_noun_tags()

        if self.pos in ["VERB", "INFN", "PRTS", "PRTF", "GRND"]:
            return self._get_verb_tags()

        if self.pos in ["ADJF", "ADJS", "COMP"]:
            return self._get_adjf_tags()

    def _get_noun_tags(self):
        cases_numbers = [[cn.tag.case, cn.tag.number] for cn in self.parses]

        if "femn" in self.parse_chosen.tag:
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

        if "3_ii" in self.extra_tags:
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

        if "refl" in self.extra_tags:
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

    def _try_register(self):

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
                return {"parses": parses, "tag": []}

            for tag in title_tags:
                for p in parses:
                    if tag in p.tag:
                        return {"parses": parses, "tag": [tag, ]}

        else:
            return {"parses": self.parses, "tag": []}


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
