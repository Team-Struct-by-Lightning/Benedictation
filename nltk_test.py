import nltk
from nltk.tag import pos_tag, map_tag
#nltk.download()


sentence = """ We should schedule a meeting for January 28th, 2015"""
tokens = nltk.word_tokenize(sentence)
tagged = nltk.pos_tag(tokens)
#map tags to universal tagset
simplifiedTags = [(word, map_tag('en-ptb', 'universal', tag)) for word, tag in tagged]


for word, tag in simplifiedTags:
	if(tag == 'NOUN' or tag == 'PRON'):
		print word


