# Inverted Index 
from collections import defaultdict, OrderedDict
import re
import json 
import math

# cPickle is the C implementation of pickle. It runs faster than normal pickle module
try:
	import cPickle as pickle
except:
	import pickle

from bs4 import BeautifulSoup
from posting import Posting
from index_parser import build_record, stringify_record, parse_url, extract_tokens

# Capitalize this later
base_dump_path = 'index_dumps/'

class NoHtml(Exception):
	pass

class InvertedIndex():
	def __init__(self):
		self.url_map = dict()
		self.unique_urls = set()
		self.unique_tokens = set()
		self.index = defaultdict(list)
		self.id_count = 0
		self.num_seen_before = 0
		self.num_non_HTML = 0
		self.mergeNum = 0 		

	# Given a batch of documents, build a partial index
	def build_partial_index(self, documents, dump_file):
		for doc_file in documents:
			with open(doc_file) as doc:
				doc_data = json.load(doc)
				self._add_to_index(doc_data)

		self._sort_and_dump(dump_file)

		self.index.clear()	

	def merge_indexes(self, dump_file1, dump_file2, merge_file):
		f1 = open(dump_file1, 'r')
		f2 = open(dump_file2, 'r')
 
		with open(merge_file, 'w') as mf:
			line1 = f1.readline()
			line2 = f2.readline() 
	
			while line1 and line2 and len(line1) > 0 and len(line2) > 0: 
				t1, postings1 = build_record(line1)
				t2, postings2 = build_record(line2)

				if t1 == t2:
					merged_postings = []
					p1 = 0
					p2 = 0
					while p1 < len(postings1) and p2 < len(postings2):
						if postings1[p1].doc_id < postings2[p2].doc_id:
							merged_postings.append(postings1[p1])
							p1 += 1
						else:
							merged_postings.append(postings2[p2])
							p2 += 1

					while p1 < len(postings1):
						merged_postings.append(postings1[p1])
						p1 += 1	

					while p2 < len(postings2):
						merged_postings.append(postings2[p2])
						p2 += 1	

					merged_record = stringify_record(t1, merged_postings)
					mf.write(merged_record)

					line1 = f1.readline()
					line2 = f2.readline()				
							
				elif t1 < t2:
					mf.write(line1)
					line1 = f1.readline()
				else:
					mf.write(line2)
					line2 = f2.readline()

			while line1 and len(line1) > 0:
				mf.write(line1)
				line1 = f1.readline()
			
			while line2 and len(line2) > 0:
				mf.write(line2)
				line2 = f2.readline()	
						
		f1.close()
		f2.close()

	# def write_tfidf(self, index_file, final_index_file, n_docs):
	# 	final_f = open(final_index_file, 'w')
	# 	index_f = open(index_file, 'r')

	# 	line = index_f.readline()
	# 	while line and len(line) > 0:
	# 		t, postings = build_record(line)
	# 		idf = math.log(n_docs / len(postings))
	# 		for posting in postings:
	# 			tf = posting.frequency / posting.total_tokens
	# 			posting.tfidf = tf * idf
			
	# 		new_record = stringify_record(t, postings) 
	# 		final_f.write(new_record)
	# 		line = index_f.readline()

	# 	index_f.close()
	# 	final_f.close()

	def store_idf(self, index_file, idf_file):
		idf_dict = dict()

		with open(index_file, 'r') as index_f:
			line = index_f.readline()

			while line and len(line) > 0:
				t, postings = build_record(line)
				idf = math.log(self.id_count / len(postings))
				idf_dict[t] = idf 

				line = index_f.readline()

		with open(idf_file, 'wb') as idf_f:
			pickle.dump(idf_dict, idf_f)

	def print_index(self):
		for term, postings in self.index.items():
			print(" ---- TERM: " + term + " ----")
			for posting in postings:
				print(posting.doc_id, self.url_map[posting.doc_id], posting.frequency)

	def print_report(self):
		print("------ Index Report -------")
		print("Number of documents indexed: " + str(self.id_count))
		print("Number of unique tokens: " + str(len(self.unique_tokens)))
		print("Number of Non-HTML Files: " + str(self.num_non_HTML))
		print("Number of urls already indexed: " + str(self.num_seen_before))

	# Index a document 
	def _add_to_index(self, document: 'Dictionary decoded from JSON'):		
		parsed_url = parse_url(document["url"])
		print("Indexing Doc " + str(self.id_count) + ": " + parsed_url)

		if parsed_url in self.unique_urls:
			# Skip this file if the parsed url is already in the url_map.
			self.num_seen_before += 1
			return 

		try: 
			soup = BeautifulSoup(document['content'], 'html.parser')

			if soup.find('html') == None:
				raise NoHtml	
			
			total_tokens, tokens = extract_tokens(soup.get_text(' '))		

			for token, freq in tokens.items():
				self.index[token].append(Posting(self.id_count, freq, total_tokens))			
		except NoHtml:
			# Skip this file due to no html content
			self.num_non_HTML += 1
			return

		self.url_map[self.id_count] = parsed_url	
		self.unique_urls.add(parsed_url)
	
		self.id_count += 1

	# Sorts the inverted index and dumps the content into specified dump file
	def _sort_and_dump(self, dump_file):
		with open(dump_file, 'w') as f:
			for term in sorted(self.index.keys()):
				record = stringify_record(term, self.index[term])
				f.write(record)
				del self.index[term]	

	# Store hashmap of doc_ids to urls 
	def dump_url_map(self, dump_file):
		with open(dump_file, 'wb') as f:
			pickle.dump(self.url_map, f)

	def dump_term_offsets(self, index_file, dump_file):
		offset_dict = dict()

		offset = 0 
		with open (index_file, 'r') as index_f:
			line = index_f.readline()
			while line and len(line) > 0:
				t, postings = build_record(line)
				offset_dict[t] = offset 
				offset = index_f.tell()
				line = index_f.readline()

		with open (dump_file, 'wb') as f:
			pickle.dump(offset_dict, f)





