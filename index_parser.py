
from posting import Posting
from nltk.tokenize import RegexpTokenizer
from nltk.stem import PorterStemmer
from collections import defaultdict

def build_record(line):
	'''Given a line from an index file, parse and return the term and its respective posting list object'''
	line = line.rstrip('\n').split('=')
	token = line[0]
	postings = line[1].split(':')
	posting_list = []
	for s in postings:
		doc_id, freq, total_tokens, tf = s.split(',')
		posting_list.append(Posting(int(doc_id), int(freq), int(total_tokens), float(tf)))	
	return (token, posting_list)

def get_record_term(line):
	'''Given a line from an index file, parse and return the term only'''	
	line = line.rstrip('\n').split('=')
	token = line[0]
	return token

def stringify_record(token, postings):
	'''
	Given a term and its respective posting list, stringify the information so 
	that it is ready to be written to an index file

	Format: 
       [term]=[doc1],[frequency1],[total_tokens1],[tf1]:[doc2],[frequency2],[total_tokens2],[tf2]

       '=' is a delimeter that separates the term and its posting list
       ':' is a delimeter that separates different postings
       ',' is a delimeter that separates the data stored within a posting

	'''	
	record_str = token + '='

	for i in range(len(postings)):
		posting_str = (str(postings[i].doc_id) + ',' 
					+ str(postings[i].frequency) + ',' 
					+ str(postings[i].total_tokens) + ',' 
					+ str(postings[i].tf))
		if i < len(postings) - 1:
			posting_str += ':'
		record_str += posting_str

	record_str += '\n'		
	return record_str

def parse_url(url):
	'''parse url by removing query parameters and query fragments'''
	return url.split('?')[0].split('#')[0].rstrip('/ ')	

def extract_tokens(s):
	'''
	For given string of text, tokenize and stem each term.
	Return a count of total tokens along with a dictionary mapping the 
	term frequency for each term
	'''  
	tokenizer = RegexpTokenizer(r'[a-zA-Z0-9]+')
	ps = PorterStemmer()

	tokens = defaultdict(int)
	total_tokens = 0

	# tokenize 
	words = tokenizer.tokenize(s)

	# stem each token before storing
	for word in words:
		token = ps.stem(word.lower())
		tokens[token] += 1
		total_tokens += 1

	return (total_tokens, tokens)
