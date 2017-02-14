import re
from collections import Counter

def words(text): return re.findall(r'\w+', text.lower())

def bigrams(input_list):
    bigram_list = []
    for i in range(len(input_list) - 1):
        bigram_list.append(input_list[i] + ' ' + input_list[i + 1])
        return bigram_list

WORDS = Counter(words(open('big.txt').read()))
BIGRAMS = Counter(bigrams(words(open('big.txt').read())))

def P(word, N=sum(WORDS.values())): 
    "Probability of `word`."
    # if " " in word:
    #     word_list = word.split(' ')
    #     first_word = word_list[0]
    #     second_word = word_list[1]
    #     return WORDS[first_word] / N + WORDS[second_word] / N
    # else:
    return WORDS[word] / N

def correction(word): 
    "Most probable spelling correction for word."
    # print(candidates(word))
    return max(candidates(word), key=P)

def candidates(word): 
    "Generate possible spelling corrections for word."
    return (known_bigrams(edits1(word)) or known([word]) or known(edits1(word)) or known(edits2(word)) or [word])

def known(words): 
    "The subset of `words` that appear in the dictionary of WORDS."
    for word in list(words):
        if " " in word:
            word_list = word.split(' ')
            first_word = word_list[0]
            second_word = word_list[1]
            if first_word in WORDS and second_word in WORDS:
                return set([word])
        else:
            if word in WORDS:
                return set(word)

def known_bigrams(words):
    return set(w for w in words if w in BIGRAMS)

def edits1(word):
    "All edits that are one edit away from `word`."
    letters    = 'abcdefghijklmnopqrstuvwxyz'
    word = word.replace(" ", "")
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    # print('splits:')
    # print(splits)
    deletes    = [L + R[1:]               for L, R in splits if R]
    # print('deletes:')
    # print(deletes)
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    # print('transposes:')
    # print(transposes)
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    # print('replaces:')
    # print(replaces)
    inserts    = [L + c + R               for L, R in splits for c in letters]
    # print('inserts:')
    # print(inserts)
    spaces     = [L + ' ' + R             for L, R in splits if R]
    # print('spaces:')
    # print(spaces)
    return set(deletes + transposes + replaces + inserts + spaces)


def edits2(word): 
    "All edits that are two edits away from `word`."
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))

# print(correction('speling'))
print(correction('taketo'))
print(correction('mor efun'))
print(correction('with out'))
