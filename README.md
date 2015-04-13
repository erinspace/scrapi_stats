# SHARE Stats

usage: ```python aggregate.py [-h] [-m MISSING [MISSING ...]] [-t TERMS [TERMS ...]]
                    [-s SIZE] [-i INCLUDES [INCLUDES ...]] [-b] [-p]```

examples: 
```python aggregate.py -i description``` will generate percentages for all sources with descriptions

```python aggregate.py -m sponsor``` will generate percentages for all sources without sponsors

```python aggregate.py -t tags -s 10``` will generate top 10 list for elements with that name

```python aggregate.py -t tags -v 1 -s 10``` will gennerate top 10 list for elements using v1 of the schema

```
A command line interface for getting numbers of SHARE sources missing given
terms

optional arguments:
  -h, --help            show this help message and exit
  -m MISSING [MISSING ...], --missing MISSING [MISSING ...]
                        The terms to aggregate with, to find sources with
                        terms missing
  -t TERMS [TERMS ...], --terms TERMS [TERMS ...]
                        The top unique entries with given terms. Use with size
                        to control number of results shown.
  -s SIZE, --size SIZE  The number of results to return per aggretation
  -v V, --version V     The version of the OSF SHARE API to hit
  -i INCLUDES [INCLUDES ...], --includes INCLUDES [INCLUDES ...]
                        The terms to aggregate with, to find sources with
                        terms included
  -b, --bargraph        A flag to signal to draw a bar graph
  -p, --piegraph        A flag to signal to draw a pie graph
  
```
