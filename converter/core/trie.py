import pandas as pd


url_currencies_short = 'https://drive.google.com/uc?id=1LFQO13AVf4U0LXOzKEycRYL0gKx3tv1m'
CURRENCIES_SHORT = pd.read_csv(url_currencies_short)

url_europe_currencies = 'https://drive.google.com/uc?id=1JRSbtOFZ54PPCo55qwA4FfPKjw31NRY5'
EUROPE_CURRENCIES = pd.read_csv(url_europe_currencies)


def prepare_and_get_word_searcher():
    word_searcher = Trie()
    for country in CURRENCIES_SHORT['Country']:
        word_searcher.add_word(country.lower())
    for code in CURRENCIES_SHORT['AlphabeticCode']:
        word_searcher.add_word(code)
    for country, code in zip(CURRENCIES_SHORT['Country'], CURRENCIES_SHORT['AlphabeticCode']):
        word_searcher.currencies_dict[country.lower()] = code

    return word_searcher


class TrieNode:
    """
    Node of the trie, used to store one letter of processed words.
    Connects letter with further ones using set 'self.children'.
    Stores if the letter is an end of some word in a variable 'self.end'.
    """

    def __init__(self):
        self.children = {}
        self.end = False


class Trie:
    """
    Prefix tree that stores names of currencies and countries. Used to validate inputted currencies and
    to provide a search with the first 3 letters of a country's name.
    Lowercase words are countries, uppercase words are currency codes.
    self.currencies_dict -> {country name : alphabetic currency code}

    Methods
    -------
    add_word(word)
        Adds a new word to the trie
    search(prefix)
        Searches a word with a given prefix, returns the word
    """

    def __init__(self):
        self.root = TrieNode()
        self.currencies_dict = {}

    def add_word(self, word: str):
        """
        Adds a new word to the trie.
        Iterates through letters, adds letter to the previous one's children set.

        Parameters
        ----------
        word : str
            word to add to the trie
        """

        curr = self.root

        for c in word:
            if c not in curr.children:
                curr.children[c] = TrieNode()
            curr = curr.children[c]

        curr.end = True

    def get_code(self, prefix: str) -> str:
        search_result = self.__search_with_prefix(prefix)
        if search_result.islower():
            code = self.__get_code_with_country_name(search_result)
        else:
            code = search_result
        return code

    def __search_with_prefix(self, prefix: str) -> str:
        """
        Searches a word with a given prefix among all added before words.
        Returns the word or None in case of non-existence of such word.

        Parameters
        ----------
        prefix : str
            prefix to search the word with; lowercase -> country's name, uppercase -> currency code
        """
        curr = self.root
        answer = ''

        for ch in prefix:
            if ch not in curr.children:
                return ''
            answer += ch
            curr = curr.children[ch]

        while not curr.end:
            for pair in curr.children.items():
                ch, curr = pair
                answer += ch
        return answer

    def __get_code_with_country_name(self, country_name: str) -> str:
        return self.currencies_dict.get(country_name)