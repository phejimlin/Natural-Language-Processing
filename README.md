# Natural-Language-Processing
A course provided by NTHU ISA in 2017 spring.


## Lab1_Spell Checker
### Goal:
* Fusion errors (e.g. “taketo” → “take to”)
* Multi-token errors (e.g. “mor efun” → “more fun”)
* Fusion errors (e.g. “with out” → “without”)

Reference :  http://norvig.com/spell-correct.html

## Lab2_Ngram Language modle
### Goal is to fix sentence error.
Example:
* make a depe hole  ->	make a deep hole
* an ansion method of hunting -> an ancient method of hunting
* at brake time -> at break time

[Result](./Lab2_Ngram%20Language%20modle/report.txt):
* Test case 1 is to correct wrong sentence.
* hits: 198  corrections: 90  error: 108


* Test case 2 is to correct right sentence and see false alarm.
* hits: 198 corrections: 116  error: 82
