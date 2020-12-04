
from posting import Posting
from nltk.tokenize import RegexpTokenizer
from nltk.stem import PorterStemmer
from collections import defaultdict

def build_record(line):
	line = line.rstrip('\n').split('=')
	token = line[0]
	postings = line[1].split(':')
	posting_list = []
	for s in postings:
		doc_id, freq, total_tokens, tf = s.split(',')
		posting_list.append(Posting(int(doc_id), int(freq), int(total_tokens), float(tf)))	
	return (token, posting_list)

def get_record_term(line):
	line = line.rstrip('\n').split('=')
	token = line[0]
	return token

def stringify_record(token, postings):
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
	return url.split('?')[0].split('#')[0].rstrip('/ ')	

def extract_tokens(s):
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
