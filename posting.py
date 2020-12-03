import math

class Posting: 
	def __init__(self, doc_id, frequency, total_tokens, tfidf=0.0):
		self.doc_id = doc_id
		self.frequency = frequency
		self.total_tokens = total_tokens 
		self.tf = 1 + math.log(frequency)
		# self.tf = frequency / total_tokens
		# self.tfidf = tfidf 
		
		# Store the positions of where the term occurred. Use it later when I decide to implement extent lists
		# self.positions = []

