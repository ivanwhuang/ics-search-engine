# ICS Search Engine
A search engine built from the ground up using web pages scraped from UC Irvine's *Information and Computer Science's (ICS)* domain.
It is capable of handling tens of thousands of documents, under harsh operational constriants and having a query response time under 300ms.

This search engine performs ranked retrieval using the lnc.ltc weighting scheme for a vector spaced scoring of documents.

> **The inverted index file was too large to upload, but it is inside dumps.zip.**

> **If you were interested in seeing the inverted index creation for yourself, unfortunately, even a compressed zip file 
of the total collection of documents is too large to upload to GitHub. You'll only be able to get the Search Engine running.**

This was a project assignment for CS-121 (Information Retreival) at UC Irvine.

## Getting Started
These instructions will get you a copy of the project up and running on your local machine

### Prerequisites/Installation
Make sure you have Python3 installed on your system. 

1. Clone the repo to get started. 
2. Unzip the contents of dumps.zip into a folder named 'dumps'. If you would like to unzip via terminal, run `unzip dumps.zip -d dumps`
3. Create a virtual environment if you would like. 
```
python3 -m venv env 
source env/bin/activate
```
4. Install the following Python packagaes
``` 
pip3 install nltk
pip3 install bs4
pip3 install flask
```

### Using the Terminal Interface 

Run `python3 interface.py` to start up the console interface.

At the start of the program and after every search is completed, you can either:
- s : [Search] if you would like to enter a new query
- q : [Quit] if you would like to terminate the program

The time it took to process the query is shown immediately after the list of top 10 results.

### Using the Web Interface 

Run `python3 web_ui.py` to start up the Web interface.

Visit [http://127.0.0.1:5000/](http://127.0.0.1:5000/) to view and use the system.





