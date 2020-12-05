import glob
from inverted_index import InvertedIndex

base_doc_path = 'ics_docs/'
base_dump_path = 'dumps/index_dumps/'
test_dump_path = 'dumps/test_dumps/'

def build_ics_index():
	'''Build an inverted index for the entire set of ICS documents'''
	index = InvertedIndex()
	batch_size = 15000
	docs = []

	for doc_file in glob.iglob(base_doc_path + '/**/*.json', recursive=True):
		docs.append(doc_file)	

	index.build_full_index(docs, batch_size, base_dump_path)
	
def build_test_index():
	'''Build an inverted index for a small set of ICS documents for testing/debugging purposes'''
	index = InvertedIndex()
	batch_size = 7
	docs = []

	for doc_file in glob.iglob(base_doc_path + '/aiclub_ics_uci_edu/*.json', recursive=True):
		docs.append(doc_file)		

	for doc_file in glob.iglob(base_doc_path + '/hobbes_ics_uci_edu/*.json', recursive=True):
		docs.append(doc_file)		

	for doc_file in glob.iglob(base_doc_path + '/chenli_ics_uci_edu/*.json', recursive=True):
		docs.append(doc_file)

	index.build_full_index(docs, batch_size, test_dump_path)


if __name__ == "__main__":
	# build_ics_index()
	build_test_index()


