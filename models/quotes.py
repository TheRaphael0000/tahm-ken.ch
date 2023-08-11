import random
tk_quotes = open("static/txt/tk_quotes.txt",
                 "rb").read().decode("utf8").split("\n")


def random_quote():
    return random.choice(tk_quotes)
