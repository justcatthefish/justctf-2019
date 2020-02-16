import random

def generate(sentence, n=2):
    z = zip(*[sentence[i:] for i in range(n)])
    random.shuffle(z)
    return z

text = "there_was_no_single_doubt_in_my_mind_that_great_player_like_you_shall_solve_the_puzzle"
print(', '.join(map(lambda x: ''.join(x), generate(text,3))))