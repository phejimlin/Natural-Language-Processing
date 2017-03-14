from __future__ import division

from collections import defaultdict, Counter
from itertools import groupby
from operator import itemgetter
from collocation import BaseWord
import fileinput


def parse_line(line):
    # baseword, collocate, distance = line.strip().split('\t')
    return line.strip().split('\t')


if __name__ == '__main__':
    for baseword, colls in groupby(map(parse_line, fileinput.input()), key=itemgetter(0)):
        skipbigrams = defaultdict(Counter)
        # write your code here...
        for _, collword, distance in colls:
            distance = int(distance)
            skipbigrams[collword][distance] += 1
        baseWord_obj = BaseWord(skipbigrams)
        # print(baseWord_obj.items())

        for coll, collocate in baseWord_obj.items():
            for i, freq in collocate.items():
                print(baseword, coll, i, collocate.strength, collocate.spread, collocate.peak, freq)
