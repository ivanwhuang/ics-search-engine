from flask import Flask, render_template, jsonify, make_response
from search_engine import SearchEngine
from index_parser import extract_tokens
import time

try:
	import cPickle as pickle
except:
	import pickle

import time

app = Flask(__name__)


def display_results(results):
	for i, result in enumerate(results, 1):
		doc_id, score = result
		print(i, url_map[doc_id], score)	

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/search/<query>')
def retrieve_docs(query):
	start_time = time.time()
	_ , tokens = extract_tokens(query)
	results = engine.retrieve_docs(tokens.keys())
	end_time = time.time()
	response_time = int((end_time - start_time) * 1000)
	print("Query Response Time: ", response_time, "ms\n")
	if results:
		res = make_response(jsonify({"results": results, "responseTime": response_time}), 200)
		return res 
	else:
		res = make_response(jsonify({"results": [], "responseTime": response_time}), 200)
		return res 

	# return render_template('index.html', )	


if __name__ == '__main__':
	engine = SearchEngine()
	app.run(debug=True)









