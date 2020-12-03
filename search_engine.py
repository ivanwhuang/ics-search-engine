from posting import Posting
from queue import PriorityQueue 
from collections import defaultdict

from index_parser import build_record

try:
	import cPickle as pickle
except:
	import pickle

import math

index_file = 'index_dumps/final_index.txt'
url_map_file = 'index_dumps/url_map.pkl'
offset_file = 'index_dumps/term_offsets.pkl'
idf_file = 'index_dumps/idf.pkl'	

class SearchEngine():
	def __init__(self):
		self.index_f = open(index_file, 'r')
		with open(idf_file, 'rb') as idf_f:
			self.idf_dict = pickle.load(idf_f)

		with open(offset_file, 'rb') as offset_f:
			self.offsets = pickle.load(offset_f)
		with open(url_map_file, 'rb') as map_f:
			self.url_map = pickle.load(map_f)

	'''
	Old boolean retrieval method
	'''

	# def retrieve_docs(self, tokens: ['tokens']):
	# 	tokens = set(tokens)

	# 	records = PriorityQueue()

	# 	for token in tokens:
	# 		if token not in self.offsets:
	# 			continue 
	# 		else:
	# 			self.index_f.seek(self.offsets[token])
	# 			line = self.index_f.readline()
	# 			t, posting_list = build_record(line)
	# 			records.put((len(posting_list), {t}, posting_list))

	# 	if records.qsize() == 0:
	# 		return None

	# 	while records.qsize() > 1: 
	# 		r1 = records.get()
	# 		r2 = records.get()
			
	# 		t1, postings1 = r1[1:]
	# 		t2, postings2 = r2[1:]

	# 		token_list = t1 | t2 

	# 		p1 = 0
	# 		p2 = 0

	# 		common_postings = []

	# 		while p1 < len(postings1) and p2 < len(postings2):
	# 			if postings1[p1].doc_id == postings2[p2].doc_id:
	# 				common_postings.append(Posting(postings1[p1].doc_id, 
	# 									   postings1[p1].frequency + postings2[p2].frequency, 
	# 									   postings1[p1].total_tokens, 
	# 									   postings1[p1].tf + postings2[p2].tf))
	# 				p1 += 1 
	# 				p2 += 1
	# 			elif postings1[p1].doc_id < postings2[p2].doc_id:
	# 				p1 += 1
	# 			else:
	# 				p2 += 1

	# 		records.put((len(common_postings), token_list, common_postings))

	# 	self.index_f.seek(0)

	# 	if records.qsize() == 1:
	# 		merged_record = records.get()
	# 		return sorted(merged_record[2], key=lambda p: p.tf, reverse=True)[:10]


	def retrieve_docs(self, tokens: ['tokens']):
		token_count = defaultdict(int)

		for token in tokens:
			token_count[token] += 1

		# calculating lnc.ltc cosine simularity 
		scores = defaultdict(int)
		
		q_tfidf = dict()
		d_tfidf_vector = defaultdict(list)

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
				# Calculate tfidf (lnc) of the query term for document vector
				# since lnc, tfidf is just tf before normalization
				d_tfidf_vector[posting.doc_id].append(posting.tf)
				
				# Calculate the current ltc.lnc value of the current query term and add it to document score 
				scores[posting.doc_id] += q_tfidf[token] * posting.tf


		# Compute the length for the query vector 
		# q_tfidf_vector_len = 0
		# for tfidf in q_tfidf.values():
		# 	q_tfidf_vector_len += pow(tfidf, 2)
		# q_tfidf_vector_len = math.sqrt(q_tfidf_vector_len)

		# for doc_id, score in scores.items():
		# 	# Compute the length for the doc vector 
		# 	d_tfidf_vector_len = 0
		# 	for tfidf in d_tfidf_vector[doc_id]:
		# 		d_tfidf_vector_len += pow(tfidf, 2)
		# 	d_tfidf_vector_len = math.sqrt(d_tfidf_vector_len)

			# Compute the total vector length 
			# total_vector_length = q_tfidf_vector_len * d_tfidf_vector_len

			# compute and store the new noramlized score			
			# normalized_score = score / total_vector_length
			# scores[doc_id] = normalized_score

		top_k = sorted(scores.keys(), key=lambda doc_id: scores[doc_id], reverse=True)[:10]	
		results = [self.url_map[doc_id] for doc_id in top_k]

		return results

	def close(self):
		self.index_f.close()