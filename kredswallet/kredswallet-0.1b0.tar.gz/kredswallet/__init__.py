import base64,time,requests,hashlib,json,hmac

class KredsAPI():
	def __init__(self,KREDS_API,KREDS_SECRET):
		self.url = "https://kredswallet.com/api"
		self.KREDS_API = KREDS_API
		self.KREDS_SECRET = KREDS_SECRET

	def genHeaders(self,params={}):
		params["nonce"] = str(round(time.time()*1000))
		payload = base64.b64encode(json.dumps(params).encode())
		SIGNATURE = hmac.new(payload,self.KREDS_SECRET.encode(),hashlib.sha512).hexdigest()
		return {
			"context-type":"application/json",
			"X-WWT-APIKEY":self.KREDS_API,
			"X-WWT-PAYLOAD":payload.decode("utf-8"),
			"X-WWT-SIGNATURE":SIGNATURE
		}

	def status(self): # Returns status of the API
		return requests.get("{}/status".format(self.url)).json()

	def info(self): # Returns information on the kreds wallet
		return requests.get("{}/info".format(self.url)).json()

	def getAddresses(self): # Returns information on the addresses for your account
		headers = self.genHeaders()
		return requests.get("{}/addresses".format(self.url),headers=headers).json()

	def newAddress(self): # Generates a fresh address for your users
		headers = self.genHeaders()
		return requests.post("{}/addresses".format(self.url),headers=headers).json()
		
	def balance(self): # Retrieves user's balance
		headers = self.genHeaders()
		return requests.get("{}/balance".format(self.url),headers=headers).json()

	def deposits(self): # Fetches account deposits
		headers = self.genHeaders()
		return requests.get("{}/deposits".format(self.url),headers=headers).json()

	def summary(self): # Gathers summary of the user's account
		headers = self.genHeaders()
		return requests.get("{}/summary".format(self.url),headers=headers).json()

	def transactions(self): # Gather information on all transactions for a user's account
		headers = self.genHeaders()
		return requests.get("{}/transactions".format(self.url),headers=headers).json()

	def transaction(self,TXID): # Gather details of provided TXID
		headers = self.genHeaders()
		return requests.get("{}/transactions/{}".format(self.url,TXID),headers=headers).json()

	def withdraws(self): # Retrieve user's withdrawals
		headers = self.genHeaders()
		return requests.get("{}/withdraws".format(self.url),headers=headers).json()

	def withdraw(self,ADDRESS,AMT,FEE): # Generate a new withdrawal
		headers = self.genHeaders()
		return requests.post("{}/withdraws/{}/{}/{}".format(self.url,ADDRESS,AMT,FEE),heades=headers).json()

	def account(self): # Creates new API information
		headers = self.genHeaders()
		return requests.post("{}/account".format(self.url),headers=headers).json()

	def credit(self,ACCOUNT,AMT): # Credits an account
		headers = self.genHeaders()
		return requests.post("{}/account/credit/{}/{}".format(self.url,ACCOUNT,AMT),headers=headers).json()
