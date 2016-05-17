class toClass(object):
	'''Takes a dictionary and converts it's keys to attributes of the class'''
	def __init__(self, d):
		for k in d.keys():
			exec("self.{0} = d['{0}']".format(k))