from search_engine import SearchEngine
from index_parser import extract_tokens

try:
	import cPickle as pickle
except:
	import pickle

import time

class Interface():
	# def __init__(self, index_file, url_map_file, idf_file, offset_file):
	# 	self.engine = SearchEngine(index_file, idf_file, offset_file)

	def __init__(self, url_map_file):
		self.engine = SearchEngine()	

	def start(self):
		with open(url_map_file, 'rb') as map_f:
			self.url_map = pickle.load(map_f)		

			while True:
				option = input("Enter Q to Quit or S to Search: ").lower()
				if option == 'q':
					self.engine.close()
					return
				elif option == 's':
					query = input("Enter a search query: ")
					start_time = time.time()
					_ , tokens = extract_tokens(query)
					results = self.engine.retrieve_docs(tokens.keys())
					end_time = time.time()
					response_time = (end_time - start_time) * 1000
					print("Query Response Time: ", response_time, "ms\n")
					if results:
						# self.display_results_data(results)
						self.display_results(results)
					else:
						print("No results")
				else:
					print("Please specify a valid option.")

	def display_results(self, results):
		for i, result in enumerate(results, 1):
			doc_id, score = result
			print(i, self.url_map[doc_id], score)	

	# def display_results_data(self, results):
	# 	for i, posting in enumerate(results, 1):
	# 		print(i, posting.doc_id, "freq:", posting.frequency, 
	# 			  "Total Tokens:", posting.total_tokens, "tf:", 
	# 			  posting.tf, self.url_map[posting.doc_id])	

if __name__ == "__main__":
	# index_file = 'index_dumps/final_index.txt'
	url_map_file = 'index_dumps/url_map.pkl'
	# offset_file = 'index_dumps/term_offsets.pkl'
	# idf_file = 'index_dumps/idf.pkl'
	# new_session = Interface(index_file, url_map_file, idf_file, offset_file)

	print("Starting ICS Document Retrieval System...")

	new_session = Interface(url_map_file)
	new_session.start()