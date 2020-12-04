# Inverted Index 
from collections import defaultdict, deque
import re
import json 
import math
import os 

# cPickle is the C implementation of pickle. It runs faster than normal pickle module
try:
	import cPickle as pickle
except:
	import pickle

from bs4 import BeautifulSoup
from posting import Posting
from index_parser import build_record, stringify_record, parse_url, extract_tokens

class NoHtml(Exception):
	pass

class InvertedIndex():
	def __init__(self):
		self.index = defaultdict(list)
		self.id_count = 0		
		self.url_map = dict()
		self.vector_lens = dict()
		self.unique_urls = set()
		self.unique_tokens = set()
		self.num_seen_before = 0
		self.num_non_HTML = 0
		self.mergeNum = 0 		

	def build_full_index(self, documents, batch_size, dump_path): 
		'''
		Given a list of documents and a batch size, create partial indexes that have 
		a maximum capacity of the specified batch size. Then sequentially merge these 
		partial indexes in order to build the full inverted index. 
		'''
		if len(documents) == 0:
			print("No documents found to index")
			return			

		batch_num = 0
		merge_num = 0
		dump_file_paths = deque()

		while len(documents) > 0:
			batch = []
			# Get Batch
			for i in range(min(batch_size, len(documents))):
				batch.append(documents.pop())
			
			dump_file = dump_path + 'dump' + str(batch_num) + '.txt'
			# Build a partial index for each batch 
			self.build_partial_index(batch, dump_file)
			dump_file_paths.append(dump_file)

			batch_num += 1

		self.print_report()

		# Merge in the order of merging smaller index files first. 
		while len(dump_file_paths) > 1:
			dump1 = dump_file_paths.popleft()
			dump2 = dump_file_paths.popleft()
			merge_file = dump_path + 'merge' + str(merge_num) + '.txt'

			self.merge_indexes(dump1, dump2, merge_file)
			dump_file_paths.appendleft(merge_file)	

			merge_num += 1

		# Rename the final merged file 
		index_path = dump_file_paths.pop()
		os.rename(index_path, dump_path + 'final_index.txt')

		# Dump all info that is necessary for scoring and retrieval 
		self._dump_idf(dump_path + 'final_index.txt', dump_path + 'idf.pkl')	
		self._dump_term_offsets(dump_path + 'final_index.txt', dump_path + 'term_offsets.pkl')
		self._dump_url_map(dump_path + 'url_map.pkl')
		self._dump_vector_lens(dump_path + 'vector_lens.pkl')

	def merge_indexes(self, dump_file1, dump_file2, merge_file):
		'''Merge two inverted index files'''

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
		os.remove(dump_file1)
		os.remove(dump_file2)

	def build_partial_index(self, documents, dump_file):
		'''Given a batch of documents, build a partial index'''
		for doc_file in documents:
			with open(doc_file) as doc:
				doc_data = json.load(doc)
				self._add_to_index(doc_data)

		self._sort_and_dump(dump_file)
		self.index.clear()	

	
	def print_report(self):
		'''Print statistics of Inverted Index'''
		print("------ Index Report -------")
		print("Number of documents indexed: " + str(self.id_count))
		print("Number of unique tokens: " + str(len(self.unique_tokens)))
		print("Number of Non-HTML Files: " + str(self.num_non_HTML))
		print("Number of urls already indexed: " + str(self.num_seen_before) + "\n")				
 
	def _add_to_index(self, document: 'Dictionary decoded from JSON'):	
		'''
		For given document, create a posting for each unique term in the document and 
		append it to its respective posting list 

		'''

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
			vector_len = 0	

			for token, freq in tokens.items():
				tf = 1 + math.log(freq)
				self.index[token].append(Posting(self.id_count, freq, total_tokens, tf))
				vector_len += pow(tf, 2)	
			vector_len = math.sqrt(vector_len)
			self.vector_lens[self.id_count] = vector_len

		except NoHtml:
			# Skip this file due to no html content
			self.num_non_HTML += 1
			return

		self.url_map[self.id_count] = parsed_url	
		self.unique_urls.add(parsed_url)
		self.id_count += 1

	def _sort_and_dump(self, dump_file):
		'''Sort the partial inverted index and dump the content into specified dump file'''
		with open(dump_file, 'w') as f:
			for term in sorted(self.index.keys()):
				record = stringify_record(term, self.index[term])
				f.write(record)
				del self.index[term]				

	def _dump_idf(self, index_file, dump_file):
		'''Dump hashmap of the IDF values corresponding to each term'''
		idf_dict = dict()

		with open(index_file, 'r') as index_f:
			line = index_f.readline()

			while line and len(line) > 0:
				t, postings = build_record(line)
				idf = math.log(self.id_count / len(postings))
				idf_dict[t] = idf 

				line = index_f.readline()

		with open(dump_file, 'wb') as f:
			pickle.dump(idf_dict, f)				

	def _dump_url_map(self, dump_file):
		'''Dump hashmap of the urls corresponding to each document'''
		with open(dump_file, 'wb') as f:
			pickle.dump(self.url_map, f)

	def _dump_vector_lens(self, dump_file):
		'''Dump hashmap of vector lengths of each document'''
		with open(dump_file, 'wb') as f:
			pickle.dump(self.vector_lens, f)

	def _dump_term_offsets(self, index_file, dump_file):
		'''Dump hashmap of term offsets for each term in the index file'''
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



