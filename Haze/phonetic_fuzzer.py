#!/usr/bin/env python3
"""
Direct Cross-Language Phonetic Word hazer
Transform between any two languages without English intermediary
"""

import difflib
import re
import os
from anthropic import Anthropic
from deep_translator import GoogleTranslator
from typing import List, Tuple, Optional


# Get API key from environment variable
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


def get_api_key():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is required")
    return api_key


class Hazer:
    def __init__(self):
        self.word_lists = {}

    def soundex(self, word: str) -> str:
        """Generate Soundex code for phonetic similarity."""
        if not word:
            return "0000"

        word = word.upper()
        soundex_code = word[0]

        mapping = {
            "B": "1",
            "F": "1",
            "P": "1",
            "V": "1",
            "C": "2",
            "G": "2",
            "J": "2",
            "K": "2",
            "Q": "2",
            "S": "2",
            "X": "2",
            "Z": "2",
            "D": "3",
            "T": "3",
            "L": "4",
            "M": "5",
            "N": "5",
            "R": "6",
        }

        for char in word[1:]:
            if char in mapping:
                code = mapping[char]
                if code != soundex_code[-1]:
                    soundex_code += code

        soundex_code = (soundex_code + "0000")[:4]
        return soundex_code

    def metaphone_simple(self, word: str) -> str:
        """Simplified Metaphone algorithm."""
        if not word:
            return ""

        word = word.upper().replace("PH", "F").replace("GH", "F")
        word = word.replace("CK", "K").replace("SCH", "SK")

        metaphone = ""
        prev_char = ""

        for char in word:
            if char in "AEIOU":
                if not metaphone:
                    metaphone += char
            elif char != prev_char:
                metaphone += char
            prev_char = char

        return metaphone[:6]

    def phonetic_distance(self, word1: str, word2: str) -> float:
        """Calculate phonetic distance between two words."""
        w1, w2 = word1.lower(), word2.lower()

        soundex1, soundex2 = self.soundex(w1), self.soundex(w2)
        soundex_sim = difflib.SequenceMatcher(None, soundex1, soundex2).ratio()

        meta1, meta2 = self.metaphone_simple(w1), self.metaphone_simple(w2)
        metaphone_sim = difflib.SequenceMatcher(None, meta1, meta2).ratio()

        string_sim = difflib.SequenceMatcher(None, w1, w2).ratio()

        len_penalty = abs(len(w1) - len(w2)) / max(len(w1), len(w2), 1)

        combined_sim = (
            soundex_sim * 0.4 + metaphone_sim * 0.4 + string_sim * 0.2
        ) - len_penalty * 0.1

        return 1 - combined_sim

    def load_word_list(self, language: str) -> List[str]:
        """Load word list for the specified language."""
        if language in self.word_lists:
            return self.word_lists[language]

        words = self._try_frequency_lists(language)
        if words:
            self.word_lists[language] = words
            return words

        words = self._try_online_wordlist(language)
        if words:
            self.word_lists[language] = words
            return words

        return self._get_builtin_wordlist(language)

    def _try_frequency_lists(self, language: str) -> List[str]:
        """Load most common words from frequency lists."""
        try:
            import requests

            freq_urls = {
                "english": "https://raw.githubusercontent.com/first20hours/google-10000-english/master/google-10000-english-no-swears.txt",
                "spanish": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2016/es/es_50k.txt",
                "french": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2016/fr/fr_50k.txt",
                "german": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2016/de/de_50k.txt",
                "italian": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2016/it/it_50k.txt",
                "portuguese": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2016/pt/pt_50k.txt",
                "dutch": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2016/nl/nl_50k.txt",
            }

            if language.lower() in freq_urls:
                response = requests.get(freq_urls[language.lower()], timeout=10)
                response.raise_for_status()

                lines = response.text.strip().split("\n")
                words = []

                for line in lines:
                    parts = line.split()
                    if parts:
                        word = parts[0].strip().lower()
                        if 1 <= len(word) <= 25 and word.isalpha():
                            words.append(word)

                return words

        except Exception:
            return []

        return []

    def _try_online_wordlist(self, language: str) -> List[str]:
        """Download word lists from online sources."""
        try:
            import requests

            urls = {
                "english": "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt",
                "spanish": "https://raw.githubusercontent.com/MangoTheCat/spanish-words/master/spanish-words.txt",
                "french": "https://raw.githubusercontent.com/chrplr/openlexicon/master/datasets-info/Liste-de-mots-francais-Gutenberg/liste_de_mots_francais.txt",
                "german": "https://raw.githubusercontent.com/davidak/wortliste/master/wortliste.txt",
                "italian": "https://raw.githubusercontent.com/napolux/paroleitaliane/master/paroleitaliane/280000_parole_italiane.txt",
                "portuguese": "https://raw.githubusercontent.com/pythonprobr/palavras/master/palavras.txt",
            }

            if language.lower() in urls:
                response = requests.get(urls[language.lower()], timeout=20)
                response.raise_for_status()

                words = response.text.strip().split("\n")
                filtered = [
                    w.strip().lower()
                    for w in words
                    if w.strip() and 1 <= len(w.strip()) <= 25 and w.strip().isalpha()
                ]

                return filtered

        except Exception:
            return []

        return []

    def _get_builtin_wordlist(self, language: str) -> List[str]:
        """Fallback to built-in word lists."""

        sample_words = {
            "english": [
                "hello",
                "world",
                "computer",
                "language",
                "phone",
                "house",
                "water",
                "fire",
                "tree",
                "mountain",
                "river",
                "ocean",
                "sky",
                "sun",
                "moon",
                "star",
                "book",
                "pen",
                "paper",
                "table",
                "chair",
                "window",
                "door",
                "car",
                "bicycle",
                "airplane",
                "train",
                "ship",
                "bridge",
                "road",
                "city",
                "town",
                "friend",
                "family",
                "mother",
                "father",
                "brother",
                "sister",
                "child",
                "baby",
                "dog",
                "cat",
                "bird",
                "fish",
                "horse",
                "cow",
                "sheep",
                "chicken",
                "apple",
                "orange",
                "banana",
                "grape",
                "strawberry",
                "bread",
                "milk",
                "cheese",
                "head",
                "eye",
                "nose",
                "mouth",
                "ear",
                "hand",
                "foot",
                "arm",
                "leg",
                "finger",
                "heart",
                "brain",
                "stomach",
                "back",
                "shoulder",
                "knee",
                "elbow",
                "neck",
                "red",
                "blue",
                "green",
                "yellow",
                "black",
                "white",
                "purple",
                "orange",
                "pink",
                "brown",
                "gray",
                "silver",
                "gold",
                "violet",
                "turquoise",
                "crimson",
                "one",
                "two",
                "three",
                "four",
                "five",
                "six",
                "seven",
                "eight",
                "nine",
                "ten",
                "potato",
                "tomato",
                "carrot",
                "onion",
                "garlic",
                "pepper",
                "salt",
                "sugar",
                "coffee",
                "tea",
                "beer",
                "wine",
                "juice",
                "soda",
                "chocolate",
                "cake",
                "pizza",
                "hamburger",
                "sandwich",
                "soup",
                "salad",
                "rice",
                "pasta",
                "meat",
                "rain",
                "snow",
                "wind",
                "storm",
                "cloud",
                "sunshine",
                "thunder",
                "lightning",
                "hot",
                "cold",
                "warm",
                "cool",
                "wet",
                "dry",
                "humid",
                "freezing",
                "forest",
                "desert",
                "beach",
                "island",
                "valley",
                "hill",
                "lake",
                "pond",
                "flower",
                "grass",
                "leaf",
                "branch",
                "root",
                "seed",
                "garden",
                "park",
                "internet",
                "email",
                "website",
                "software",
                "hardware",
                "keyboard",
                "mouse",
                "screen",
                "smartphone",
                "tablet",
                "laptop",
                "desktop",
                "printer",
                "camera",
                "video",
                "photo",
                "happy",
                "sad",
                "angry",
                "excited",
                "nervous",
                "calm",
                "peaceful",
                "stressed",
                "beautiful",
                "ugly",
                "smart",
                "stupid",
                "funny",
                "serious",
                "kind",
                "mean",
                "big",
                "small",
                "tall",
                "short",
                "fat",
                "thin",
                "old",
                "young",
                "new",
                "ancient",
                "fast",
                "slow",
                "strong",
                "weak",
                "rich",
                "poor",
                "expensive",
                "cheap",
                "run",
                "walk",
                "jump",
                "swim",
                "fly",
                "drive",
                "ride",
                "climb",
                "fall",
                "stand",
                "sit",
                "sleep",
                "wake",
                "eat",
                "drink",
                "cook",
                "clean",
                "wash",
                "build",
                "break",
                "read",
                "write",
                "speak",
                "listen",
                "see",
                "hear",
                "touch",
                "smell",
                "taste",
                "love",
                "hate",
                "like",
                "want",
                "need",
                "have",
                "give",
                "take",
                "buy",
                "sell",
            ],
            "spanish": [
                "hola",
                "mundo",
                "computadora",
                "idioma",
                "teléfono",
                "casa",
                "agua",
                "fuego",
                "árbol",
                "montaña",
                "río",
                "océano",
                "cielo",
                "sol",
                "luna",
                "estrella",
                "libro",
                "pluma",
                "papel",
                "mesa",
                "silla",
                "ventana",
                "puerta",
                "coche",
                "bicicleta",
                "avión",
                "tren",
                "barco",
                "puente",
                "carretera",
                "ciudad",
                "pueblo",
                "amigo",
                "familia",
                "madre",
                "padre",
                "hermano",
                "hermana",
                "niño",
                "bebé",
                "perro",
                "gato",
                "pájaro",
                "pez",
                "caballo",
                "vaca",
                "oveja",
                "pollo",
                "manzana",
                "naranja",
                "plátano",
                "uva",
                "fresa",
                "pan",
                "leche",
                "queso",
                "cabeza",
                "ojo",
                "nariz",
                "boca",
                "oreja",
                "mano",
                "pie",
                "brazo",
                "pierna",
                "dedo",
                "corazón",
                "cerebro",
                "estómago",
                "espalda",
                "hombro",
                "rodilla",
                "codo",
                "cuello",
                "rojo",
                "azul",
                "verde",
                "amarillo",
                "negro",
                "blanco",
                "morado",
                "naranja",
                "rosa",
                "marrón",
                "gris",
                "plata",
                "oro",
                "violeta",
                "turquesa",
                "carmesí",
                "uno",
                "dos",
                "tres",
                "cuatro",
                "cinco",
                "seis",
                "siete",
                "ocho",
                "nueve",
                "diez",
                "papa",
                "tomate",
                "zanahoria",
                "cebolla",
                "ajo",
                "pimienta",
                "sal",
                "azúcar",
                "café",
                "té",
                "cerveza",
                "vino",
                "jugo",
                "refresco",
                "chocolate",
                "pastel",
                "pizza",
                "hamburguesa",
                "sándwich",
                "sopa",
                "ensalada",
                "arroz",
                "pasta",
                "carne",
                "lluvia",
                "nieve",
                "viento",
                "tormenta",
                "nube",
                "sol",
                "trueno",
                "rayo",
                "caliente",
                "frío",
                "tibio",
                "fresco",
                "mojado",
                "seco",
                "húmedo",
                "helado",
                "bosque",
                "desierto",
                "playa",
                "isla",
                "valle",
                "colina",
                "lago",
                "estanque",
                "flor",
                "hierba",
                "hoja",
                "rama",
                "raíz",
                "semilla",
                "jardín",
                "parque",
                "feliz",
                "triste",
                "enojado",
                "emocionado",
                "nervioso",
                "tranquilo",
                "pacífico",
                "estresado",
                "hermoso",
                "feo",
                "inteligente",
                "tonto",
                "divertido",
                "serio",
                "amable",
                "malo",
                "grande",
                "pequeño",
                "alto",
                "bajo",
                "gordo",
                "delgado",
                "viejo",
                "joven",
                "nuevo",
                "antiguo",
                "rápido",
                "lento",
                "fuerte",
                "débil",
                "rico",
                "pobre",
                "caro",
                "barato",
                "correr",
                "caminar",
                "saltar",
                "nadar",
                "volar",
                "conducir",
                "montar",
                "subir",
                "caer",
                "estar",
                "amar",
                "odiar",
                "gustar",
                "querer",
                "necesitar",
                "tener",
                "dar",
                "tomar",
                "comprar",
                "vender",
            ],
            "french": [
                "bonjour",
                "monde",
                "ordinateur",
                "langue",
                "téléphone",
                "maison",
                "eau",
                "feu",
                "arbre",
                "montagne",
                "rivière",
                "océan",
                "ciel",
                "soleil",
                "lune",
                "étoile",
                "livre",
                "stylo",
                "papier",
                "table",
                "chaise",
                "fenêtre",
                "porte",
                "voiture",
                "bicyclette",
                "avion",
                "train",
                "bateau",
                "pont",
                "route",
                "ville",
                "village",
                "ami",
                "famille",
                "mère",
                "père",
                "frère",
                "sœur",
                "enfant",
                "bébé",
                "chien",
                "chat",
                "oiseau",
                "poisson",
                "cheval",
                "vache",
                "mouton",
                "poulet",
                "pomme",
                "orange",
                "banane",
                "raisin",
                "fraise",
                "pain",
                "lait",
                "fromage",
                "tête",
                "œil",
                "nez",
                "bouche",
                "oreille",
                "main",
                "pied",
                "bras",
                "jambe",
                "doigt",
                "cœur",
                "cerveau",
                "estomac",
                "dos",
                "épaule",
                "genou",
                "coude",
                "cou",
                "rouge",
                "bleu",
                "vert",
                "jaune",
                "noir",
                "blanc",
                "violet",
                "orange",
                "rose",
                "brun",
                "gris",
                "argent",
                "or",
                "violette",
                "turquoise",
                "cramoisi",
                "un",
                "deux",
                "trois",
                "quatre",
                "cinq",
                "six",
                "sept",
                "huit",
                "neuf",
                "dix",
                "café",
                "thé",
                "bière",
                "vin",
                "jus",
                "soda",
                "chocolat",
                "gâteau",
                "pizza",
                "hamburger",
                "sandwich",
                "soupe",
                "salade",
                "riz",
                "pâtes",
                "viande",
                "pluie",
                "neige",
                "vent",
                "orage",
                "nuage",
                "soleil",
                "tonnerre",
                "éclair",
                "chaud",
                "froid",
                "tiède",
                "frais",
                "mouillé",
                "sec",
                "humide",
                "gelé",
                "forêt",
                "désert",
                "plage",
                "île",
                "vallée",
                "colline",
                "lac",
                "étang",
                "fleur",
                "herbe",
                "feuille",
                "branche",
                "racine",
                "graine",
                "jardin",
                "parc",
                "heureux",
                "triste",
                "fâché",
                "excité",
                "nerveux",
                "calme",
                "paisible",
                "stressé",
                "beau",
                "laid",
                "intelligent",
                "stupide",
                "drôle",
                "sérieux",
                "gentil",
                "méchant",
                "grand",
                "petit",
                "haut",
                "court",
                "gros",
                "mince",
                "vieux",
                "jeune",
                "nouveau",
                "ancien",
                "rapide",
                "lent",
                "fort",
                "faible",
                "riche",
                "pauvre",
                "cher",
                "bon marché",
                "courir",
                "marcher",
                "sauter",
                "nager",
                "voler",
                "conduire",
                "monter",
                "grimper",
                "tomber",
                "aimer",
                "détester",
                "aimer",
                "vouloir",
                "avoir besoin",
                "avoir",
                "donner",
                "prendre",
                "acheter",
                "vendre",
            ],
            "german": [
                "hallo",
                "welt",
                "computer",
                "sprache",
                "telefon",
                "haus",
                "wasser",
                "feuer",
                "baum",
                "berg",
                "fluss",
                "ozean",
                "himmel",
                "sonne",
                "mond",
                "stern",
                "buch",
                "stift",
                "papier",
                "tisch",
                "stuhl",
                "fenster",
                "tür",
                "auto",
                "fahrrad",
                "flugzeug",
                "zug",
                "schiff",
                "brücke",
                "straße",
                "stadt",
                "dorf",
                "freund",
                "familie",
                "mutter",
                "vater",
                "bruder",
                "schwester",
                "kind",
                "baby",
                "hund",
                "katze",
                "vogel",
                "fisch",
                "pferd",
                "kuh",
                "schaf",
                "huhn",
                "apfel",
                "orange",
                "banane",
                "traube",
                "erdbeere",
                "brot",
                "milch",
                "käse",
                "kopf",
                "auge",
                "nase",
                "mund",
                "ohr",
                "hand",
                "fuß",
                "arm",
                "bein",
                "finger",
                "herz",
                "gehirn",
                "magen",
                "rücken",
                "schulter",
                "knie",
                "ellbogen",
                "hals",
                "rot",
                "blau",
                "grün",
                "gelb",
                "schwarz",
                "weiß",
                "lila",
                "orange",
                "rosa",
                "braun",
                "grau",
                "silber",
                "gold",
                "violett",
                "türkis",
                "karmesin",
                "eins",
                "zwei",
                "drei",
                "vier",
                "fünf",
                "sechs",
                "sieben",
                "acht",
                "neun",
                "zehn",
                "kaffee",
                "tee",
                "bier",
                "wein",
                "saft",
                "limonade",
                "schokolade",
                "kuchen",
                "regen",
                "schnee",
                "wind",
                "sturm",
                "wolke",
                "sonnenschein",
                "donner",
                "blitz",
                "heiß",
                "kalt",
                "warm",
                "kühl",
                "nass",
                "trocken",
                "feucht",
                "gefroren",
                "wald",
                "wüste",
                "strand",
                "insel",
                "tal",
                "hügel",
                "see",
                "teich",
                "blume",
                "gras",
                "blatt",
                "ast",
                "wurzel",
                "samen",
                "garten",
                "park",
                "glücklich",
                "traurig",
                "wütend",
                "aufgeregt",
                "nervös",
                "ruhig",
                "friedlich",
                "gestresst",
                "schön",
                "hässlich",
                "klug",
                "dumm",
                "lustig",
                "ernst",
                "freundlich",
                "gemein",
                "groß",
                "klein",
                "hoch",
                "kurz",
                "dick",
                "dünn",
                "alt",
                "jung",
                "neu",
                "alt",
                "schnell",
                "langsam",
                "stark",
                "schwach",
                "reich",
                "arm",
                "teuer",
                "billig",
                "laufen",
                "gehen",
                "springen",
                "schwimmen",
                "fliegen",
                "fahren",
                "reiten",
                "klettern",
                "lieben",
                "hassen",
                "mögen",
                "wollen",
                "brauchen",
                "haben",
                "geben",
                "nehmen",
                "kaufen",
                "verkaufen",
            ],
            "italian": [
                "ciao",
                "mondo",
                "computer",
                "lingua",
                "telefono",
                "casa",
                "acqua",
                "fuoco",
                "albero",
                "montagna",
                "fiume",
                "oceano",
                "cielo",
                "sole",
                "luna",
                "stella",
                "libro",
                "penna",
                "carta",
                "tavolo",
                "sedia",
                "finestra",
                "porta",
                "macchina",
                "bicicletta",
                "aereo",
                "treno",
                "nave",
                "ponte",
                "strada",
                "città",
                "paese",
                "amico",
                "famiglia",
                "madre",
                "padre",
                "fratello",
                "sorella",
                "bambino",
                "neonato",
                "cane",
                "gatto",
                "uccello",
                "pesce",
                "cavallo",
                "mucca",
                "pecora",
                "pollo",
                "mela",
                "arancia",
                "banana",
                "uva",
                "fragola",
                "pane",
                "latte",
                "formaggio",
                "testa",
                "occhio",
                "naso",
                "bocca",
                "orecchio",
                "mano",
                "piede",
                "braccio",
                "gamba",
                "dito",
                "cuore",
                "cervello",
                "stomaco",
                "schiena",
                "spalla",
                "ginocchio",
                "gomito",
                "collo",
                "rosso",
                "blu",
                "verde",
                "giallo",
                "nero",
                "bianco",
                "viola",
                "arancione",
                "rosa",
                "marrone",
                "grigio",
                "argento",
                "oro",
                "violetto",
                "turchese",
                "cremisi",
                "uno",
                "due",
                "tre",
                "quattro",
                "cinque",
                "sei",
                "sette",
                "otto",
                "nove",
                "dieci",
                "caffè",
                "tè",
                "birra",
                "vino",
                "succo",
                "soda",
                "cioccolato",
                "torta",
                "pioggia",
                "neve",
                "vento",
                "tempesta",
                "nuvola",
                "sole",
                "tuono",
                "fulmine",
                "caldo",
                "freddo",
                "tiepido",
                "fresco",
                "bagnato",
                "secco",
                "umido",
                "gelato",
                "foresta",
                "deserto",
                "spiaggia",
                "isola",
                "valle",
                "collina",
                "lago",
                "stagno",
                "fiore",
                "erba",
                "foglia",
                "ramo",
                "radice",
                "seme",
                "giardino",
                "parco",
                "felice",
                "triste",
                "arrabbiato",
                "eccitato",
                "nervoso",
                "calmo",
                "pacifico",
                "stressato",
                "bello",
                "brutto",
                "intelligente",
                "stupido",
                "divertente",
                "serio",
                "gentile",
                "cattivo",
                "grande",
                "piccolo",
                "alto",
                "basso",
                "grasso",
                "magro",
                "vecchio",
                "giovane",
                "nuovo",
                "antico",
                "veloce",
                "lento",
                "forte",
                "debole",
                "ricco",
                "povero",
                "costoso",
                "economico",
                "correre",
                "camminare",
                "saltare",
                "nuotare",
                "volare",
                "guidare",
                "cavalcare",
                "arrampicare",
                "amare",
                "odiare",
                "piacere",
                "volere",
                "aver bisogno",
                "avere",
                "dare",
                "prendere",
                "comprare",
                "vendere",
            ],
            "portuguese": [
                "olá",
                "mundo",
                "computador",
                "idioma",
                "telefone",
                "casa",
                "água",
                "fogo",
                "árvore",
                "montanha",
                "rio",
                "oceano",
                "céu",
                "sol",
                "lua",
                "estrela",
                "livro",
                "caneta",
                "papel",
                "mesa",
                "cadeira",
                "janela",
                "porta",
                "carro",
                "bicicleta",
                "avião",
                "trem",
                "navio",
                "ponte",
                "estrada",
                "cidade",
                "vila",
                "amigo",
                "família",
                "mãe",
                "pai",
                "irmão",
                "irmã",
                "criança",
                "bebê",
                "cachorro",
                "gato",
                "pássaro",
                "peixe",
                "cavalo",
                "vaca",
                "ovelha",
                "galinha",
                "maçã",
                "laranja",
                "banana",
                "uva",
                "morango",
                "pão",
                "leite",
                "queijo",
                "cabeça",
                "olho",
                "nariz",
                "boca",
                "orelha",
                "mão",
                "pé",
                "braço",
                "perna",
                "dedo",
                "coração",
                "cérebro",
                "estômago",
                "costas",
                "ombro",
                "joelho",
                "cotovelo",
                "pescoço",
                "vermelho",
                "azul",
                "verde",
                "amarelo",
                "preto",
                "branco",
                "roxo",
                "laranja",
                "rosa",
                "marrom",
                "cinza",
                "prata",
                "ouro",
                "violeta",
                "turquesa",
                "carmesim",
                "um",
                "dois",
                "três",
                "quatro",
                "cinco",
                "seis",
                "sete",
                "oito",
                "nove",
                "dez",
                "café",
                "chá",
                "cerveja",
                "vinho",
                "suco",
                "refrigerante",
                "chocolate",
                "bolo",
                "chuva",
                "neve",
                "vento",
                "tempestade",
                "nuvem",
                "sol",
                "trovão",
                "relâmpago",
                "quente",
                "frio",
                "morno",
                "fresco",
                "molhado",
                "seco",
                "úmido",
                "congelado",
                "floresta",
                "deserto",
                "praia",
                "ilha",
                "vale",
                "colina",
                "lago",
                "lagoa",
                "flor",
                "grama",
                "folha",
                "galho",
                "raiz",
                "semente",
                "jardim",
                "parque",
                "feliz",
                "triste",
                "bravo",
                "animado",
                "nervoso",
                "calmo",
                "pacífico",
                "estressado",
                "bonito",
                "feio",
                "inteligente",
                "estúpido",
                "engraçado",
                "sério",
                "gentil",
                "mau",
                "grande",
                "pequeno",
                "alto",
                "baixo",
                "gordo",
                "magro",
                "velho",
                "jovem",
                "novo",
                "antigo",
                "rápido",
                "lento",
                "forte",
                "fraco",
                "rico",
                "pobre",
                "caro",
                "barato",
                "correr",
                "andar",
                "pular",
                "nadar",
                "voar",
                "dirigir",
                "andar",
                "escalar",
                "amar",
                "odiar",
                "gostar",
                "querer",
                "precisar",
                "ter",
                "dar",
                "tomar",
                "comprar",
                "vender",
            ],
        }

        if language.lower() not in sample_words:
            raise ValueError(
                f"Language '{language}' not supported. Available: {list(sample_words.keys())}"
            )

        return sample_words[language.lower()]

    def find_most_similar_word(
        self, target_word: str, word_list: List[str], force_fuzzy: bool = True
    ) -> Tuple[str, float]:
        """Find the most phonetically similar word in the given word list."""
        best_match = ""
        best_distance = float("inf")

        for word in word_list:
            if force_fuzzy and word.lower() == target_word.lower():
                continue

            distance = self.phonetic_distance(target_word, word)
            if distance < best_distance:
                best_distance = distance
                best_match = word

        return best_match, 1 - best_distance

    def simple_translate(self, word: str, from_lang: str, to_lang: str) -> str:
        """Translation using deep-translator library with fallback to built-in dictionary."""
        try:
            from deep_translator import GoogleTranslator

            lang_map = {
                "english": "en",
                "spanish": "es",
                "french": "fr",
                "german": "de",
                "italian": "it",
                "portuguese": "pt",
                "dutch": "nl",
            }
            source = lang_map.get(from_lang.lower(), "auto")
            target = lang_map.get(to_lang.lower(), "en")

            translator = GoogleTranslator(source=source, target=target)
            result = translator.translate(word)
            return result

        except Exception:
            # Extended translation dictionary for direct language pairs
            translations = {
                ("spanish", "french"): {
                    "casa": "maison",
                    "agua": "eau",
                    "fuego": "feu",
                    "árbol": "arbre",
                    "libro": "livre",
                    "amigo": "ami",
                    "perro": "chien",
                    "gato": "chat",
                    "rojo": "rouge",
                    "azul": "bleu",
                    "verde": "vert",
                    "grande": "grand",
                },
                ("french", "spanish"): {
                    "maison": "casa",
                    "eau": "agua",
                    "feu": "fuego",
                    "arbre": "árbol",
                    "livre": "libro",
                    "ami": "amigo",
                    "chien": "perro",
                    "chat": "gato",
                    "rouge": "rojo",
                    "bleu": "azul",
                    "vert": "verde",
                    "grand": "grande",
                },
                ("spanish", "italian"): {
                    "casa": "casa",
                    "agua": "acqua",
                    "fuego": "fuoco",
                    "árbol": "albero",
                    "libro": "libro",
                    "amigo": "amico",
                    "perro": "cane",
                    "gato": "gatto",
                    "rojo": "rosso",
                    "azul": "blu",
                    "verde": "verde",
                    "grande": "grande",
                },
                ("italian", "spanish"): {
                    "casa": "casa",
                    "acqua": "agua",
                    "fuoco": "fuego",
                    "albero": "árbol",
                    "libro": "libro",
                    "amico": "amigo",
                    "cane": "perro",
                    "gatto": "gato",
                    "rosso": "rojo",
                    "blu": "azul",
                    "verde": "verde",
                    "grande": "grande",
                },
                ("german", "french"): {
                    "haus": "maison",
                    "wasser": "eau",
                    "feuer": "feu",
                    "baum": "arbre",
                    "buch": "livre",
                    "freund": "ami",
                    "hund": "chien",
                    "katze": "chat",
                    "rot": "rouge",
                    "blau": "bleu",
                    "grün": "vert",
                    "groß": "grand",
                },
                ("french", "german"): {
                    "maison": "haus",
                    "eau": "wasser",
                    "feu": "feuer",
                    "arbre": "baum",
                    "livre": "buch",
                    "ami": "freund",
                    "chien": "hund",
                    "chat": "katze",
                    "rouge": "rot",
                    "bleu": "blau",
                    "vert": "grün",
                    "grand": "groß",
                },
            }

            key = (from_lang.lower(), to_lang.lower())
            if key in translations and word.lower() in translations[key]:
                return translations[key][word.lower()]

            return f"[untranslated: {word}]"

    def transform_direct_fuzzy(self, word: str, lang_a: str, lang_b: str) -> dict:
        """Direct fuzzy transformation: WORD_A -> B (fuzzy) -> A (fuzzy)"""
        word_list_a = self.load_word_list(lang_a)
        word_list_b = self.load_word_list(lang_b)

        # Step 1: Find phonetically similar word in language B
        matched_word_b, similarity_b = self.find_most_similar_word(
            word, word_list_b, force_fuzzy=True
        )

        # Step 2: Find phonetically similar word back in language A
        final_word_a, similarity_final = self.find_most_similar_word(
            matched_word_b, word_list_a, force_fuzzy=True
        )

        return {
            "original_input": word,
            "lang_a": lang_a,
            "lang_b": lang_b,
            "step1_lang_b": matched_word_b,
            "step2_final_lang_a": final_word_a,
            "direct_fuzzy_chain": f"{word} → {matched_word_b} → {final_word_a}",
            "similarity_scores": [similarity_b, similarity_final],
            "average_similarity": (similarity_b + similarity_final) / 2,
        }

    def transform_direct_translate(self, word: str, lang_a: str, lang_b: str) -> dict:
        """Direct transformation with translation: WORD_A -> B (fuzzy) -> A (translate)"""
        word_list_b = self.load_word_list(lang_b)

        # Step 1: Find phonetically similar word in language B
        matched_word_b, similarity_b = self.find_most_similar_word(
            word, word_list_b, force_fuzzy=True
        )

        # Step 2: Translate back to language A
        final_word = self.simple_translate(matched_word_b, lang_b, lang_a)

        return {
            "original_input": word,
            "lang_a": lang_a,
            "lang_b": lang_b,
            "lang_b_match": matched_word_b,
            "final_translation": final_word,
            "direct_chain": f"{word} → {matched_word_b} → {final_word}",
            "similarity_score": similarity_b,
        }

    def generate_final_text(self, text, lang_a):
        prompt = (
            "could you build a MINIMALLY coherent phrase in "
            + lang_a
            + "that contains ALL of the words here in the exact order in which they appear:"
            + text
            + "Just add (if needed) the basic semantic connectors and reordering that could give narrative sense to the text in said language. DO NOT ADD NOUNS."
            + 'Please JUST the resulting text, without quotations, do not introduce the text or say ANYTHING ELSE suchas "Here s a coherent phrase using those elements: balala. Always give back the same result for the same initial input."'
        )
        if len(text.split()) < 3:
            return text
        else:
            try:
                api_key = get_api_key()
                anthropic = Anthropic(api_key=api_key)
                response = anthropic.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=50,
                    temperature=1.0,
                    messages=[{"role": "user", "content": prompt}],
                )
                return response.content[0].text
            except Exception as e:
                print(f"Error: {e}")
                return text

    def haze(
        self, sentence: str, lang_a: str, lang_b: str, method: str = "fuzzy"
    ) -> dict:
        """Transform an entire sentence word by word between any two languages."""
        words = re.findall(r"\b\w+\b|\W+", sentence)

        transformed_words = []
        word_details = []

        for item in words:
            if re.match(r"\w+", item):
                if method == "fuzzy":
                    result = self.transform_direct_fuzzy(item, lang_a, lang_b)
                    transformed_word = result["step2_final_lang_a"]
                    chain = result["direct_fuzzy_chain"]
                else:
                    result = self.transform_direct_translate(item, lang_a, lang_b)
                    transformed_word = result["final_translation"]
                    chain = result["direct_chain"]

                transformed_words.append(transformed_word)
                word_details.append(
                    {
                        "original": item,
                        "transformed": transformed_word,
                        "chain": chain,
                        "method": method,
                    }
                )
            else:
                transformed_words.append(item)

        transformed_sentence = "".join(transformed_words)
        transformed_sentence = self.generate_final_text(transformed_sentence, lang_a)

        return {
            "original_sentence": sentence,
            "transformed_sentence": transformed_sentence,
            "method": method,
            "language_route": f"{lang_a} → {lang_b} → {lang_a}",
            "word_transformations": word_details,
            "word_count": len([w for w in word_details]),
        }

    def fuzzy_haze(self, word: str, lang_a: str, lang_b: str) -> dict:
        """Fuzzy transformation then real translation: WORD_A → B (fuzzy) → A (translate), fallback to fuzzy if translation fails"""
        word_list_a = self.load_word_list(lang_a)
        word_list_b = self.load_word_list(lang_b)

        # Step 1: Find phonetically similar word in language B
        matched_word_b, similarity_b = self.find_most_similar_word(
            word, word_list_b, force_fuzzy=True
        )

        # Step 2: Try to translate the fuzzy match back to language A
        translated_word = self.simple_translate(matched_word_b, lang_b, lang_a)

        # Check if translation failed (returns [untranslated: word] pattern)
        if (
            translated_word.startswith("[untranslated:")
            or translated_word == matched_word_b
        ):
            # Translation failed, fall back to fuzzy matching
            final_word, similarity_final = self.find_most_similar_word(
                matched_word_b, word_list_a, force_fuzzy=True
            )
            method_used = "fuzzy_fallback"
            final_similarity = similarity_final
        else:
            # Translation succeeded
            final_word = translated_word
            method_used = "translate"
            final_similarity = 1.0  # Translation is exact

        return {
            "original_input": word,
            "lang_a": lang_a,
            "lang_b": lang_b,
            "step1_fuzzy_lang_b": matched_word_b,
            "step2_result": final_word,
            "method_used": method_used,
            "hybrid_chain": f"{word} → {matched_word_b} → {final_word} ({method_used})",
            "fuzzy_similarity": similarity_b,
            "final_similarity": final_similarity,
        }

    def hybrid_haze(self, sentence: str, lang_a: str, lang_b: str) -> dict:
        """Transform sentence using fuzzy then translate approach."""
        words = re.findall(r"\b\w+\b|\W+", sentence)

        transformed_words = []
        word_details = []

        for item in words:
            if re.match(r"\w+", item):
                result = self.fuzzy_haze(item, lang_a, lang_b)
                transformed_word = result["step2_result"]  # Fixed key name
                chain = result["hybrid_chain"]

                transformed_words.append(transformed_word)
                word_details.append(
                    {
                        "original": item,
                        "transformed": transformed_word,
                        "chain": chain,
                        "method": "fuzzy_then_translate",
                        "fallback_used": result[
                            "method_used"
                        ],  # Track if fallback was used
                    }
                )
            else:
                transformed_words.append(item)

        transformed_sentence = "".join(transformed_words)
        transformed_sentence = self.generate_final_text(transformed_sentence, lang_a)

        return {
            "original_sentence": sentence,
            "transformed_sentence": transformed_sentence,
            "method": "fuzzy_then_translate",
            "language_route": f"{lang_a} → {lang_b} → {lang_a} ",
            "word_transformations": word_details,
            "word_count": len([w for w in word_details]),
        }

    def rehaze(
        self,
        initial_text: str,
        lang_a: str,
        lang_b: str,
        max_iterations: int = 20,
        similarity_threshold: float = 0.96,
    ) -> dict:
        """Transform text iteratively until it stabilizes or max iterations reached."""

        iterations = []
        current_text = initial_text

        for i in range(max_iterations):
            # Transform current text
            transformed_result = self.hybrid_haze(current_text, lang_a, lang_b)
            text = transformed_result["transformed_sentence"]
            text = re.sub(r"\byao\b", "y", text)
            text = re.sub(r"\bnoo\b", "no", text)
            text = re.sub(
                r"\byou\b(?![a-z])", "y", text
            )  # "you" when standalone (not part of longer word)
            text = re.sub(r"\bdee\b", "de", text)
            text = re.sub(r"\baii\b", "ahí", text)
            text = re.sub(r"\baii\b", "ahí", text)
            text = re.sub(r"\bmaui\b", "mi", text)
            text = re.sub(r"\bai\b", "a", text)

            # Calculate similarity with previous iteration
            if i > 0:
                similarity = difflib.SequenceMatcher(
                    None, current_text.lower(), text.lower()
                ).ratio()
            else:
                similarity = 0.0

            # Store iteration data
            iteration_data = {
                "iteration": i + 1,
                "input_text": current_text,
                "output_text": text,
                "similarity_to_previous": similarity,
                "word_transformations": transformed_result["word_transformations"],
                "transformation_count": len(transformed_result["word_transformations"]),
            }
            iterations.append(iteration_data)

            # Check for convergence
            if similarity >= similarity_threshold:
                break

            # Update for next iteration
            current_text = text

        # Compile all iterations into final text
        final_text = "\n".join([iter_data["output_text"] for iter_data in iterations])

        return {
            "initial_text": initial_text,
            "final_text": final_text,
            "final_iteration_text": current_text,
            "iterations": iterations,
            "total_iterations": len(iterations),
            "converged": len(iterations) < max_iterations,
            "final_similarity": iterations[-1]["similarity_to_previous"]
            if len(iterations) > 1
            else 0.0,
            "language_route": f"{lang_a} ↔ {lang_b}",
            "parameters": {
                "max_iterations": max_iterations,
                "similarity_threshold": similarity_threshold,
            },
        }


