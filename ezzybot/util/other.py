class toClass(object):
	def __init__(self, d):
		for k in d.keys():
			exec "self.{} = d['{}']".format(k,k)
