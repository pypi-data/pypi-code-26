import os,matplotlib.pyplot as plt, numpy as np, datetime as dtm
from scipy.optimize import curve_fit
from scipy.special import erfc
from ast import literal_eval
import sqlite3
from npat.reactions import isotope
from npat.misc import plotter


class spectrum(object):
	def __init__(self,filename='',directory='',read_maestro=True):
		self.filename,self.directory = filename,directory+('' if directory.endswith('/') else '/') if directory!='' else ''
		self.peak_fits,self.calibrate,self.meta,self.spec = None,False,{},[]
		if read_maestro and filename!='':
			self.init_maestro(filename,directory)
		self.clr = plotter().pallate()
	def init_maestro(self,filename,directory=''):
		self.filename,self.directory = filename,directory+('' if directory.endswith('/') else '/') if directory!='' else ''
		word,data = '',{}
		for ln in open(self.directory+filename,'r').read().split('\n')[:-1]:
			if ln.startswith('$'):
				word = ln.strip().split('$')[1].split(':')[0]
				data[word] = []
				continue
			data[word].append(ln.strip())
		self.start_time = dtm.datetime.strptime(data['DATE_MEA'][0],'%m/%d/%Y %H:%M:%S')
		self.live_time = float(data['MEAS_TIM'][0].split(' ')[0])
		self.real_time = float(data['MEAS_TIM'][0].split(' ')[1])
		self.spec = map(int,data['DATA'][1:])
		self.engcal = [float(i) for i in reversed(data['ENER_FIT'][0].split(' '))]
		self.effcal = [float(i) for i in data['SHAPE_CAL'][1].split(' ')]
		self.E_range = [self.engcal[0]*i+self.engcal[1] for i in range(len(self.spec))]
		self.meta = literal_eval(''.join(data['META'])) if 'META' in data else {'res':0.05,'R':0.2,'alpha':0.9}
		self.meta['res'],self.meta['R'],self.meta['alpha'] = (self.meta['res'] if 'res' in self.meta else 0.05),(self.meta['R'] if 'R' in self.meta else 0.2),(self.meta['alpha'] if 'alpha' in self.meta else 0.9)
		self.errata = [data['SPEC_ID'],data['SPEC_REM'],data['ROI'],data['PRESETS'],data['MCA_CAL']]
		self.rescal = self.meta['res']
		self.SNP = self.SNIP()
		self.QSNP = np.zeros(len(self.spec)).tolist()
	def init_db(self,db=None,db_connection=None,db_name=None,db_path=None):
		self.db,self.db_connection = None,None
		if db is not None and db_connection is not None:
			self.db = db
			self.db_connection = db_connection
		elif db_name is not None:
			db_path = './' if db_path is None else db_path
			db_fnm = db_path+('' if db_path.endswith('/') else '/')+db_name
			if not os.path.exists(db_fnm):
				f = open(db_fnm,'wb')
				f.close()
			self.db_connection = sqlite3.connect(db_fnm)
			self.db = self.db_connection.cursor()
		if self.db is not None:
			if len(list(self.db.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="peaks"')))==0:
				self.db.execute("CREATE TABLE 'peaks' ( `idx` INTEGER, `isotope` TEXT, `energy` REAL, `intensity` REAL, `unc_intensity` REAL, `N` INTEGER, `unc_N` REAL, `efficiency` REAL, `unc_efficiency` REAL, `efficiency_correction` REAL, `chi2` REAL, `fit` TEXT, `unc_fit` TEXT )")
			if len(list(self.db.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="spectra"')))==0:
				self.db.execute("CREATE TABLE `spectra` ( `idx` INTEGER, `filename` TEXT, `directory` TEXT, `start_time` TEXT, `live_time` REAL, `real_time` REAL, `meta` TEXT )")
			self.db_connection.commit()
	def write_db(self,calibrate=False):
		idx_ls = list(self.db.execute('SELECT idx FROM spectra WHERE filename=? AND directory=?',(self.filename,self.directory)))
		if len(idx_ls)==0:
			idx_tb = [i[0] for i in self.db.execute('SELECT idx FROM spectra')]
			idx = max(idx_tb)+1 if len(idx_tb)>0 else 1
			self.db.execute('INSERT INTO spectra VALUES (?,?,?,?,?,?,?)',(idx,self.filename,self.directory,self.start_time.strftime('%m/%d/%Y %H:%M:%S'),self.live_time,self.real_time,str(self.meta)))
		else:
			idx = idx_ls[0][0]
		self.db.execute('DELETE FROM peaks WHERE idx=?',(idx,))
		for pk in self.get_fmt_pks(calibrate):
			self.db.execute('INSERT INTO peaks VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',(idx,pk['istp'],pk['E'],pk['I'],pk['unc_I'],pk['N'],pk['unc_N'],pk['eff'],pk['unc_eff'],pk['eff_corr'],pk['chi2'],str(pk['fit']),str(pk['unc'])))
		self.db_connection.commit()
	def get_fmt_pks(self,calibrate=False):
		pks = []
		for pk in self.fit_peaks(calibrate):
			N,M = len(pk['fit'])/(5 if self.calibrate else 3),(5 if self.calibrate else 3)
			for m in range(N):
				info,fit,unc = pk['pk_info'][m],pk['fit'][m*M:m*M+M],[u[m*M:m*M+M] for u in pk['unc'][m*M:m*M+M]]
				pks.append({'istp':info[3],'E':info[0],'I':info[1],'unc_I':info[2],'N':info[4],'unc_N':info[5],'eff':self.map_efficiency(info[0]),'unc_eff':self.map_unc_efficiency(info[0]),'eff_corr':self.map_efficiency_correction(info[0]),'chi2':info[6],'fit':fit,'unc':unc})
		return pks
	def read_db(self,update=False):
		idx_ls = list(self.db.execute('SELECT idx FROM spectra WHERE filename=? AND directory=?',(self.filename,self.directory)))
		if len(idx_ls)==0:
			return []
		peaks,idx = [],idx_ls[0][0]
		if update:
			rd = list(self.db.execute('SELECT * FROM spectra WHERE idx=?',(idx,)))[0]
			self.update_params(start_time=str(rd[3]),live_time=rd[4],real_time=rd[5],meta=literal_eval(rd[6]))
		return [{'istp':str(p[1]),'E':p[2],'I':p[3],'unc_I':p[4],'N':p[5],'unc_N':p[6],'eff':p[7],'unc_eff':p[8],'eff_corr':p[9],'chi2':p[10],'fit':literal_eval(str(p[11])),'unc':literal_eval(str(p[12]))} for p in self.db.execute('SELECT * FROM peaks WHERE idx=?',(idx,))]
	def update_params(self,start_time=None,live_time=None,real_time=None,engcal=None,effcal=None,meta=None):
		if start_time is not None:
			if type(start_time)==str:
				self.start_time = dtm.datetime.strptime(start_time,'%m/%d/%Y %H:%M:%S')
			self.start_time = start_time
		if live_time is not None:
			self.live_time = live_time
		if real_time is not None:
			self.real_time = real_time
		if engcal is not None:
			self.engcal = engcal
			self.E_range = [self.engcal[0]*i+self.engcal[1] for i in range(len(self.spec))]
		if effcal is not None:
			self.effcal = effcal
		if meta is not None:
			for itm in meta:
				self.meta[itm] = meta[itm]
			self.rescal = self.meta['res'] if 'res' in self.meta else 0.05
			if len(self.spec)>0:
				self.SNP = self.SNIP()
	def write_maestro(self):
		groups = ['SPEC_ID','SPEC_REM','DATE_MEA','MEAS_TIM','DATA','ROI','PRESETS','ENER_FIT','MCA_CAL','SHAPE_CAL','META']
		data = self.errata[:2]+[[self.start_time.strftime('%m/%d/%Y %H:%M:%S')]]+[[str(int(self.live_time))+' '+str(int(self.real_time))]]
		data.append(['0 '+str(len(self.spec)-1)]+[''.join([' ' for i in range(7-int(np.log(max((s,1)))/np.log(10.0)))])+str(s) for s in self.spec])
		data += self.errata[2:4]+[[str(self.engcal[1])+' '+str(self.engcal[0])]]+[self.errata[4]]
		data += [[str(len(self.effcal)),' '.join(map(str,self.effcal))]]+[[str(self.meta),'']]
		f = open(self.directory+self.filename,'w+')
		f.write('\n'.join(['$'+groups[N]+':\n'+'\n'.join(d) for N,d in enumerate(data)]))
		f.close()
	def get_plot_spec(self,logscale=True):
		lim_y = 1 if logscale else 0
		bn = [max((self.spec[0],lim_y))]
		for i in range(len(self.spec)-1):
			bn.append(max((self.spec[i],lim_y)))
			bn.append(max((self.spec[i+1],lim_y)))
		return bn
	def get_plot_energy(self):
		eng,bn = [self.engcal[0]*(i-0.5)+self.engcal[1] for i in range(len(self.spec))],[]
		for i in range(1,len(eng)):
			bn.append(eng[i-1])
			bn.append(eng[i])
		return bn+[eng[-1]]
	def map_energy(self,indx):
		if type(indx) in [int,float,np.float64]:
			return self.engcal[0]*indx+self.engcal[1]
		return [self.engcal[0]*i+self.engcal[1] for i in indx]
	def map_index(self,energy):
		if type(energy) in [int,float,np.float64]:
			return int(round((energy-self.engcal[1])/self.engcal[0]))
		return [int(round((e-self.engcal[1])/self.engcal[0])) for e in energy]
	def map_efficiency(self,energy):
		if type(energy) in [int,float,np.float64]:
			return np.exp(self.effcal[0]*np.log(energy)**2+self.effcal[1]*np.log(energy)+self.effcal[2])
		return [np.exp(self.effcal[0]*np.log(e)**2+self.effcal[1]*np.log(e)+self.effcal[2]) for e in energy]
	def map_unc_efficiency(self,energy):
		if 'unc_eff' in self.meta:
			u = self.meta['unc_eff']
			if type(energy) in [int,float,np.float64]:
				return np.sqrt(np.log(energy)**4*u[0][0]+2.0*np.log(energy)**3*u[0][1]+2.0*np.log(energy)**2*u[0][2]+np.log(energy)**2*u[1][1]+2.0*np.log(energy)*u[1][2]+u[2][2])*self.map_efficiency(energy)
			return [np.sqrt(np.log(energy[n])**4*u[0][0]+2.0*np.log(energy[n])**3*u[0][1]+2.0*np.log(energy[n])**2*u[0][2]+np.log(energy[n])**2*u[1][1]+2.0*np.log(energy[n])*u[1][2]+u[2][2])*e for n,e in enumerate(self.map_efficiency(energy))]
		else:
			if type(energy) in [int,float,np.float64]:
				return 0.05*self.map_efficiency(energy)
			return [0.05*i for i in self.map_efficiency(energy)]
	def map_resolution(self,indx):
		if type(indx) in [int,float,np.float64]:
			return self.rescal*np.sqrt(indx)
		return list(self.rescal*np.sqrt(indx))
	def map_efficiency_correction(self,energy):
		DT = self.dead_time_efficiency()
		SA = self.solid_angle_efficiency(self.meta['R_src'],self.meta['R_det'],self.meta['dist']) if 'R_src' in self.meta and 'R_det' in self.meta and 'dist' in self.meta else 1.0
		if type(energy) in [int,float,np.float64]:
			AT = self.self_attenuation_efficiency(energy,self.meta['Z'],self.meta['thickness']) if 'Z' in self.meta and 'thickness' in self.meta else 1.0
			return DT*AT*SA
		AT = [self.self_attenuation_efficiency(e,self.meta['Z'],self.meta['thickness']) for e in energy] if 'Z' in self.meta and 'thickness' in self.meta else np.ones(len(energy)).tolist()
		return [DT*a*SA for a in AT]
	def dead_time_efficiency(self):
		return self.live_time/self.real_time
	def self_attenuation_efficiency(self,energy,Z,thickness):
		return 1.0
	def solid_angle_efficiency(self,R_src,R_det,dist):
		if R_src/R_det<0.1:
			return 1.0
		N,x,y = 50.0,R_src**2+R_det**2+dist**2/(2.0*R_src*R_det),dist**2/(2.0*R_src*R_det)
		sa_disk = (R_det/R_src)*(1.0/N)*sum([np.sin(np.pi*(n+0.5)/N)**2/(np.sqrt(x-np.cos(np.pi*(n+0.5)/N))*(np.sqrt(y)+np.sqrt(x-np.cos(np.pi*(n+0.5)/N)))) for n in range(int(N))])
		# sa_point = 1.0-1.0/np.sqrt(1.0+R_det**2/dist**2)
		R_point = 1.0
		N,x,y = 50.0,R_point**2+R_det**2+dist**2/(2.0*R_point*R_det),dist**2/(2.0*R_point*R_det)
		sa_point = (R_det/R_point)*(1.0/N)*sum([np.sin(np.pi*(n+0.5)/N)**2/(np.sqrt(x-np.cos(np.pi*(n+0.5)/N))*(np.sqrt(y)+np.sqrt(x-np.cos(np.pi*(n+0.5)/N)))) for n in range(int(N))])
		return sa_disk/sa_point
	def __add__(self,other):
		### add another spectrum to self.spec and add live and real time
		self.spec = [i+self.spec[n] for n,i in enumerate(other.spec)]
		self.live_time,self.real_time = self.live_time+other.live_time,self.real_time+other.real_time
		return self
	def __sub__(self,other):
		### subtract another spectrum multiplied ratio of live times (for bg subtraction)
		mult = self.real_time/other.real_time
		self.spec = [max((0,int(self.spec[n]-mult*i))) for n,i in enumerate(other.spec)]
		return self
	def __mul__(self,other):
		### multiply self.spec by a float or int
		self.spec = [max((0,int(i*other))) for i in self.spec]
		return self
	def exp_smooth(self,ls,alpha=0.3):
		R,RR,b = [ls[0]],[ls[-1]],1.0-alpha
		for i,ii in zip(ls[1:],reversed(ls[:-1])):
			R.append(alpha*i+b*R[-1])
			RR.append(alpha*ii+b*RR[-1])
		return [0.5*(R[n]+r) for n,r in enumerate(reversed(RR))]
	def SNIP(self,sig=4.5,offsig=1.5,alpha1=0.75,alpha2=0.15):
		dead,vi = 0,[np.log(np.log(np.sqrt(i+1.0)+1.0)+1.0) for i in self.exp_smooth(self.spec,alpha=alpha1)]
		while self.spec[dead]==0:
			dead+=1
		a,L,off = self.rescal,len(vi),int(self.rescal*sig*len(vi)**0.5)
		for M in np.arange(0,sig,0.1):
			vi = vi[:dead+off]+[min((v,0.5*(vi[n-int(M*a*np.sqrt(n))]+vi[n+int(M*a*np.sqrt(n))]))) for v,n in zip(vi[dead+off:L-off],range(dead+off,L-off))]+vi[-1*off:]
		return [s+offsig*np.sqrt(s+1) for n,s in enumerate(self.exp_smooth([int((np.exp(np.exp(i)-1.0)-1.0)**2)-1 for i in vi],alpha=alpha2))]
	def QSNIP(self,L,H):
		self.QSNP = np.zeros(len(self.spec)).tolist()
		for n,l in enumerate(L):
			A = self.quadratic_regression(range(l-1,H[n]+1),self.SNP[l-1:H[n]+1])
			for i in range(l-1,H[n]+1):
				self.QSNP[i] = sum([a*i**n for n,a in enumerate(A)])
	def find_pks(self):
		SNP,pks = self.SNIP(2.0),[]
		clip = [int(i-SNP[n]) if int(i-SNP[n])>3.5*np.sqrt(SNP[n]) else 0 for n,i in enumerate(self.exp_smooth(self.spec))]
		for n,i in enumerate(clip[1:]):
			if i>0 and clip[n]==0:
				pks.append({'l':n+1,'h':n+1,'m':i,'mu':n+1})
			elif i>0:
				pks[-1]['h'] = n+1
				if i>pks[-1]['m']:
					pks[-1]['m'],pks[-1]['mu'] = i,n+1
		return [p['mu'] for p in pks if 0.5*(p['h']-p['l'])>self.rescal*np.sqrt(p['mu'])]
	def linear_regression(self,x,y):
		xb,yb = np.average(x),np.average(y)
		m = sum([(i-xb)*(y[n]-yb) for n,i in enumerate(x)])/sum([(i-xb)**2 for i in x])
		return m,yb-m*xb
	def quadratic_regression(self,x,y):
		M = np.array([[sum([i**(m+n) for i in x]) for m in range(3)] for n in range(3)])
		b = np.array([sum([i**m*y[n] for n,i in enumerate(x)]) for m in range(3)])
		return np.dot(np.linalg.inv(M),b).tolist()
	def auto_calibrate(self):
		guess,L,best = list(self.engcal),len(self.spec),0.0
		peak_eng = [e for itp in self.meta['istp'] for e in isotope(itp).gammas(I_lim=[0.5,None],E_lim=[50,None])['E']]
		log_peaks = [np.log(np.log(np.sqrt(max((i-self.SNP[n],0))+1.0)+1.0)+1.0) for n,i in enumerate(self.spec)]
		for itr in range(3):
			delta = (0.5*guess[0]/float(itr+1)**2,(0.5*abs(guess[1])+25.0)/float(itr+1)**2)
			mrange = np.arange(guess[0]-delta[0],guess[0]+delta[0],delta[0]/100.0)
			brange = np.arange(guess[1]-delta[1],guess[1]+delta[1],delta[1]/100.0)
			for m in mrange:
				for b in brange:
					ob = sum([log_peaks[i] for i in [int(round((e-b)/m)) for e in peak_eng] if 0<i<L])
					if ob>best:
						guess,best = [m,b],ob
		self.update_params(engcal=guess,meta={'res':self.guess_res()})
	def guess_res(self):
		guess,L = 0.05,len(self.spec)
		clip = [int(i-self.SNP[n]) if int(i-self.SNP[n])>3.5*np.sqrt(self.SNP[n]) else 0 for n,i in enumerate(self.spec)]
		gammas = [isotope(itp).gammas(I_lim=[0.5,None],E_lim=[50,0.95*(self.engcal[0]*L+self.engcal[1])]) for itp in self.meta['istp']]
		gammas = {'I':[i for gm in gammas for i in gm['I']],'E':[e for gm in gammas for e in gm['E']]}
		lines = [[int((e-self.engcal[1])/self.engcal[0]),gammas['I'][n]] for n,e in enumerate(gammas['E']) if clip[int((e-self.engcal[1])/self.engcal[0])]>0]
		peak_idx,I = [i[0] for i in lines],[i[1] for i in lines]
		for itr in range(3):
			sig = [max((int(2.5*guess*np.sqrt(i)),1)) for i in peak_idx]
			S = [np.sqrt(sum([clip[n]*(n-idx)**2 for n in range(idx-sig[m],idx+sig[m])])/float(sum(clip[idx-sig[m]:idx+sig[m]])-1)) for m,idx in enumerate(peak_idx)]
			guess = np.average([s/np.sqrt(peak_idx[n]) for n,s in enumerate(S)],weights=I)
		return guess
	def peak(self,x,A,mu,sig,R,alpha):
		r2 = 1.41421356237
		return [A*np.exp(-0.5*((i-mu)/sig)**2)+R*A*np.exp((i-mu)/(alpha*sig))*erfc((i-mu)/(r2*sig)+1.0/(r2*alpha)) if abs(i-mu)/sig<10.0 else 0.0 for i in x]
	def Npeak(self,x,*args,**kwargs):
		cal,Q = (kwargs['cal'] if 'cal' in kwargs else self.calibrate),(kwargs['Q'] if 'Q' in kwargs else True)
		if cal:
			N,I = len(args)/5,[self.peak(x,args[5*n],args[5*n+1],args[5*n+2],args[5*n+3],args[5*n+4]) for n in range(len(args)/5)]
		else:
			N,I = len(args)/3,[self.peak(x,args[3*n],args[3*n+1],args[3*n+2],self.meta['R'],self.meta['alpha']) for n in range(len(args)/3)]
		if Q:
			return [self.QSNP[int(round(i))]+sum([I[m][n] for m in range(N)]) for n,i in enumerate(x)]
		return [self.SNP[int(round(i))]+sum([I[m][n] for m in range(N)]) for n,i in enumerate(x)]
	def chi2(self,fn,x,y,b):
		if float(len(y)-len(b))<1:
			return float('Inf')
		return sum([(y[n]-i)**2/y[n] for n,i in enumerate(fn(x,*b)) if y[n]>0])/float(len(y)-len(b))
	def get_gammas(self,cutoff=4.5):
		gammas,L = {},len(self.spec)-int(5.0*self.rescal*np.sqrt(len(self.spec)))
		clip = [max((int(i-self.SNP[n]),0)) for n,i in enumerate(self.spec)]
		for istp in self.meta['istp']:
			gm = isotope(istp).gammas(E_lim=[50,None])
			pk = [(i,I,e,dI,sig,eff) for i,I,e,dI,sig,eff in zip(self.map_index(gm['E']),gm['I'],gm['E'],gm['dI'],self.map_resolution(self.map_index(gm['E'])),self.map_efficiency(gm['E'])) if i<L]
			A0 = np.exp(np.average(np.log([clip[p[0]]*p[4]/(p[5]*p[1])+1.0 for p in pk]),weights=[p[1] for p in pk]))-1.0
			pk = [p for p in pk if (A0*2.506*p[5]*p[1])/np.sqrt(sum(self.SNP[p[0]-int(3*p[4]):p[0]+int(3*p[4])+1]))>=cutoff]
			if len(pk)>0:
				gammas[istp] = [{'p0':[A0*p[5]*p[1]/p[4],float(p[0]),p[4]],'gm':[p[2],p[1],p[3],istp],'l':int(p[0]-max((6.0*p[4],4))),'h':int(p[0]+max((5.5*p[4],4)))} for p in pk]
		sp,A,itps = [],[],[]
		for istp in gammas:
			gm = gammas[istp][0]
			itps.append(istp)
			A.append(gm['p0'][0]*gm['p0'][2]/(self.map_efficiency(gm['gm'][0])*gm['gm'][1]))
			sp.append(self.Npeak(range(len(self.spec)),*[i for p in gammas[istp] for i in p['p0']],**{'Q':False,'cal':False}))
		try:
			fit,unc = curve_fit(lambda x,*dA:[self.SNP[i]+sum([sp[n][i]*a-self.SNP[i] for n,a in enumerate(dA)]) for i in x],range(len(self.spec)),self.spec,p0=np.ones(len(A)),bounds=(np.zeros(len(A)),np.inf))
		except:
			fit = np.ones(len(A))
		for n,dA in enumerate(fit):
			gammas[istp] = [{'p0':[dA*p['p0'][0],p['p0'][1],p['p0'][2]],'gm':p['gm'],'l':p['l'],'h':p['h']} for p in gammas[istp]]
		return gammas
	def plot_p0(self):
		f,ax = plt.subplots()
		ax.plot(self.E_range,self.spec,color='k')
		gammas = self.get_gammas()
		for istp in gammas:
			peak = self.Npeak(range(len(self.spec)),*[i for p in gammas[istp] for i in p['p0']],**{'Q':False,'cal':False})
			ax.plot(self.E_range,peak)
		ax.set_yscale('log')
		ax.set_ylabel('Counts')
		ax.set_xlabel('Energy [keV]')
		f.tight_layout()
		plt.show()
	def get_bounds(self,n_par,val,upper=True):
		if upper:
			return {0:2.5*val,1:1.001*val,2:1.5*val,3:0.5,4:2.5}[n_par]
		return {0:0.0,1:0.999*val,2:0.7*val,3:0.1,4:0.5}[n_par]
	def zip_peaks(self,pks):
		l,h = min([p['l'] for p in pks]),max([p['h'] for p in pks])
		pk_info,p0 = [p['gm'] for p in pks],[p for pk in pks for p in pk['p0']]
		fit = [p for pk in pks for p in pk['fit']] if 'fit' in pks[0] else []
		N,L = len(fit)/len(pk_info),len(fit)
		unc = [np.zeros(N*n).tolist()+p+np.zeros(L-N*n-N).tolist() for n,pk in enumerate(pks) for p in pk['unc']] if 'unc' in pks[0] else []
		bounds = ([self.get_bounds(n,p,False) for pk in pks for n,p in enumerate(pk['p0'])],[self.get_bounds(n,p) for pk in pks for n,p in enumerate(pk['p0'])])
		return {'l':l,'h':h,'pk_info':pk_info,'p0':p0,'bounds':bounds,'fit':fit,'unc':unc}
	def get_p0(self):
		gammas = self.get_gammas()
		peaks = sorted([p for istp in gammas for p in gammas[istp]],key=lambda h:h['l'])
		if self.calibrate:
			peaks = [{'l':p['l'],'h':p['h'],'gm':p['gm'],'p0':p['p0']+[self.meta['R'],self.meta['alpha']]} for p in peaks]
		return self.group_peaks(peaks)
	def group_peaks(self,peaks):
		groups = [[peaks[0]]]
		if len(peaks)>1:
			for p in peaks[1:]:
				if p['l']<groups[-1][-1]['h']:
					groups[-1].append(p)
				else:
					groups.append([p])
		self.QSNIP([min([p['l'] for p in p0]) for p0 in groups],[max([p['h'] for p in p0]) for p0 in groups])
		return map(self.zip_peaks,groups)
	def filter_peaks(self,pks,cutoff=2.5):
		peaks = []
		for pk in pks:
			N = len(pk['p0'])/len(pk['pk_info'])
			for m in range(len(pk['pk_info'])):
				if len(pk['pk_info'])==1:
					x,y = range(pk['l'],pk['h']),self.spec[pk['l']:pk['h']]
				else:
					p0 = [i for n,i in enumerate(pk['fit']) if int(n/N)!=m]
					x = range(int(pk['fit'][N*m+1]-6.0*pk['fit'][N*m+2]),int(pk['fit'][N*m+1]+5.5*pk['fit'][N*m+2]))
					offs = self.Npeak(x,*p0)
					y = [i-offs[n]+self.SNP[n+x[0]] for n,i in enumerate(self.spec[x[0]:x[-1]+1])]
				if N==3:
					chi2 = self.chi2(self.Npeak,x,y,[i for n,i in enumerate(pk['fit']) if int(n/N)==m])
					N_cts = int(pk['fit'][N*m]*(2.506*pk['fit'][N*m+2]+2*self.meta['R']*self.meta['alpha']*pk['fit'][N*m+2]*np.exp(-0.5/self.meta['alpha']**2)))
				else:
					chi2 = self.chi2(self.Npeak,x,y,[i for n,i in enumerate(pk['fit']) if int(n/N)==m])
					N_cts = int(pk['fit'][N*m]*(2.506*pk['fit'][N*m+2]+2*pk['fit'][N*m+3]*pk['fit'][N*m+4]*pk['fit'][N*m+2]*np.exp(-0.5/pk['fit'][N*m+4]**2)))
				sig = pk['fit'][N*m]/max((np.sqrt(self.SNP[int(round(pk['fit'][N*m+1]))]),5.0))
				unc_N = (min((np.sqrt(abs(pk['unc'][N*m][N*m])*(N_cts/pk['fit'][N*m])**2+abs(pk['unc'][N*m+2][N*m+2])*(N_cts/pk['fit'][N*m+2])**2),1e18))) if not np.isinf(pk['unc'][N*m][N*m]) else np.sqrt(N_cts)
				if sig>cutoff and chi2*cutoff<N_cts:
					peaks.append({'l':x[0],'h':x[-1],'gm':pk['pk_info'][m]+[N_cts,unc_N,chi2],'p0':pk['p0'][N*m:N*m+N],'fit':pk['fit'][N*m:N*m+N],'unc':[u.tolist()[N*m:N*m+N] for u in pk['unc'][N*m:N*m+N]]})
		self.peak_fits = self.group_peaks(peaks)
		return self.peak_fits
	def fit_peaks(self,calibrate=False):
		if self.peak_fits is not None:
			return self.peak_fits
		self.calibrate = calibrate
		p0 = self.get_p0()
		fits = []
		for p in p0:
			try:
				p['fit'],p['unc'] = curve_fit(self.Npeak,range(p['l'],p['h']),self.spec[p['l']:p['h']],p0=p['p0'],bounds=p['bounds'],sigma=np.sqrt(self.SNP[p['l']:p['h']]))
				fits.append(p)
			except Exception, err:
				print 'Error on peak:',p['pk_info']
				print Exception, err
		return self.filter_peaks(fits)
	def plot_spectrum(self,logscale=True,wfit=False,bg=False,calibrate=False,subpeak=False,printout=False,saveas=None):
		f,ax = plt.subplots(figsize=(16,4.5))
		ax.plot(self.get_plot_energy(),self.get_plot_spec(logscale),lw=1.2,color=self.clr['k'],zorder=1,label=(self.meta['name'] if 'name' in self.meta else self.filename))
		if wfit:
			for n,pk in enumerate(self.fit_peaks(calibrate)):
				if printout:
					print pk['pk_info']
				ax.plot([self.engcal[0]*i+self.engcal[1] for i in np.arange(pk['l'],pk['h'],0.1)],self.Npeak(np.arange(pk['l'],pk['h'],0.1),*pk['fit']),lw=1.8,color=self.clr['r'],zorder=10,label=('Peak Fit'+('s' if len(self.peak_fits)>1 else '') if n==0 else None))
				if subpeak:
					N,M = len(pk['fit'])/(5 if calibrate else 3),(5 if calibrate else 3)
					if N>1:
						for m in range(N):
							ax.plot([self.engcal[0]*i+self.engcal[1] for i in np.arange(pk['l'],pk['h'],0.1)],self.Npeak(np.arange(pk['l'],pk['h'],0.1),*pk['fit'][m*M:m*M+M]),lw=1.2,ls='--',color=self.clr['r'],zorder=5)
		if bg:
			ax.plot(self.get_energy(),self.SNP,lw=1.2,color=self.clr['b'],zorder=3)
		if logscale:
			ax.set_yscale('log')
		ax.set_ylim((max((0.9,ax.get_ylim()[0])),ax.get_ylim()[1]))
		ax.set_xlim((self.E_range[0],self.E_range[-1]))
		ax.set_xlabel('Energy (keV)')
		ax.set_ylabel('Counts')
		ax.legend(loc=0)
		f.tight_layout()
		if saveas is None:
			plt.show()
		else:
			f.savefig(saveas)
			plt.close()