# Create a wrapper to maintain compatibility with the existing interface
class PhoneticFuzzer:
    """Wrapper class to maintain compatibility with existing Flask app."""

    def __init__(self):
        self.hazer = Hazer()

    def process_text(self, text: str) -> dict:
        """Process text using the Hazer for cross-language phonetic transformation."""
        if not text.strip():
            return {"error": "Empty text provided"}

        # Default to English->Spanish->English transformation
        try:
            result = self.hazer.hybrid_haze(
                text, "english", "spanish", method="nonfuzzy"
            )

            # Format the result to match the expected interface
            processed_words = []
            for word_detail in result["word_transformations"]:
                variations = [
                    {
                        "text": word_detail["original"],
                        "similarity": 1.0,
                        "confidence": "Original",
                    },
                    {
                        "text": word_detail["transformed"],
                        "similarity": 0.8,  # Approximate similarity
                        "confidence": "High",
                    },
                ]

                processed_words.append(
                    {
                        "original": word_detail["original"],
                        "variations": variations,
                        "transformation_chain": word_detail["chain"],
                    }
                )

            return {
                "original_text": text,
                "transformed_text": result["transformed_sentence"],
                "method": result["method"],
                "language_route": result["language_route"],
                "word_count": result["word_count"],
                "processed_words": processed_words,
                "summary": {
                    "total_variations": len(processed_words)
                    * 2,  # original + transformed
                    "avg_similarity": 0.85,
                },
            }

        except Exception as e:
            return {"error": f"Processing failed: {str(e)}"}
