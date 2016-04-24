class toClass(object):

	def __init__(self, d):
		for k in d.keys():
			exec("self.{0} = d['{1}']".format(k,k))
