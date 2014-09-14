class NetworkView(object) :
	"""
	
	"""
	
	def __init__(self) :
		self.subscribers = list()

	def add_subscriber(self, s) :
		self.subscribers.append(s)

	def process_message(self.mobj) :
		"""
		Process an inbound message, update any state that need be updated, and emit events to subscribers.		
		"""

		pass
