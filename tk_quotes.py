import random
tk_quotes = open("static/txt/tk_quotes.txt").read().split("\n")

class RandomQuotes:
    # a small class to be able to access a random property in the template
    @property
    def random(self):
        return random.choice(tk_quotes)