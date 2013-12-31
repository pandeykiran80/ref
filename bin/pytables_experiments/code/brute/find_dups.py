from __future__ import print_function #python 3
import tables as tb
import cProfile
import time
import numpy as np


class Timer:    
    def __enter__(self):
        self.start = time.clock()
        return self

    def __exit__(self, *args):
        self.end = time.clock()
        self.interval = self.end - self.start

def dups1(th):
	#~ with Timer() as t:
		for row in th:
			id = row['id']
			counts = row['counts']
			query = '(id == %d) & (counts == %d)' %(id, counts)
			result = th.readWhere(query)
			if len(result) > 1:
				#~ print(row['id'], row['counts'])
				pass
	#~ print('''
	#~ brute force method
	#~ with row looksups
	#~ rectangular search
	#~ nrows=%d
	#~ time = %.3fs
	#~ ''') %(th.nrows, t.interval)
		
		
def dups2(th):
	with Timer() as t:
		for row in th:
			id = row['id']
			counts = row['counts']
			query = '(id == %d) & (counts == %d)' %(id, counts)
			result = th.readWhere(query, start=row.nrow, stop=th.nrows)
			if len(result) > 1:
				print(row['id'])
	print('''
	brute force method
	triangular search
	row lookups
	nrows=%d
	time = %.3fs	
	
	''') %(th.nrows, t.interval)


def dups3(th):
	with Timer() as t:
		for row in th:
			result = th.readWhere('(id == cid) & (counts == ccounts)', {'cid': row['id'], 'ccounts': row['counts']})
			if len(result) > 1:
				print(row['id'])
	print('''
	brute force method
	rectangular search
	with condvals
	nrows=%d
	time = %.3fs	
	
	''')%(th.nrows, t.interval)
			
def dups4(th):
	with Timer() as t:
		for row in th:
			result = th.readWhere('(id == cid) & (counts == ccounts)', {'cid': row['id'], 'ccounts': row['counts']}, start=row.nrow, stop=th.nrows)
			if len(result) > 1:
				print(row['id'])
	print('''
	brute force method
	triangular search
	with condvals
	nrows=%d
	time = %.3fs
	
	''')%(th.nrows, t.interval)

			
def dups5(th):
	''' 
	iterator only
	'''
	iters = []
	with Timer() as t:
		for row in th:
			result = th.where('(id == cid) & (counts == ccounts)', {'cid': row['id'], 'ccounts': row['counts']})
	print( '''
	brute force method
	iterator only
	with condvals
	nrows=%d
	time = %.3fs	
	
	''')%(th.nrows, t.interval)

def dups6(th):
	'''
	bloom filter
	'''

	ex = tb.Expr('(x * 65536) + y', uservars = {"x": th.cols.id, "y":  th.cols.counts})
	ex.setOutput(th.cols.hash)
	ex.eval()
	th.cols.hash.remove_index()
	th.cols.hash.create_csindex(filters=filters)
	ref = None
	dups = []
	for row in th.itersorted(sortby=th.cols.hash):
		if row['hash'] == ref:
			dups.append(row['hash'] )
		ref = row['hash']

	print("ids: ", np.right_shift(np.array(dups, dtype=np.int64), 16))
	print("counts: ", np.array(dups, dtype=np.int64) & 65536-1)
		
	#~ print('''
	#~ hash calculation
	#~ nrows=%d
	#~ time = %.3fs	
	
	#~ ''' %(th.nrows, t.interval))
	
def dups7(th):
	'''
	sorted
	'''
	
	with Timer() as t:
		id = None
		z = th.itersorted(sortby=th.cols.id)
		for row in z:
			id_tmp = row['id']
			if id_tmp == id:
				print(id)
			id = id_tmp

			
			#~ if row['id'] == id:
				#~ bucket.append(row['counts'])
			#~ else:
				#~ if len(bucket) >1:
					#~ bucket = np.sort(bucket)
					#~ dups = bucket[bucket[:-1] == bucket[1:]]
					#~ if dups:
						#~ pass
						#~ print(id, dups)
				#~ id = row['id']
				#~ bucket = []
			
			
		#~ for row in z:
			#~ result = th.readWhere('(id == cid) & (counts == ccounts)', {'cid': row['id'], 'ccounts': row['counts']}, start=row.nrow, stop=row.nrow+1)
			#~ if len(result) > 1:
				#~ print(row['id'])
	#~ print('''
	#~ sort method
	#~ adjacent search
	#~ with condvals
	#~ nrows=%d
	#~ time = %.3fs
	
	#~ ''')%(th.nrows, t.interval)
	

def dups8(th):
	'''
	sorted
	'''
	z = th.itersorted(th.cols.id)
	with Timer() as t:
		id = None
		counts = None
		for row in z:
			if (row['id'] == id) & (row['counts'] == counts) :
				print(row['id'], row['counts'])
			id = row['id']
			counts = row['counts']
				
	print('''
	sort method
	simple adjacent search
	nrows=%d
	time = %.3fs
	
	''')%(th.nrows, t.interval)		
	
def dups9(th):
	''' 
	iterator only
	'''
	iters = []
	with Timer() as t:
		for row in th:
			iters.append(th.get_where_list('(id == cid) & (counts == ccounts)', {'cid': row['id'], 'ccounts': row['counts']}))
		for i in iters:
			if len(i) > 1:
				print(th[i[1]]['id'])
			
		
	print('''
	brute force method
	iterator only
	with condvals
	nrows=%d
	time = %.3fs	
	
	''')%(th.nrows, t.interval)	


if __name__ == '__main__':
	#~ print th.willQueryUseIndexing(condition, condvars=None)
	for n in range(4, 13, 1):
		nrows = int(10**n)
		print("1e%d rows" %n)
		db = tb.openFile('db.h5', mode = "w", title='test')
		node = db.createGroup("/", 'line', 'Node')
		mytype = np.dtype([('id', np.int64),('counts', np.int64), ('hash', np.int64)])
		filters = tb.Filters(complib='blosc', complevel=1)
		th = db.createTable(node, 'TH', mytype, "Headers", expectedrows=nrows, filters=filters)
		data = np.random.randint(1, 2**16, (nrows, 3)).astype(np.int64)
		th.append(data)
		indexrows = th.cols.id.create_csindex(filters=filters)
		indexrows = th.cols.counts.create_csindex(filters=filters)	
		
		#~ dups1(th)
		#~ dups2(th)
		#~ dups3(th)
		#~ dups4(th)
		#~ dups5(th)
		#~ dups6(th)
		#~ dups7(th)
		#~ dups8(th)
		#~ dups9(th)
		import timeit
		#~ print(np.amin(timeit.repeat("dups6(th)", setup="from __main__ import dups6, th", number=1, repeat=1)))
		print(np.amin(timeit.repeat("dups7(th)", setup="from __main__ import dups7, th", number=1, repeat=1)))
		db.close()


	