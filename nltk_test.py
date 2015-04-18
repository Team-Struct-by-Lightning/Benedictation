import nltk
from nltk.tag import pos_tag, map_tag
from stat_parser import Parser, display_tree

from timex import time_tag
nltk.download('all')

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
	print "we are checking if we can schedule a meeting!"
	tokens = nltk.word_tokenize(sentence)
	tagged = nltk.pos_tag(tokens)
	schedule_verbs = ['set', 'make', 'create', 'get', 'schedule', 'appoint',
					 'slate', 'arrange', 'organize', 'construct', 'coordinate',
					 'establish', 'form', 'formulate', 'run', 'compose', 'have', 'meet']
	schedule_nouns = ['appointment', 'meeting','meetup', 'reservation', 'session'
					 'talk', 'call', 'powwow', 'meet', 'rendezvous', 'event', 'conference']
	simplifiedTags = [(word, map_tag('en-ptb', 'universal', tag)) for word, tag in tagged]
	retval = False
	parser = Parser()
	tree = parser.parse(sentence)
	#print tree

	for element in tree:
		if element.label() == 'VP':
			for verb_subtrees in element.subtrees():
				if verb_subtrees.label() == 'VB' or verb_subtrees.label() == 'VBZ' \
				or verb_subtrees.label() == 'VBP'or verb_subtrees.label() == 'VBG' \
				and any(x in verb_subtrees.leaves() for x in schedule_verbs):
					for noun_subtrees in element.subtrees():
						if noun_subtrees.label() == 'NP' and any(x in noun_subtrees.leaves() for x in schedule_nouns):
							print "True"


	for index, word_and_tag in enumerate(simplifiedTags):
		word, tag = word_and_tag
		if(index + 2 < len(simplifiedTags)):
			next_word, next_tag = simplifiedTags[index + 1]
			next_next_word, next_next_tag = simplifiedTags[index + 2]
			#the idea is capture case of verb -> determinate article -> noun
			if word in schedule_verbs and tag == 'VERB' and \
			next_tag == 'DET' and \
			next_next_word in schedule_nouns and next_next_tag == 'NOUN':
				retval = True
				#print "meeting will be at "
				#time_tag(sentence)

	return retval


schedule_meeting("Can you set up a powwow for me")