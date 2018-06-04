# -*- coding: utf-8 -*-
import math, pymongo, os, gridfs, json, pickle
from ngram import NGram
import multiprocessing as mp
from udic_nlp_API.settings_database import uri
from PMIofKCM.utils.graceful_auto_reconnect import graceful_auto_reconnect
from pympler.asizeof import asizeof

class PMI(object):
	"""docstring for PMI"""
	def __init__(self, lang, uri=None, ngram=False):
		self.client = pymongo.MongoClient(uri)
		self.uri = uri
		self.lang = lang
		self.db = self.client['nlp_{}'.format(self.lang)]
		self.fs = gridfs.GridFS(self.db)

		self.Collect = self.db['pmi']
		self.cpus = math.ceil(mp.cpu_count() * 0.2)
		self.frequency = {}

		if ngram:
			# use ngram for searching
			self.pmiNgram = NGram((i['key'] for i in self.db['pmi'].find({}, {'key':1, '_id':False})))

	def getWordFreqItems(self):
		# use cache
		if os.path.exists('frequency.pkl'):
			self.frequency = pickle.load(open('frequency.pkl', 'rb'))
			frequency_of_total_keyword = pickle.load(open('frequency_of_total_keyword.pkl', 'rb'))
			return frequency_of_total_keyword

		# return all frequency of word in type of dict.
		self.frequency = {}
		frequency_of_total_keyword = 0

		# iterate through gridFS
		for keyword in self.fs.list():
			cursor = self.fs.find({"filename": keyword})[0]
			value = {'PartOfSpeech':cursor.contentType, 'value':json.loads(self.fs.get(cursor._id).read().decode('utf-8'))}
			for correlation_keyword, PartOfSpeech, corTermCount in value['value']:
				frequency_of_total_keyword += corTermCount
				# accumulate keyword's frequency.
				self.frequency[keyword] = self.frequency.setdefault(keyword, 0) + corTermCount

		# iterate through all normal collection
		for i in self.db['kcm'].find({}):
			keyword = i['key']
			for correlation_keyword, PartOfSpeech, corTermCount in i['value']:
				frequency_of_total_keyword += corTermCount
				# accumulate keyword's frequency.
				self.frequency[keyword] = self.frequency.setdefault(keyword, 0) + corTermCount

		pickle.dump(self.frequency, open('frequency.pkl', 'wb'))
		pickle.dump(frequency_of_total_keyword, open('frequency_of_total_keyword.pkl', 'wb'))
		return frequency_of_total_keyword

	def build(self):
		self.Collect.remove({})
		# read all frequency from KCM and build all PMI of KCM in MongoDB. 
		# with format {key:'中興大學', freq:100, value:[(keyword, PMI-value), (keyword, PMI-value)...]}
		frequency_of_total_keyword = self.getWordFreqItems()
		print('frequency of total keyword:'+str(frequency_of_total_keyword))

		@graceful_auto_reconnect
		def process_job(job_list):
			# Each process need independent Mongo Client
			# or it may raise Deadlock in Mongo.
			client = pymongo.MongoClient(self.uri)
			db = client['nlp_{}'.format(self.lang)]
			process_collect = db['pmi']
			kcm_collect = db['kcm']
			fs = gridfs.GridFS(db)

			result = []
			for keyword, keyword_freq in job_list:
				pmiResult = []

				collection_cursor = kcm_collect.find({'key':keyword}, {'value':1, '_id':False}).limit(1)
				if collection_cursor.count() == 0:
					gridfs_cursor = fs.find({"filename": keyword}).limit(1)[0]
					cursor_result = json.loads(fs.get(gridfs_cursor._id).read().decode('utf-8'))[:500]
				else:
					cursor_result = collection_cursor[0]['value']
				for kcmKeyword, PartOfSpeech, kcmCount in cursor_result:
					# algorithm:
					# PMI = log2(p(x, y)/p(x)*p(y)) 
					# p(x, y) = frequency of (x, y) / frequency of total keyword.
					# p(x) = frequency of x / frequency of total keyword.
					value = math.log2( 
						kcmCount * frequency_of_total_keyword / (keyword_freq * self.frequency[kcmKeyword]) 
					)

					# this equation is contributed by 陳聖軒. 
					# contact him with facebook: https://www.facebook.com/henrymayday
					value *= math.log2(self.frequency[kcmKeyword])

					pmiResult.append((kcmKeyword, value))

				pmiResult = sorted(pmiResult, key = lambda x: -x[1])
				result.append({'key':keyword, 'freq':keyword_freq, 'value':pmiResult})

				# Insert Collections into MongoDB
				if len(result) > 5000:
					process_collect.insert(result)
					result = []

		amount = math.ceil(len(self.frequency)/self.cpus)
		job_list = list(self.frequency.items())
		job_list = [job_list[i:i + amount] for i in range(0, len(self.frequency), amount)]
		processes = [mp.Process(target=process_job, kwargs={'job_list':job_list[i]}) for i in range(self.cpus)]
		for process in processes:
			process.start()
		for process in processes:
			process.join()
		self.Collect.create_index([("key", pymongo.HASHED)])

	def get(self, keyword, amount):
		cursor = self.Collect.find({'key':keyword}, {'value':1, '_id':False}).limit(1)
		if cursor.count() != 0:
			return {'key':keyword, 'value':cursor[0]['value'][:amount], 'similarity':1}
		else:
			pmiNgramKeyword = self.pmiNgram.find(keyword)
			if pmiNgramKeyword:
				result = self.Collect.find({'key':pmiNgramKeyword}, {'value':1, '_id':False}).limit(1)[0]['value'][:amount]
				return {'key':pmiNgramKeyword, 'value':result, 'similarity':self.pmiNgram.compare(pmiNgramKeyword, keyword)}
		return {}