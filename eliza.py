import logging
import random
import re
from pathlib import Path
from collections import namedtuple

# Fix Python2/Python3 incompatibility
try: input = raw_input
except NameError: pass

log = logging.getLogger(__name__)

LAST_TOPIC = {
    "country": None,
    "region": None,
    "category": None,
    "subcategory": None
}

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

        # Lightweight conversation context for GeoBot
        self.geo_state = {
            'country': None,
            'region': None,
            'subtopic': None,
            'turn': 0,
        }

    # Country/topic dialog
    _COUNTRY_ALIASES = {
        # North America
        'united states': 'United States',
        'united states of america': 'United States',
        'usa': 'United States',
        'us': 'United States',
        'u.s.': 'United States',
        'u.s.a.': 'United States',
        'america': 'United States',
        'canada': 'Canada',
        'mexico': 'Mexico',
        # Europe
        'united kingdom': 'United Kingdom',
        'uk': 'United Kingdom',
        'u.k.': 'United Kingdom',
        'britain': 'United Kingdom',
        'great britain': 'United Kingdom',
        'england': 'United Kingdom',
        'france': 'France',
        'germany': 'Germany',
        'italy': 'Italy',
        'spain': 'Spain',
        # Asia
        'japan': 'Japan',
        'china': 'China',
        'people\'s republic of china': 'China',
        'prc': 'China',
        'india': 'India',
        'south korea': 'South Korea',
        'korea': 'South Korea',
        'republic of korea': 'South Korea',
        # Middle East / Africa
        'uae': 'United Arab Emirates',
        'united arab emirates': 'United Arab Emirates',
        'egypt': 'Egypt',
        'south africa': 'South Africa',
        # South America
        'brazil': 'Brazil',
        'argentina': 'Argentina',
        # Oceania
        'australia': 'Australia',
        'new zealand': 'New Zealand',
        # A few common extras
        'bangladesh': 'Bangladesh',
    }

    _US_REGIONS = {
        'west coast': 'West Coast',
        'pacific coast': 'West Coast',
        'south': 'South',
        'southeast': 'South',
        'midwest': 'Midwest',
        'northeast': 'Northeast',
        'southwest': 'Southwest',
        'pnw': 'Pacific Northwest',
        'pacific northwest': 'Pacific Northwest',
        'mountain west': 'Mountain West',
    }

    _COUNTRY_QUESTIONS = {
        'United States': [
            "Which part of the United States are you thinking about—the West Coast, the South, the Midwest, the Northeast, the Southwest, or the Pacific Northwest?",
            "Are you thinking more about the U.S. physical geography (mountains, rivers, climate) or human geography (people, culture, economy, cities)?",
            "What do you want to compare in the U.S.—distances, climate patterns, major cities, or landmarks?",
        ],
        'Canada': [
            "Are you thinking about Canada\'s regions (Atlantic, Quebec, Ontario, Prairies, British Columbia, or the North)?",
            "Do you want to focus on distances between cities, climate zones, or culture and languages in Canada?",
            "Which part of Canada interests you most—mountains, lakes, forests, or urban areas?",
        ],
        'Mexico': [
            "Are you thinking about northern Mexico, central Mexico, the Yucatán Peninsula, or the Pacific coast?",
            "Do you want to explore Mexico\'s physical geography (volcanoes, deserts, coasts) or human geography (cities, culture, migration, economy)?",
            "Are you curious about distances between cities, climate, or famous landmarks in Mexico?",
        ],
        'Japan': [
            "Which part of Japan—Hokkaido, Honshu, Shikoku, Kyushu, or Okinawa—are you thinking about?",
            "Do you want to focus on Japan\'s climate and terrain, or on cities, culture, and population patterns?",
            "Are you curious about travel distances, major cities, or physical features like mountains and coastlines in Japan?",
        ],
        'France': [
            "Are you thinking about northern France, the Paris region, the Alps, the Atlantic coast, or the Mediterranean coast?",
            "Do you want to focus on distances and travel routes, climate, or cultural/human geography in France?",
            "Which details matter most to you—cities, borders, rivers/mountains, or landmarks in France?",
        ],
        'United Kingdom': [
            "Which part of the UK—England, Scotland, Wales, or Northern Ireland—are you thinking about?",
            "Do you want to explore the UK\'s cities and culture (human geography) or its landscapes and climate (physical geography)?",
            "Are you curious about distances between cities, regional identities, or famous landmarks in the UK?",
        ],
        'China': [
            "Are you thinking about coastal China, central China, western China, or the northeast?",
            "Do you want to focus on human geography (cities, languages, economy) or physical geography (rivers, mountains, climate) in China?",
            "Are you curious about distances between major cities, climate zones, or natural landmarks in China?",
        ],
        'India': [
            "Which part of India—north, south, east, west, or the northeast—are you thinking about?",
            "Do you want to focus on physical geography (Himalayas, rivers, monsoons) or human geography (languages, cities, culture, economy) in India?",
            "Are you curious about distances between cities, climate patterns, or major landmarks in India?",
        ],
        'Brazil': [
            "Are you thinking about Brazil\'s Amazon region, the northeast, the southeast (São Paulo/Rio), or the south?",
            "Do you want to focus on physical geography (rainforest, rivers, coastline) or human geography (cities, culture, economy) in Brazil?",
            "Are you curious about distances between cities, climate, or famous landmarks in Brazil?",
        ],
        'Australia': [
            "Which part of Australia—east coast, west coast, the Outback, or the north—are you thinking about?",
            "Do you want to focus on physical geography (deserts, reefs, coasts) or human geography (cities, population, culture) in Australia?",
            "Are you curious about distances, climate, or major landmarks in Australia?",
        ],
        'Bangladesh': [
            "Are you thinking about Dhaka, Chittagong, Sylhet, Khulna, Rajshahi, or the coastal delta areas?",
            "Do you want to focus on rivers and floodplains (physical geography) or cities, culture, and language (human geography) in Bangladesh?",
            "Are you curious about distances between cities, climate/monsoon seasons, or major landmarks in Bangladesh?",
        ],
    }

    _SUBTOPIC_KEYWORDS = {
        'distances': {'distance', 'distances', 'far', 'close', 'near', 'miles', 'kilometers', 'km', 'mi', 'drive', 'road trip', 'travel time'},
        'climate': {'climate', 'weather', 'temperature', 'rain', 'snow', 'humid', 'humidity', 'dry', 'monsoon', 'seasons'},
        'capitals': {'capital', 'capitals', 'capital city'},
        'maps': {'map', 'maps', 'atlas', 'location', 'where', 'coordinate', 'coordinates'},
        'physical': {'physical', 'terrain', 'mountain', 'mountains', 'river', 'rivers', 'coast', 'coasts', 'desert', 'deserts', 'plains', 'forest', 'forests'},
        'human': {'human', 'people', 'culture', 'languages', 'language', 'cities', 'population', 'economy', 'migration', 'traditions', 'religion', 'food'},
    }

    def _detect_country(self, text: str):
        t = text.strip().lower()
        # direct match
        if t in self._COUNTRY_ALIASES:
            return self._COUNTRY_ALIASES[t]
        # word-boundary match
        for alias, canon in self._COUNTRY_ALIASES.items():
            if re.search(r'' + re.escape(alias) + r'', t):
                return canon
        return None

    def _detect_us_region(self, text: str):
        t = text.strip().lower()
        if t in self._US_REGIONS:
            return self._US_REGIONS[t]
        for k, v in self._US_REGIONS.items():
            if re.search(r'' + re.escape(k) + r'', t):
                return v
        return None

    def _detect_subtopic(self, text: str):
        t = text.strip().lower()
        for topic, kws in self._SUBTOPIC_KEYWORDS.items():
            for kw in kws:
                if kw in t:
                    return topic
        return None

    def _geo_followup(self):
        country = self.geo_state.get('country')
        region = self.geo_state.get('region')
        subtopic = self.geo_state.get('subtopic')

        place = region if (country == 'United States' and region) else country
        if not place:
            return None

        if subtopic == 'distances':
            return f"Between which two places in {place} do you want to compare distance—cities, landmarks, or states/provinces?"
        if subtopic == 'climate':
            return f"What kind of climate are you thinking about in {place}—hot/cold, wet/dry, seasonal changes, or extreme weather?"
        if subtopic == 'capitals':
            return f"Are you asking about the capital of {place}, or comparing capitals across regions?"
        if subtopic == 'maps':
            return f"Do you want a location overview of {place}, or directions/relative position to nearby places?"
        if subtopic == 'physical':
            return f"Physical geography in {place}: are you thinking mountains, rivers, plains, coasts, or climate zones?"
        if subtopic == 'human':
            return f"Human geography in {place}: languages, food, migration, economy, or regional culture—what are you most curious about?"
        # default
        return f"What would you like to explore about {place}—maps, capitals, climate, distances, physical geography, or human geography?"

    def _geo_context_response(self, text: str):
        raw = text.strip()
        if not raw:
            return None

        t = raw.lower()

        country = self._detect_country(raw)
        if country:
            self.geo_state['country'] = country
            self.geo_state['region'] = None
            self.geo_state['subtopic'] = None
            self.geo_state['turn'] += 1
            qs = self._COUNTRY_QUESTIONS.get(country, [
                f"What about {country} interests you—maps, capitals, climate, distances, physical geography, or human geography?"
            ])
            q = qs[(self.geo_state['turn'] - 1) % len(qs)]
            return q.split(' ')

        # If we are already in a country context, keep the conversation going.
        if self.geo_state.get('country'):
            country = self.geo_state['country']

            # USA region selection
            if country == 'United States' and not self.geo_state.get('region'):
                region = self._detect_us_region(raw)
                if region:
                    self.geo_state['region'] = region
                    self.geo_state['turn'] += 1
                    return f"Nice—{region}. Are you curious about maps, capitals, climate, distances, physical geography, or human geography there?".split(' ')

            # Special case: user asks about people/culture expectations
            if re.search(r'\b(kind of people|what kind of people|people do you expect|culture|cultural)\b', t):
                self.geo_state['subtopic'] = 'human'
                self.geo_state['turn'] += 1
                place = self.geo_state.get('region') if (country == 'United States' and self.geo_state.get('region')) else country
                return f"What kinds of people or cultures do you expect in {place}, and what experiences shaped that expectation?".split(' ')

            # Subtopic selection
            subtopic = self._detect_subtopic(raw)
            if subtopic and subtopic != self.geo_state.get('subtopic'):
                self.geo_state['subtopic'] = subtopic
                self.geo_state['turn'] += 1
                return self._geo_followup().split(' ')
            # Otherwise: gentle follow-up to continue
            self.geo_state['turn'] += 1
            return self._geo_followup().split(' ')

        return None

    def load(self, path):
        key = None
        decomp = None
        p = Path(path)
        if not p.exists():
            p = Path(__file__).resolve().with_name(path)
        with p.open() as file:
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
                    self.quits.append(content)
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
                    key.decomps.append(decomp)
                elif tag == 'reasmb':
                    parts = content.split(' ')
                    decomp.reasmbs.append(parts)

    def _match_decomp_r(self, parts, words, results):
        if not parts and not words:
            return True
        if not parts or (not words and parts != ['*']):
            return False
        if parts[0] == '*':
            for index in range(len(words), -1, -1):
                results.append(words[:index])
                if self._match_decomp_r(parts[1:], words[index:], results):
                    return True
                results.pop()
            return False
        elif parts[0].startswith('@'):
            root = parts[0][1:]
            if not root in self.synons:
                raise ValueError("Unknown synonym root {}".format(root))
            if not words[0].lower() in self.synons[root]:
                return False
            results.append([words[0]])
            return self._match_decomp_r(parts[1:], words[1:], results)
        elif parts[0].lower() != words[0].lower():
            return False
        else:
            return self._match_decomp_r(parts[1:], words[1:], results)

    def _match_decomp(self, parts, words):
        results = []
        if self._match_decomp_r(parts, words, results):
            return results
        return None

    def _next_reasmb(self, decomp):
        index = decomp.next_reasmb_index
        result = decomp.reasmbs[index % len(decomp.reasmbs)]
        decomp.next_reasmb_index = index + 1
        return result

    def _reassemble(self, reasmb, results):
        output = []
        for reword in reasmb:
            if not reword:
                continue
            if reword[0] == '(' and reword[-1] == ')':
                index = int(reword[1:-1])
                if index < 1 or index > len(results):
                    raise ValueError("Invalid result index {}".format(index))
                insert = results[index - 1]
                for punct in [',', '.', ';']:
                    if punct in insert:
                        insert = insert[:insert.index(punct)]
                output.extend(insert)
            else:
                output.append(reword)
        return output

    def _sub(self, words, sub):
        output = []
        for word in words:
            word_lower = word.lower()
            if word_lower in sub:
                output.extend(sub[word_lower])
            else:
                output.append(word)
        return output

    def _match_key(self, words, key):
        for decomp in key.decomps:
            results = self._match_decomp(decomp.parts, words)
            if results is None:
                log.debug('Decomp did not match: %s', decomp.parts)
                continue
            log.debug('Decomp matched: %s', decomp.parts)
            log.debug('Decomp results: %s', results)
            results = [self._sub(words, self.posts) for words in results]
            log.debug('Decomp results after posts: %s', results)
            reasmb = self._next_reasmb(decomp)
            log.debug('Using reassembly: %s', reasmb)
            if reasmb[0] == 'goto':
                goto_key = reasmb[1]
                if not goto_key in self.keys:
                    raise ValueError("Invalid goto key {}".format(goto_key))
                log.debug('Goto key: %s', goto_key)
                return self._match_key(words, self.keys[goto_key])
            output = self._reassemble(reasmb, results)
            if decomp.save:
                self.memory.append(output)
                log.debug('Saved to memory: %s', output)
                continue
            return output
        return None

    def respond(self, text):
        if text.lower() in self.quits:
            return None

        geo = self._geo_context_response(text)
        if geo:
            return " ".join(geo)

        text = re.sub(r'\s*\.+\s*', ' . ', text)
        text = re.sub(r'\s*,+\s*', ' , ', text)
        text = re.sub(r'\s*;+\s*', ' ; ', text)
        log.debug('After punctuation cleanup: %s', text)

        words = [w for w in text.split(' ') if w]
        log.debug('Input: %s', words)

        words = self._sub(words, self.pres)
        log.debug('After pre-substitution: %s', words)

        keys = [self.keys[w.lower()] for w in words if w.lower() in self.keys]
        keys = sorted(keys, key=lambda k: -k.weight)
        log.debug('Sorted keys: %s', [(k.word, k.weight) for k in keys])

        output = None

        for key in keys:
            output = self._match_key(words, key)
            if output:
                log.debug('Output from key: %s', output)
                break
        if not output:
            if self.memory:
                index = random.randrange(len(self.memory))
                output = self.memory.pop(index)
                log.debug('Output from memory: %s', output)
            else:
                output = self._next_reasmb(self.keys['xnone'].decomps[0])
                log.debug('Output from xnone: %s', output)
        text_l = text.lower()

        # Continue food conversation naturally
        if LAST_TOPIC["category"] == "human geography" and LAST_TOPIC["subcategory"] == "food":
            if any(w in text_l for w in ["food", "eat", "cuisine", "dishes", "meals", "over there"]):
                return (
                    f"What kinds of food do you expect in the {LAST_TOPIC['region']}? "
                    f"Are you thinking more about street food, seafood, or regional specialties?"
                )

            if any(w in text_l for w in ["expect", "think", "guess", "assume"]):
                return (
                    "What do you think you might enjoy about that food—and is there anything you think you might not like?"
                )

            return (
                "Do you think food culture reflects the people and history of a place? "
                "What do you imagine influences West Coast cuisine the most?"
            )


        return " ".join(output)

    def initial(self):
        return random.choice(self.initials)

    def final(self):
        return random.choice(self.finals)

    def run(self):
        print(self.initial())

        while True:
            sent = input('> ')

            output = self.respond(sent)
            if output is None:
                break

            print(output)

        print(self.final())


def main():
    eliza = Eliza()
    eliza.load('doctor.txt')
    eliza.run()

if __name__ == '__main__':
    logging.basicConfig()
    main()
