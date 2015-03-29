import nltk
from nltk.tag import pos_tag, map_tag
#nltk.download()


#sentence = """ We should schedule a meeting for January 28th, 2015"""

def find_nouns(sentence):
	tokens = nltk.word_tokenize(sentence)
	tagged = nltk.pos_tag(tokens)
	#map tags to universal tagset
	simplifiedTags = [(word, map_tag('en-ptb', 'universal', tag)) for word, tag in tagged]

	return_list = []
	for word, tag in simplifiedTags:
		if(tag == 'NOUN' or tag == 'PRON'):
			return_list.append(word)
			#print word

	return return_list

def schedule_meeting(sentence):
	tokens = nltk.word_tokenize(sentence)
	tagged = nltk.pos_tag(tokens)

	simplifiedTags = [(word, map_tag('en-ptb', 'universal', tag)) for word, tag in tagged]
	retval = 'false'
	for word, tag in simplifiedTags:
		print word, tag
		if(tag == 'VERB' and word == 'schedule'):
			retval = 'true'

	return retval