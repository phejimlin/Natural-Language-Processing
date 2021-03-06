import re, collections
from Linggle.LinggleAPI import Linggle
from itertools import product

ngrams_cache = {}

def words(text): return re.findall('[a-z]+', text.lower())

def train(features):
    model = collections.defaultdict(lambda: 1)
    for f in features:
        model[f] += 1
    return model

file = open('big.txt', 'r')
NWORDS = train(words(file.read()))

alphabet = 'abcdefghijklmnopqrstuvwxyz'

def edits1(word):
   splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
   deletes    = [a + b[1:] for a, b in splits if b]
   transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
   replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
   inserts    = [a + c + b     for a, b in splits for c in alphabet]
   return set(deletes + transposes + replaces + inserts)

def known_edits2(word):
    return set(e2 for e1 in edits1(word) for e2 in edits1(e1) if e2 in NWORDS)

def known(words):
    return set(w for w in words if w in NWORDS)


def correct(word):
    candidates = find_confusables(word)
    if candidates:
        return candidates
    else:
        candidates = sort_word_count(known([word]).union(known(edits1(word)))) or sort_word_count(known_edits2(word))
        candidates.add(word)  # Add original word to candidates avoid the word not in big.txt
        return candidates


def sort_word_count(word_list):
    word_count_dict = {}
    for candidate_word in word_list:
        word_count_dict[candidate_word] = NWORDS[candidate_word]
    sorted_result = [(w, word_count_dict[w]) for w in sorted(word_count_dict, key=word_count_dict.get, reverse=True)]
    candidates = set()
    for candidate in sorted_result[:5]:  # Just take the word whose frequency is top 5 in the big.txt to candidates.
        candidates.add(candidate[0])
    return candidates


def find_confusables(word):
    for confusables_line in open('lab2.confusables.txt', 'r'):
        confusables_list = confusables_line.split('	')
        confusables_list[1] = confusables_list[1].rstrip()
        if word in confusables_list:
            return set(x for x in confusables_list)


def compose_candidates_sentence(sentence):
    #  input: [{'a'}, {'man'}, {'weight', 'wight', 'wright'}, {'for'}, {'the'}, {'animal'}]
    #  output: ['a man weight for the animal', 'a man wight for the animal', 'a man wright for the animal']
    all_sentence_candidates = []
    for word_group in sentence:
        all_sentence_candidates.append(word_group)
        if len(all_sentence_candidates) > 1:
            all_sentence_candidates[0] = combine_two_word_group(all_sentence_candidates[0], all_sentence_candidates[1])
            all_sentence_candidates.pop(1)
    return all_sentence_candidates[0]


def combine_two_word_group(word_group1, word_group2):
    # input: {'chasing', 'chatting', 'charing'}, {'to'}
    # output: ['chatting to', 'charing to', 'chasing to']
    sentence_list = []
    for sentence in product(word_group1, word_group2):
        sentence_list.append(' '.join(str(i) for i in sentence))
    return sentence_list


def calculate_best_candidates(sentence_list):
    # Use every candidates sentence to run 3-grams and its length grams to chose the highest frequency sentence.
    for i, sentence in enumerate(sentence_list):
        word_list = sentence.split()
        candidates_score = ngrams_calculate_score(3, word_list) * ngrams_calculate_score(len(word_list), word_list)
        sentence_list[i] = (sentence, candidates_score)
    return max(sentence_list, key=lambda x: x[1])[0]


def ngrams_calculate_score(n, word_list):
    if n > 5:
        n = 5
    candidates_score = 1
    for i in range(len(word_list) - n + 1):
        query_sentence = ' '.join(word_list[i:i + n])
        if query_sentence in ngrams_cache.keys():
            # A dict to do cache function.
            candidates_score += ngrams_cache[query_sentence]
        else:
            res = SE.search(query_sentence)
            if res:
                candidates_score += res[0][1]
                ngrams_cache[query_sentence] = res[0][1]
                # print('\n'.join('\t'.join([str(y) for y in x]) for x in res))
            else:
                ngrams_cache[query_sentence] = 1  # avoid * 0 = 0
    return candidates_score

SE = Linggle()
f = open('result_answer.txt', 'w')
file = open('lab2.test.1.txt', 'r')
hits = 0
error = 0
corrections = 0
not_alter_word = 0
for index, line in enumerate(file):
        f.write(str(index)+'. \n' + 'Title: ' + line.rstrip() + '\n')
        print(str(index)+'. \n' + 'Title: ' + line.rstrip() + '\n')

        # Ex: line will be: a man waight for the animal 	a man waits for the animal
        answer = line.split(' 	')[1].split('\n')[0]
        error_sentence = line.split(' 	')[0]

        sentence_candidates = []
        for w in re.split('-| ', error_sentence):
            correct_word = correct(w)
            sentence_candidates.append(correct_word)
        # Ex: sentence_candidates will be [{'a'}, {'man'}, {'weight', 'wight', 'wright'}, {'for'}, {'the'}, {'animal'}]
        result = calculate_best_candidates(compose_candidates_sentence(sentence_candidates))

        # Calculate corrections and error.
        if answer == result:
            corrections += 1
            print('Correct!!!!' + '\n')
            f.write('Correct!!!!' + '\n')
        elif error_sentence == result:
            not_alter_word += 1
            print('not_alter_word:' + str(not_alter_word) + '\n')
            f.write('not_alter_word:' + str(not_alter_word) + '\n')
        else:
            error += 1
            print('Error...' + '\n')
            f.write('Error...' + '\n')
        hits += 1
        print('Result: ' + result + '\n' + 'hits: ' + str(hits) + '  corrections: ' + str(corrections) + '  error: ' + str(error) + '\n\n')
        f.write('Result: ' + result + '\n' + 'hits: ' + str(hits) + '  corrections: ' + str(corrections) + '  error: ' + str(error) + '\n\n')

