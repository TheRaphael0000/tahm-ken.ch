import random
tk_quotes = open("static/txt/tk_quotes.txt").read().split("\n")


def random_quote():
    return random.choice(tk_quotes)
