from posting import Posting
from queue import PriorityQueue 
from collections import defaultdict

from index_parser import build_record, get_record_term

try:
	import cPickle as pickle
except:
	import pickle

import math

base_path = 'dumps/index_dumps/'
# base_path = 'dumps/test_dumps/'

index_file =  base_path + 'final_index.txt'
url_map_file =  base_path + 'url_map.pkl'
vector_lens_file = base_path + 'vector_lens.pkl'
offset_file = base_path + 'term_offsets.pkl'
idf_file = base_path + 'idf.pkl'	

class SearchEngine():
	def __init__(self):
		self.index_f = open(index_file, 'r')
		with open(idf_file, 'rb') as idf_f:
			self.idf_dict = pickle.load(idf_f)
		with open(offset_file, 'rb') as offset_f:
			self.offsets = pickle.load(offset_f)
		with open(url_map_file, 'rb') as map_f:
			self.url_map = pickle.load(map_f)
		with open(vector_lens_file, 'rb') as lens_f:
			self.vector_lens = pickle.load(lens_f)

	def retrieve_docs(self, tokens: ['tokens']):
		'''
		Utilize seek() operations to directly jump to the positions of all the query terms directly. 
		Documents are scored and ranked via lnc.ltc vector space scoring method. 
		'''		
		token_count = defaultdict(int)

		for token in tokens:
			token_count[token] += 1

		scores = defaultdict(int)		
		q_tfidf = dict()

		for token, q_freq in token_count.items():
			if token not in self.offsets:
				continue
			# calculate tfidf (ltc) of the query term for query vector
			q_tf = 1 + math.log(q_freq)
			q_tfidf[token] = q_tf * self.idf_dict[token] 

			# Find the posting list for the current query term from the index
			self.index_f.seek(self.offsets[token])
			line = self.index_f.readline()
			_ , posting_list = build_record(line)	

			for posting in posting_list:
				# don't consider postings with less than 100 tokens in the top-k
				if posting.total_tokens <= 250:
					continue 
				
				# Calculate the current ltc.lnc value of the current query term and add it to document score 
				scores[posting.doc_id] += q_tfidf[token] * posting.tf

		# Compute the length for the query vector 
		q_tfidf_vector_len = 0
		for tfidf in q_tfidf.values():
			q_tfidf_vector_len += pow(tfidf, 2)
		q_tfidf_vector_len = math.sqrt(q_tfidf_vector_len)		
		
		# calculating lnc.ltc cosine simularity 
		for doc_id, score in scores.items():
			# Compute the total vector length 
			total_vector_length = q_tfidf_vector_len * self.vector_lens[doc_id]

			# Normalize the score			
			normalized_score = score / total_vector_length
			scores[doc_id] = normalized_score				

		top_k = sorted(scores.keys(), key=lambda doc_id: scores[doc_id], reverse=True)[:10]	
		
		# for doc_id in top_k:
		# 	print(self.url_map[doc_id], scores[doc_id])  # print doc scores in terminal 

		results = [self.url_map[doc_id] for doc_id in top_k]

		return results


	def retrieve_docs_slow(self, tokens: ['tokens']):
		''' 
		Scans through the entire index file for the desired posting lists. 
		Documents are scored and via a tf-idf weight for each term.  
		'''		
		tokens = set(tokens)

		scores = defaultdict(int)		

		line = self.index_f.readline()
		while line and len(line) > 0:
			if get_record_term(line) in tokens:
				term, posting_list = build_record(line)
				if term in tokens:
					for posting in posting_list:
						# Calculate tf-idf weighting for current query term and document 
						scores[posting.doc_id] += self.idf_dict[term] * posting.tf	
					tokens.remove(term)
			if len(tokens) == 0:
				break
			line = self.index_f.readline()

		top_k = sorted(scores.keys(), key=lambda doc_id: scores[doc_id], reverse=True)[:10]	
		
		# for doc_id in top_k:
		# 	print(self.url_map[doc_id], scores[doc_id])  # print doc scores in terminal 

		results = [self.url_map[doc_id] for doc_id in top_k]
		self.index_f.seek(0)

		return results		

	def close(self):
		self.index_f.close()