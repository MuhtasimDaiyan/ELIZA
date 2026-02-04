GeoBot (ELIZA-Based Geography/Travel Chatbot)

INTRODUCTION:
GeoBot is a modified version of the classic ELIZA chatbot that has been transformed from a psychiatrist-style conversation agent into a geography-focused conversational bot. Instead of discussing feelings, GeoBot guides the user through an interactive discussion about countries, regions, and human geography (culture, food, languages, etc.).

The bot aska follow-up questions and continuea a topic (for example, continuing a discussion about food culture in the U.S. West Coast instead of repeating the same menu of options).
Features

FEATURES:
Country detection - Recognizes country names and common aliases (e.g., USA, United States, UK, Japan, France, Bangladesh, etc.)

Region-specific prompts for the United States - After selecting “USA,” GeoBot asks about regions (West Coast, Midwest, Northeast, etc.)

Geographic subtopics - Maps, Capitals, Climate, Physical Geography (mountains, rivers, coasts, deserts, etc.), Human Geography (people, culture, food)

Context aware conversation: GeoBot remembers the current country of conversation, region (for the U.S.), topic (physical vs human geography), and subtopics (e.g., food, languages)

Human geography follow-ups: If the user selects “food,” GeoBot asks deeper questions like:
- What kinds of food do you expect there?
- What do you think you might enjoy or dislike?
- How might food culture reflect the people of the region?

HOW TO RUN: 
- Make sure you have Python 3 installed.
- Download the project folder and extract the files
- run python eliza.py (the python command depends on which version of python you have installed. Use python --version to check which version you have installed).

EXAMPLE CONVERSATION:
Hi! I'm GeoBot. Tell me a place you're curious about (a country, city, or region).
> USA
Which part of the United States are you thinking about—the West Coast, the South, the Midwest, the Northeast, the Southwest, or the Pacific Northwest?
> West Coast
Nice—West Coast. Are you curious about maps, capitals, climate, distances, physical geography, or human geography there?
> human geography
Human geography in West Coast: languages, food, migration, economy, or regional culture—what are you most curious about?
> food
What kinds of food do you expect in the West Coast? Are you imagining seafood, street food, comfort food, or fusion cuisine?
> seafood and asian food

IMPLEMENTATION NOTES:
- Built on top of the classic ELIZA pattern-matching system.
- Adds a lightweight geo_state to track conversation context.
- Uses keyword detection to infer geography topics and human geography subcategories.


FILE OVERVIEW:
eliza.py – Main chatbot logic with GeoBot extensions
doctor.txt – Script defining responses, keys, and patterns (converted from therapist to geography prompts)
test_eliza.py (optional) – Unit tests for GeoBot behavior

CITATIONS:
http://chayden.net/eliza/Eliza.html
git@github.com:wadetb/eliza.git