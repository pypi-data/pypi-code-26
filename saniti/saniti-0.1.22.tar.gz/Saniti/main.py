import nltk
# import gensim
# import pandas
import string
from nltk.corpus import stopwords
from gensim.models.doc2vec import TaggedDocument
from gensim.corpora import Dictionary
"""
TODO
stemming - DONE
lemmatizing - DONE
pos filter
tfidf splitter
w2v theme relevence
w2v weightings
frequency filtering (found more than twice)

RESEARCH
kwargumenrts - ad hoc arguments for theme relevence

"""

class saniti:
	def __init__(self, text = [], pipeline = [], **kwargs):

		#setup

		self.processes = {"token": self.token,
						  "depunct": self.depunct,
						  "unempty": self.unempty,
						  "out_tag_doc": self.out_tag_doc,
						  "out_corp_dict": self.out_corp_dic,
						  "lemma": self.lemma,
						  "destop": self.destop,
						  "stem": self.stem}
		self.pipeline = pipeline
		self.original_text = text


		if text != []:
			self.text = self.process(text, self.pipeline, **kwargs)

	def process(self, text, pipeline, **kwargs):
		self.text = text

		for line in pipeline:
			text = self.processes[line](text, **kwargs)

		return text

	def destop(self, text, **kwargs):
		text = [[word for word in doc if word not in stopwords.words("english")] for doc in text]
		return text

	def token(self, text, **kwargs):

		if "tokenizer" in kwargs:
			tokenizer = kwargs["tokenizer"]
		else:
			tokenizer = nltk.word_tokenize

		text = [tokenizer(x) for x in text]
		return text

	def depunct(self, text, **kwargs):

		if "puct" in kwargs:
			punct = kwargs["punct"]
		else:
			punct = string.punctuation

		punct = str.maketrans("", "", punct)
		text = [[s.translate(punct) for s in doc] for doc in text]
		return text

	def unempty(self, text, **kwargs):

		text = [[s for s in doc if s != ""] for doc in text]

		return text

	def lemma(self, text, **kwargs):

		if "lemmatizer" in kwargs:
			lemmatizer = kwargs["lemmatizer"]
		else:
			lemmatizer = nltk.WordNetLemmatizer()
		text = [[lemmatizer.lemmatize(w) for w in doc] for doc in text]

		return text

	def stem(self, text, **kwargs):

		if "stemmer" in kwargs:
			stemmer = kwargs["stemmer"]
		else:
			stemmer = nltk.stem.PorterStemmer()


		text = [[stemmer.stem(word) for word in doc] for doc in text]

		return text

	def out_corp_dic(self, text, **kwargs):

		dictionary = Dictionary(text)
		corpus = [dictionary.doc2bow(doc) for doc in text]

		return {"dictionary": dictionary, "corpus": corpus}

	def out_tag_doc(self, text, **kwargs):

		if "tags" in kwargs:
			tags = kwargs["tags"]
		else:
			tags = []

		if tags == []:
			if self.original_text != []:
				tags = self.original_text
			else :
				tags = [" ".join(doc) for doc in text]
		list2 = []
		for xt, xid in zip(text, tags):
			try:
				td = TaggedDocument(xt, [xid])
				list2.append(td)

			except:
				print(f"disambig {x}")

		return(list2)

if __name__ == "__main__":

	original_text = ["I like to moves it, move its", "I likeing to move it!", "the of"]

	text = saniti(original_text, ["token", "destop", "depunct", "unempty", "stem", "out_corp_dict"], punct = ["."])

	print(text.text)

	sani1 = saniti()
	text = sani1.process(original_text, ["token", "destop", "depunct", "unempty", "lemma", "out_tag_doc"])
	print(text)




