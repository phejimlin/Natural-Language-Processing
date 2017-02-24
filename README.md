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

In 200 sentence in lab2.test.1.txt. My result is:
* Hits: 199  Corrections: 91  Error: 108 
* Precision: 45.7286432160804% 
* Recall: 54.2713567839196%