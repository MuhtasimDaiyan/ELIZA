import logging
import random
import re
from pathlib import Path

log = logging.getLogger(__name__)

class Key:
    def __init__(self, word, weight, decomps):
        self.word = word
        self.weight = weight
        self.decomps = decomps

class Decomp:
    def __init__(self, parts, save, reasmbs):
        self.parts = parts
        self.save = save
        self.reasmbs = reasmbs
        self.next_reasmb_index = 0

class Eliza:
    def __init__(self):
        self.initials = []
        self.finals = []
        self.quits = []
        self.pres = {}
        self.posts = {}
        self.synons = {}
        self.keys = {}
        self.memory = []

        self.geo_state = {
            'country': None,
            'region': None,
            'subtopic': None,
            'turn': 0,
            'last_prompt_type': None,   
            'last_question': None,     
        }
        self.response_history = []
        self.topic_shift_count = 0

    _CONTINENTS = {
        "Africa": [
            "Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi",
            "Cameroon", "Chad", "Comoros", "Congo", "Djibouti", "Egypt",
            "Equatorial Guinea", "Eritrea", "Eswatini", "Ethiopia", "Gabon",
            "Gambia", "Ghana", "Guinea", "Ivory Coast", "Kenya", "Lesotho",
            "Liberia", "Libya", "Madagascar", "Malawi", "Mali", "Mauritania",
            "Mauritius", "Morocco", "Mozambique", "Namibia", "Niger", "Nigeria",
            "Rwanda", "Senegal", "Seychelles", "Sierra Leone", "Somalia",
            "South Africa", "South Sudan", "Sudan", "Tanzania", "Togo",
            "Tunisia", "Uganda", "Zambia", "Zimbabwe"
        ],
        "Asia": [
            "Afghanistan", "Armenia", "Azerbaijan", "Bahrain", "Bangladesh",
            "Bhutan", "Brunei", "Cambodia", "China", "Georgia", "India",
            "Indonesia", "Iran", "Iraq", "Israel", "Japan", "Jordan",
            "Kazakhstan", "Kuwait", "Kyrgyzstan", "Laos", "Lebanon",
            "Malaysia", "Maldives", "Mongolia", "Myanmar", "Nepal",
            "North Korea", "Oman", "Pakistan", "Philippines", "Qatar",
            "Saudi Arabia", "Singapore", "South Korea", "Sri Lanka", "Syria",
            "Taiwan", "Tajikistan", "Thailand", "Timor-Leste", "Turkey",
            "Turkmenistan", "United Arab Emirates", "Uzbekistan", "Vietnam", "Yemen"
        ],
        "Europe": [
            "Albania", "Andorra", "Austria", "Belarus", "Belgium",
            "Bosnia and Herzegovina", "Bulgaria", "Croatia", "Czech Republic",
            "Denmark", "Estonia", "Finland", "France", "Germany", "Greece",
            "Hungary", "Iceland", "Ireland", "Italy", "Kosovo", "Latvia",
            "Lithuania", "Luxembourg", "Malta", "Moldova", "Montenegro",
            "Netherlands", "North Macedonia", "Norway", "Poland", "Portugal",
            "Romania", "Russia", "Serbia", "Slovakia", "Slovenia", "Spain",
            "Sweden", "Switzerland", "Ukraine", "United Kingdom"
        ],
        "North America": [
            "Antigua and Barbuda", "Bahamas", "Barbados", "Belize", "Canada",
            "Costa Rica", "Cuba", "Dominica", "Dominican Republic", "El Salvador",
            "Grenada", "Guatemala", "Haiti", "Honduras", "Jamaica", "Mexico",
            "Nicaragua", "Panama", "Saint Lucia", "Trinidad and Tobago",
            "United States"
        ],
        "South America": [
            "Argentina", "Bolivia", "Brazil", "Chile", "Colombia",
            "Ecuador", "Guyana", "Paraguay", "Peru", "Suriname",
            "Uruguay", "Venezuela"
        ],
        "Oceania": [
            "Australia", "Fiji", "Kiribati", "Marshall Islands",
            "Micronesia", "Nauru", "New Zealand", "Palau",
            "Papua New Guinea", "Samoa", "Solomon Islands",
            "Tonga", "Tuvalu", "Vanuatu"
        ],
        "Antarctica": []
    }

    _COUNTRY_ALIASES = {
        # common variants
        "usa": "United States",
        "u.s.": "United States",
        "u.s.a.": "United States",
        "us": "United States",
        "america": "United States",
        "united states": "United States",
        "united states of america": "United States",

        "uk": "United Kingdom",
        "england": "United Kingdom",

        "uae": "United Arab Emirates",
        "emirates": "United Arab Emirates",

        "south korea": "South Korea",
        "korea": "South Korea",
        "north korea": "North Korea",

        "russia": "Russia",
        "ivory coast": "Ivory Coast",

        "bangladesh": "Bangladesh",
        "india": "India",
        "pakistan": "Pakistan",
        "japan": "Japan",
        "china": "China",
        "france": "France",
        "germany": "Germany",
        "italy": "Italy",
        "spain": "Spain",
        "brazil": "Brazil",
        "canada": "Canada",
        "mexico": "Mexico",
        "australia": "Australia",
        "new zealand": "New Zealand",
        "egypt": "Egypt",
        "nigeria": "Nigeria",
        "kenya": "Kenya",
        "south africa": "South Africa",
        "argentina": "Argentina",
        "chile": "Chile",
        "peru": "Peru",
        "colombia": "Colombia",
        "thailand": "Thailand",
        "vietnam": "Vietnam",
        "indonesia": "Indonesia",
        "saudi arabia": "Saudi Arabia",
        "turkey": "Turkey",
        "greece": "Greece",
        "sweden": "Sweden",
        "norway": "Norway",
        "finland": "Finland",
        "poland": "Poland",
        "ukraine": "Ukraine",
        "morocco": "Morocco",
        "ethiopia": "Ethiopia",
        "iran": "Iran",
        "iraq": "Iraq",
        "nepal": "Nepal",
        "bhutan": "Bhutan",
        "sri lanka": "Sri Lanka",
        "singapore": "Singapore",
        "malaysia": "Malaysia",
        "philippines": "Philippines"
    }

    _CONTINENT_ALIASES = {
        "africa": "Africa",
        "asia": "Asia",
        "europe": "Europe",
        "north america": "North America",
        "south america": "South America",
        "latin america": "South America",
        "oceania": "Oceania",
        "australia": "Oceania",
        "antarctica": "Antarctica"
    }

    _REGION_KEYWORDS = {
        "north": "north",
        "south": "south",
        "east": "east",
        "west": "west",
        "central": "central",
        "coastal": "coastal",
        "interior": "interior",
        "urban": "urban",
        "rural": "rural",
        "delta": "delta",
        "mountain": "mountain",
        "coast": "coast",
        "desert": "desert"
    }

    _SUBTOPIC_KEYWORDS = {
        "climate": {
            "climate", "weather", "temperature", "rain", "rainfall", "monsoon",
            "snow", "humid", "humidity", "dry", "season", "seasons", "storm",
            "storms", "hot", "cold", "warm", "cool"
        },
        "culture": {
            "culture", "cultural", "tradition", "traditions", "religion",
            "religious", "language", "languages", "people", "society",
            "food", "cuisine", "music", "festival", "festivals", "lifestyle"
        },
        "cities": {
            "city", "cities", "urban", "capital", "capitals", "town", "towns",
            "population", "metro", "metropolitan"
        },
        "distance": {
            "distance", "distances", "far", "near", "close", "drive",
            "flight", "travel time", "miles", "mile", "kilometer", "kilometers",
            "km", "mi"
        },
        "physical": {
            "physical", "terrain", "mountain", "mountains", "river", "rivers",
            "forest", "forests", "plain", "plains", "coast", "coasts",
            "coastline", "delta", "desert", "deserts", "valley", "valleys",
            "plateau", "plateaus"
        },
        "economy": {
            "economy", "economic", "industry", "industries", "trade",
            "jobs", "agriculture", "business", "development", "income"
        },
        "history": {
            "history", "historical", "past", "colonial", "empire", "war",
            "independence", "ancient", "modern"
        },
        "travel": {
            "travel", "trip", "visit", "tourism", "tourist", "vacation",
            "journey", "route", "landmark", "landmarks"
        },
        "maps": {
            "map", "maps", "atlas", "location", "located", "where",
            "border", "borders", "direction", "directions", "position"
        }
    }

    _GENERAL_FOLLOWUPS = [
        "Can you say more about what interests you there?",
        "What part of that are you most curious about?",
        "Is your interest more about people, place, or environment?",
        "Are you thinking about culture, climate, cities, or landscape?",
        "What made you curious about that in the first place?"
    ]

    _STOPWORDS = {
        "the", "a", "an", "and", "or", "but", "if", "then", "so", "because",
        "i", "me", "my", "mine", "you", "your", "yours", "we", "our", "ours",
        "they", "them", "their", "is", "are", "was", "were", "be", "being",
        "been", "am", "to", "of", "in", "on", "for", "with", "about", "into",
        "from", "at", "by", "as", "it", "this", "that", "these", "those",
        "do", "does", "did", "can", "could", "would", "should", "want",
        "like", "tell", "know", "learn", "more", "very", "really", "just"
    }

    def load(self, path):
        key = None
        decomp = None

        p = Path(path)
        if not p.exists():
            p = Path(__file__).resolve().with_name(path)

        with p.open(encoding="utf-8") as file:
            for line in file:
                s = line.strip()
                if not s or s.startswith('#'):
                    continue
                if ':' not in s:
                    continue

                tag, content = [part.strip() for part in s.split(':', 1)]

                if tag == 'initial':
                    self.initials.append(content)
                elif tag == 'final':
                    self.finals.append(content)
                elif tag == 'quit':
                    self.quits.append(content.lower())
                elif tag == 'pre':
                    parts = content.split(' ')
                    self.pres[parts[0]] = parts[1:]
                elif tag == 'post':
                    parts = content.split(' ')
                    self.posts[parts[0]] = parts[1:]
                elif tag == 'synon':
                    parts = content.split(' ')
                    self.synons[parts[0]] = parts
                elif tag == 'key':
                    parts = content.split(' ')
                    word = parts[0]
                    weight = int(parts[1]) if len(parts) > 1 else 1
                    key = Key(word, weight, [])
                    self.keys[word] = key
                elif tag == 'decomp':
                    parts = content.split(' ')
                    save = False
                    if parts[0] == '$':
                        save = True
                        parts = parts[1:]
                    decomp = Decomp(parts, save, [])
                    if key is not None:
                        key.decomps.append(decomp)
                elif tag == 'reasmb':
                    parts = content.split(' ')
                    if decomp is not None:
                        decomp.reasmbs.append(parts)

        if 'xnone' not in self.keys:
            self.keys['xnone'] = Key('xnone', 0, [Decomp(['*'], False, [
                ["Tell", "me", "more", "about", "that", "."]
            ])])

    def _tokenize(self, text):
        return re.findall(r"[A-Za-z][A-Za-z\-']*", text)

    def _sub(self, words, sub_map):
        output = []
        for word in words:
            lw = word.lower()
            if lw in sub_map:
                output.extend(sub_map[lw])
            else:
                output.append(word)
        return output

    def _join(self, words):
        if not words:
            return ""
        text = " ".join(words)
        text = re.sub(r"\s+([,.!?;:])", r"\1", text)
        text = re.sub(r"\bi\b", "I", text)
        return text

    def _next_reasmb(self, decomp):
        if not decomp.reasmbs:
            return ["Please", "go", "on", "."]
        index = decomp.next_reasmb_index
        result = decomp.reasmbs[index]
        decomp.next_reasmb_index = (index + 1) % len(decomp.reasmbs)
        return result

    def _match_decomp_r(self, parts, words, results):
        if not parts and not words:
            return True
        if not parts:
            return False
        if parts[0] == '*':
            if len(parts) == 1:
                results.append(words)
                return True
            for i in range(len(words), -1, -1):
                results.append(words[:i])
                if self._match_decomp_r(parts[1:], words[i:], results):
                    return True
                results.pop()
            return False
        elif not words:
            return False
        elif parts[0].startswith('@'):
            root = parts[0][1:]
            if root not in self.synons:
                return False
            if words[0].lower() in self.synons[root]:
                results.append([words[0]])
                return self._match_decomp_r(parts[1:], words[1:], results)
            return False
        else:
            if parts[0].lower() != words[0].lower():
                return False
            return self._match_decomp_r(parts[1:], words[1:], results)

    def _match_decomp(self, words, decomp):
        results = []
        if self._match_decomp_r(decomp.parts, words, results):
            return results
        return None

    def _reassemble(self, reasmb, results):
        output = []
        for token in reasmb:
            if re.fullmatch(r"\(\d+\)", token):
                index = int(token[1:-1]) - 1
                if 0 <= index < len(results):
                    words = self._sub(results[index], self.posts)
                    output.extend(words)
            else:
                output.append(token)
        return output

    def _match_key(self, words, key):
        for decomp in key.decomps:
            results = self._match_decomp(words, decomp)
            if results is None:
                continue

            reasmb = self._next_reasmb(decomp)
            if decomp.save:
                self.memory.append(self._join(self._reassemble(reasmb, results)))
                continue

            return self._reassemble(reasmb, results)
        return None

    def _avoid_repetition(self, response):
        normalized = response.strip().lower()
        if normalized in self.response_history:
            return False
        self.response_history.append(normalized)
        if len(self.response_history) > 12:
            self.response_history.pop(0)
        return True

    def _extract_keywords(self, text):
        words = re.findall(r"\b[a-zA-Z][a-zA-Z\-']+\b", text.lower())
        result = []
        for w in words:
            if w not in self._STOPWORDS and len(w) > 2:
                result.append(w)
        seen = set()
        ordered = []
        for w in result:
            if w not in seen:
                seen.add(w)
                ordered.append(w)
        return ordered[:8]

    def _detect_country(self, text):
        t = text.lower().strip()

        for alias, canon in sorted(self._COUNTRY_ALIASES.items(), key=lambda x: -len(x[0])):
            if re.search(r'\b' + re.escape(alias) + r'\b', t):
                return canon

        for continent, countries in self._CONTINENTS.items():
            for country in countries:
                if re.search(r'\b' + re.escape(country.lower()) + r'\b', t):
                    return country

        return None

    def _detect_continent(self, text):
        t = text.lower().strip()
        for alias, canon in sorted(self._CONTINENT_ALIASES.items(), key=lambda x: -len(x[0])):
            if re.search(r'\b' + re.escape(alias) + r'\b', t):
                return canon
        return None

    def _country_to_continent(self, country):
        for continent, countries in self._CONTINENTS.items():
            if country in countries:
                return continent
        return None

    def _detect_region(self, text):
        t = text.lower()
        for kw, region in self._REGION_KEYWORDS.items():
            if re.search(r'\b' + re.escape(kw) + r'\b', t):
                return region
        return None

    def _detect_subtopic(self, text):
        t = text.lower()

        hits = []
        for topic, kws in self._SUBTOPIC_KEYWORDS.items():
            score = 0
            for kw in kws:
                if re.search(r'\b' + re.escape(kw) + r'\b', t):
                    score += 1
            if score > 0:
                hits.append((score, topic))

        if not hits:
            return None

        hits.sort(reverse=True)
        return hits[0][1]

    def _build_place_prompt(self, place):
        continent = self._country_to_continent(place)
        templates = [
            f"What interests you most about {place}?",
            f"{place} is in {continent}. Are you more curious about its climate, culture, cities, or physical geography?" if continent else f"What part of {place} would you like to explore first?",
            f"When you think about {place}, are you thinking more about people, landscape, or travel?",
            f"Would you like to focus on history, daily life, environment, or major places in {place}?"
        ]
        return self._pick_fresh(templates)

    def _build_continent_prompt(self, continent):
        samples = self._CONTINENTS.get(continent, [])
        sample_text = ", ".join(samples[:4]) if samples else "many different places"
        templates = [
            f"What part of {continent} interests you most?",
            f"{continent} includes places like {sample_text}. Are you thinking about one country, or the region more generally?",
            f"Are you more interested in the climate, cultures, cities, or landscapes of {continent}?",
            f"Would you like to compare different countries in {continent}, or focus on one?"
        ]
        return self._pick_fresh(templates)

    def _build_subtopic_prompt(self, place, subtopic, user_keywords):
        place_text = place if place else "that place"

        topic_map = {
            "climate": [
                f"What kind of climate in {place_text} are you thinking about—heat, rainfall, seasons, or storms?",
                f"How do you think climate affects life in {place_text}?",
                f"Are you interested in everyday weather, seasonal change, or extreme climate in {place_text}?"
            ],
            "culture": [
                f"What part of the culture of {place_text} interests you most—language, food, religion, traditions, or daily life?",
                f"How do you imagine culture shapes life in {place_text}?",
                f"What kinds of people, customs, or traditions are you thinking about in {place_text}?"
            ],
            "cities": [
                f"Are you thinking about major cities, capital cities, or how people live in urban areas of {place_text}?",
                f"What do you want to know about cities in {place_text}—size, importance, daily life, or location?",
                f"Do you want to compare cities in {place_text}, or focus on one major city?"
            ],
            "distance": [
                f"Between which places do you want to think about distance in {place_text}?",
                f"Are you thinking about travel distance, city-to-city distance, or how spread out {place_text} is?",
                f"What makes distance interesting to you in {place_text}—travel, scale, or regional differences?"
            ],
            "physical": [
                f"Are you thinking about rivers, mountains, coasts, plains, forests, or another landscape feature in {place_text}?",
                f"How do you think physical geography shapes life in {place_text}?",
                f"What landscape feature stands out to you most in {place_text}?"
            ],
            "economy": [
                f"What part of the economy of {place_text} interests you—jobs, trade, agriculture, development, or industry?",
                f"How do you think geography affects the economy in {place_text}?",
                f"Are you more curious about work, resources, trade, or living standards in {place_text}?"
            ],
            "history": [
                f"What period of the history of {place_text} are you thinking about?",
                f"Are you interested in ancient history, modern history, independence, or cultural change in {place_text}?",
                f"How do you think history shaped the place we see today in {place_text}?"
            ],
            "travel": [
                f"If you visited {place_text}, what would you want to experience first?",
                f"Are you thinking about landmarks, routes, daily life, or famous places in {place_text}?",
                f"What kind of travel experience do you want in {place_text}?"
            ],
            "maps": [
                f"Do you want a location overview of {place_text}, or are you thinking about borders, nearby places, or direction?",
                f"Are you trying to picture where {place_text} is, or how different parts of it look?",
                f"What map question do you have in mind about {place_text}?"
            ]
        }

        responses = topic_map.get(subtopic, [
            f"What about {subtopic} in {place_text} interests you most?"
        ])

        if user_keywords:
            chosen = random.choice(user_keywords[:min(3, len(user_keywords))])
            responses.append(f"You mentioned {chosen}. How does that connect to what you want to know about {place_text}?")

        return self._pick_fresh(responses)

    def _build_keyword_followup(self, user_keywords):
        if not user_keywords:
            return self._pick_fresh(self._GENERAL_FOLLOWUPS)

        key = random.choice(user_keywords[:min(4, len(user_keywords))])
        templates = [
            f"You mentioned {key}. What about that stands out to you?",
            f"When you say {key}, what are you thinking about exactly?",
            f"How does {key} connect to what you want to explore?",
            f"Would you like to focus more on {key}, or connect it to a specific place?"
        ]
        return self._pick_fresh(templates)

    def _build_contextual_followup(self):
        country = self.geo_state.get("country")
        continent = self.geo_state.get("continent")
        subtopic = self.geo_state.get("subtopic")
        keywords = self.geo_state.get("keywords", [])

        if country and subtopic:
            return self._build_subtopic_prompt(country, subtopic, keywords)
        if country:
            return self._build_place_prompt(country)
        if continent:
            return self._build_continent_prompt(continent)
        return self._build_keyword_followup(keywords)

    def _pick_fresh(self, candidates):
        fresh = [c for c in candidates if c.strip().lower() not in self.response_history]
        if fresh:
            choice = random.choice(fresh)
        else:
            choice = random.choice(candidates)
        self._avoid_repetition(choice)
        return choice

    def _geo_context_response(self, text):
        raw = text.strip()
        if not raw:
            return None

        lower = raw.lower()

        country = self._detect_country(raw)
        continent = self._detect_continent(raw)
        subtopic = self._detect_subtopic(raw)
        region = self._detect_region(raw)
        keywords = self._extract_keywords(raw)

        self.geo_state["last_user_input"] = raw
        self.geo_state["keywords"] = keywords

        if country:
            self.geo_state["country"] = country
            self.geo_state["continent"] = self._country_to_continent(country)
            self.geo_state["region"] = region
            if subtopic:
                self.geo_state["subtopic"] = subtopic
            self.geo_state["turn"] += 1

            if subtopic:
                return self._build_subtopic_prompt(country, subtopic, keywords).split()

            return self._build_place_prompt(country).split()

        if continent:
            self.geo_state["continent"] = continent
            self.geo_state["country"] = None
            self.geo_state["region"] = region
            if subtopic:
                self.geo_state["subtopic"] = subtopic
            self.geo_state["turn"] += 1

            if subtopic:
                return self._build_subtopic_prompt(continent, subtopic, keywords).split()

            return self._build_continent_prompt(continent).split()

        # If user gives a subtopic without a new place, keep prior context
        if subtopic and (self.geo_state.get("country") or self.geo_state.get("continent")):
            self.geo_state["subtopic"] = subtopic
            self.geo_state["turn"] += 1
            place = self.geo_state.get("country") or self.geo_state.get("continent")
            return self._build_subtopic_prompt(place, subtopic, keywords).split()

        # If user is continuing a conversation with descriptive sentence
        if self.geo_state.get("country") or self.geo_state.get("continent"):
            continuation_cues = [
                "it", "there", "that place", "those people", "its", "their",
                "i think", "i feel", "i want", "i wonder", "maybe", "probably"
            ]
            if any(cue in lower for cue in continuation_cues) or len(keywords) >= 2:
                self.geo_state["turn"] += 1
                return self._build_contextual_followup().split()

        return None

    def respond(self, text):
        if text is None:
            return None

        raw = text.strip()
        if not raw:
            return self._pick_fresh([
                "Please say a little more.",
                "Tell me what place or topic you want to explore.",
                "What are you curious about right now?"
            ])

        if raw.lower() in self.quits:
            return None

        geo_output = self._geo_context_response(raw)
        if geo_output:
            return self._join(geo_output)

        words = self._tokenize(raw)
        words = self._sub(words, self.pres)

        keys = [self.keys[w.lower()] for w in words if w.lower() in self.keys]
        keys = sorted(keys, key=lambda k: -k.weight)

        output = None
        for key in keys:
            output = self._match_key(words, key)
            if output:
                text_out = self._join(output)
                if self._avoid_repetition(text_out):
                    return text_out
                break

        if self.memory:
            remembered = self.memory.pop(0)
            if self._avoid_repetition(remembered):
                return remembered

        keywords = self._extract_keywords(raw)
        self.geo_state["keywords"] = keywords

        return self._build_keyword_followup(keywords)

    def initial(self):
        if self.initials:
            return random.choice(self.initials)
        return "Hello. Tell me about a place or geography topic you are interested in."

    def final(self):
        if self.finals:
            return random.choice(self.finals)
        return "Goodbye."

    def run(self):
        print(self.initial())

        while True:
            sent = input("> ")
            output = self.respond(sent)
            if output is None:
                break
            print(output)

        print(self.final())


def main():
    eliza = Eliza()
    eliza.load("doctor.txt")
    eliza.run()


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    main()