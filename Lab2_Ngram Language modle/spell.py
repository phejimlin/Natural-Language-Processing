import re, collections
from NetSpeak.NetSpeakAPIpy3 import NetSpeak
from Linggle.LinggleAPI import Linggle
from nltk import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer
lmtzr = WordNetLemmatizer()
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
        candidates = known([word]) or known(edits1(word)) or known_edits2(word)
        candidates.add(word)
        print(('candidates:', candidates))
        temp = unigram_from_netspeak(candidates)
        print(('candidates after unigram:', temp))
        return temp
    # return max(candidates, key=NWORDS.get)


def unigram_from_netspeak(word_set):
    result = set()
    for word in word_set:
        lemmatize_word = lmtzr.lemmatize(word, 'v')
        # print(lemmatize_word)
        res = SE.search(lemmatize_word)
        if lemmatize_word in ngrams_cache.keys():
            # print(('hit', lemmatize_word))
            result.add(word)
        else:
            if res:
                # print('\n'.join('\t'.join([str(y) for y in x]) for x in res))
                result.add(word)
                ngrams_cache[word] = res[0][1]
            else:
                ngrams_cache[word] = 0
                # print('not found')
    return result


def find_confusables(word):
    for line in open('lab2.confusables.txt', 'r'):
        confusables_list = line.split('	')
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


def ngrams(sentence_list):
    for index, sentence in enumerate(sentence_list):
        word_list = sentence.split()
        score = 0
        for i in range(len(word_list) - 3 + 1):
            # print(i)
            query_sentence = ' '.join(word_list[i:i + 3])
            # print(query_sentence in ngrams_cache.keys())
            if query_sentence in ngrams_cache.keys():
                # print(('hit', query_sentence))
                score += ngrams_cache[query_sentence]
            else:
                res = SE.search(query_sentence)
                if res:
                    score += res[0][1]
                    ngrams_cache[query_sentence] = res[0][1]
                    print('\n'.join('\t'.join([str(y) for y in x]) for x in res))
                else:
                    ngrams_cache[query_sentence] = 0
                    # print('not found')
        sentence_list[index] = (sentence, score)
    print(('sentence list score:', sentence_list))
    return max(sentence_list, key=lambda x: x[1])[0]

# SE = NetSpeak()
SE = Linggle()

# print('speling ->', correct('speling'))
# print('korrecter ->', correct('korrecter'))
# print(correct('snowing'))
# print(known_edits2('snowing'))
# print(edits1('snowing'))
# print(known(['snowing']))

# print(unigram_from_netspeak({'snor', 'snow', 'slowing', 'knowing', 'showing', 'sowing'}))
# find_confusables('coarse')



file = open('lab2.test.1.txt', 'r')
hits = 0
error = 0
corrections = 0
for index, line in enumerate(file):
    print(index)
    if index == 20:
        print(hits, corrections, error)
        Precision = hits / corrections * 100
        Recall = hits / error * 100
        print('Precision: ' + str(Precision))
        print('Recall: ' + str(Recall))
        break

    print(line)
    answer = line.split(' 	')[1].lower().split('\n')[0]
    error_sentence = line.split(' 	')[0]
    sentence_candidates = []
    for word in re.split('-| ', error_sentence):
        word = word.lower()
        # word = lmtzr.lemmatize(word)
        correct_word=correct(word)
        # print(word, ' -> ', correct_word)
        sentence_candidates.append(correct_word)
    print(('Every word candidates: ', sentence_candidates))

    result = ngrams(compose_candidates_sentence(sentence_candidates))
    print(result)
    hits += 1
    if answer == result:
        corrections += 1
        print('Correct!!!!')
    else:
        error += 1
        print('Error...')
    print('\n')

Precision = hits/corrections*100
Recall = hits/error*100
print('Precision: ' + str(Precision))
print('Recall: ' + str(Recall))
