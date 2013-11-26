
import operator
import math
import re
import sys
from topia.termextract import tag
from topia.termextract import extract


# AFINN-111 is as of June 2011 the most recent version of AFINN
filenameAFINN = 'sentiment/AFINN-111.txt'
afinn = dict(map(lambda (w, s): (w, int(s)), [
    ws.strip().split('\t') for ws in open(filenameAFINN)]))

# Word splitter pattern
pattern_split = re.compile(r"\W+")

'''
Given a text ,return a sentiment score between -3 to 3.
The higher the value ,the more positive is the text
'''
def sentimentAnalysis(text):
    """
    Returns a float for sentiment_score strength based on the input text.
    Positive values are positive valence, negative value are negative valence. 
    """
    words = pattern_split.split(text.lower())
    sentiments = map(lambda word: afinn.get(word, 0), words)
    if sentiments:
        # How should you weight the individual word sentiments? 
        # You could do N, sqrt(N) or 1 for example. Here I use sqrt(N)
        sentiment_score = float(sum(sentiments)) / math.sqrt(len(sentiments))
    else:
        sentiment_score = 0
    return sentiment_score


#print sentimentAnalysis("Love dogs")
#print sentimentAnalysis("I Hate you")
#print sentimentAnalysis("I don't think I'm ready to give a demo tomorrow ")

