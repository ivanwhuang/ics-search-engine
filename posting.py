class Posting: 
	def __init__(self, doc_id, frequency, total_tokens, tf):
		self.doc_id = doc_id
		self.frequency = frequency
		self.total_tokens = total_tokens 
		self.tf = tf

		# Store the positions of where the term occurred. Use it later if I decide to implement extent lists
		# self.positions = [] 


