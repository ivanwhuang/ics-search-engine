import os
import glob
from collections import deque
from inverted_index import InvertedIndex

try:
	import cPickle as pickle
except:
	import pickle

import re

base_doc_path = 'ics_docs/'
base_dump_path = 'index_dumps/'
test_dump_path = 'test_dumps/'

def main():
	index = InvertedIndex()
	batch_size = 15000
	doc_stack = []
	dump_file_paths = deque()

	batch_num = 0
	merge_num = 0

	for doc_file in glob.iglob(base_doc_path + '/**/*.json', recursive=True):
		doc_stack.append(doc_file)	

	if len(doc_stack) == 0:
		print("No documents found to index")
		return				

	while len(doc_stack) > 0:
		batch = []
		# Get Batch
		for i in range(min(batch_size, len(doc_stack))):
			batch.append(doc_stack.pop())
		
		dump_file = base_dump_path + 'dump' + str(batch_num) + '.txt'
		index.build_partial_index(batch, dump_file)
		dump_file_paths.append(dump_file)

		batch_num += 1

	index.print_report()
	index.dump_url_map(base_dump_path + 'url_map.pkl')
	index.dump_vector_lens(base_dump_path + 'vector_lens.pkl')

	while len(dump_file_paths) > 1:
		dump1 = dump_file_paths.popleft()
		dump2 = dump_file_paths.popleft()
		merge_file = base_dump_path + 'merge' + str(merge_num) + '.txt'

		index.merge_indexes(dump1, dump2, merge_file)
		dump_file_paths.appendleft(merge_file)	

		merge_num += 1

	index_path = dump_file_paths.pop()
	os.rename(index_path, base_dump_path + 'final_index.txt')

	index.store_idf(base_dump_path + 'final_index.txt', base_dump_path + 'idf.pkl')		

	index.dump_term_offsets(base_dump_path + 'final_index.txt', base_dump_path + 'term_offsets.pkl')

def test_build_index():
	index = InvertedIndex()
	batch_size = 7
	doc_stack = []
	dump_file_paths = deque()

	batch_num = 0
	merge_num = 0

	for doc_file in glob.iglob(base_doc_path + '/aiclub_ics_uci_edu/*.json', recursive=True):
		doc_stack.append(doc_file)		

	for doc_file in glob.iglob(base_doc_path + '/hobbes_ics_uci_edu/*.json', recursive=True):
		doc_stack.append(doc_file)		

	for doc_file in glob.iglob(base_doc_path + '/chenli_ics_uci_edu/*.json', recursive=True):
		doc_stack.append(doc_file)

	if len(doc_stack) == 0:
		print("No documents found to index")
		return		

	while len(doc_stack) > 0:
		batch = []

		# Get Batch
		for i in range(min(batch_size, len(doc_stack))):
			batch.append(doc_stack.pop())

		dump_file = test_dump_path + 'dump' + str(batch_num) + '.txt'			
		
		index.build_partial_index(batch, dump_file)
		dump_file_paths.append(dump_file)
		batch_num += 1

	index.print_report()	
	index.dump_url_map(test_dump_path + 'url_map.pkl')
	index.dump_vector_lens(test_dump_path + 'vector_lens.pkl')

	while len(dump_file_paths) > 1:
		dump1 = dump_file_paths.popleft()
		dump2 = dump_file_paths.popleft()
		merge_file = test_dump_path + 'merge' + str(merge_num) + '.txt'

		index.merge_indexes(dump1, dump2, merge_file)
		dump_file_paths.appendleft(merge_file)	

		merge_num += 1

	index_path = dump_file_paths.pop()
	os.rename(index_path, test_dump_path + 'final_index.txt')

	index.store_idf(test_dump_path + 'final_index.txt', test_dump_path + 'idf.pkl')

	index.dump_term_offsets(test_dump_path + 'final_index.txt', test_dump_path + 'term_offsets.pkl')


if __name__ == "__main__":
	main()
