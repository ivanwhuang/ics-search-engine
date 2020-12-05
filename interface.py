from search_engine import SearchEngine
from index_parser import extract_tokens

try:
	import cPickle as pickle
except:
	import pickle

import time

class Interface():
	def __init__(self):
		self.engine = SearchEngine()	

	def start(self):	
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
				# results = self.engine.retrieve_docs_slow(tokens.keys())
				end_time = time.time()
				response_time = (end_time - start_time) * 1000
				print("Query Response Time: ", response_time, "ms\n")
				if results:
					for i, result in enumerate(results, 1):
						print(i, result)
				else:
					print("No results")
			else:
				print("Please specify a valid option.")

if __name__ == "__main__":
	print("Starting ICS Document Retrieval System...")
	new_session = Interface()
	new_session.start()