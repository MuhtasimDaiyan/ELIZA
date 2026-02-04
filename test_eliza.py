import unittest
import eliza_geobot as eliza


class GeoBotTest(unittest.TestCase):
    def test_geo_conversation_usa_chain(self):
        bot = eliza.Eliza()
        bot.load('doctor.txt')

        # Start a USA-focused thread
        r1 = bot.respond('USA')
        self.assertTrue(r1.startswith('Which part of the United States'))

        r2 = bot.respond('Midwest')
        self.assertIn('Nice—Midwest.', r2)

        r3 = bot.respond('distances')
        self.assertIn('Between which two places in Midwest', r3)

        r4 = bot.respond('what kind of people do you expect?')
        self.assertIn('people or cultures', r4)
        self.assertIn('Midwest', r4)

    def test_other_countries_trigger_specific_questions(self):
        bot = eliza.Eliza()
        bot.load('doctor.txt')

        r1 = bot.respond('Japan')
        self.assertTrue(
            r1.startswith('Which part of Japan') or r1.startswith('Do you want to focus on Japan')
        )

        r2 = bot.respond('Canada')
        self.assertTrue(
            r2.startswith('Are you thinking about Canada') or 'Canada' in r2
        )

    def test_general_geo_prompts_still_work(self):
        bot = eliza.Eliza()
        bot.load('doctor_geobot.txt')

        self.assertIn(bot.initial(), [
            "Hi! I'm GeoBot. Tell me a place you're curious about (a country, city, or region).",
        ])

        hello = bot.respond('Hello')
        self.assertTrue(isinstance(hello, str) and len(hello) > 0)

        self.assertIn(bot.final(), [
            "Goodbye! Safe travels and happy exploring.",
        ])


if __name__ == '__main__':
    unittest.main()
