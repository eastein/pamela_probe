import threading

class Flags(object) :
	"""
	Flag constants namespace
	"""

	"""
	Emit a sync event at the end of processing every message that brings the NetworkView into full sync.
	"""
	ALL_SYNCS = 1

	"""
	Emit all snapshot events, no matter the synchronization state. By default, only the initial sync snapshot is emitted,
	and all future snapshots that are used to re-establish sync are synthesized into a synthetic pair of add/remove events as needed.
	"""
	ALL_SNAPSHOTS = 2

class Event(object) :
	def __init__(self, serial, nodes) :
		self.serial = serial
		self.nodes = nodes

	def istype(self, cls) :
		return self.__class__ == cls

class Sync(Event) :
	pass

class Desync(Event) :
	pass

class Snapshot(Event) :
	pass

class Add(Event) :
	pass

class Remove(Event) :
	pass

class NetworkView(object) :
	"""
	Accepts incoming messages transmitted by transmitter.py

	Goals:
	Create a gapless (fill any gaps with synthesized events) stream of update events
	Event types:
		sync
		add
		remove
		desync

	So far, flags are not used.
	"""
	
	def __init__(self, flags=0) :
		self.subscribers = list()
		self.flags = flags
		
		# the serial that self.net is as-of.
		self.serial = None
		self.synced = False
		self.net = None
		
	def add_subscriber(self, s) :
		self.subscribers.append(s)

	def pass_event(self, e) :
		for s in self.subscribers :
			s.recv_event(e)

	def process_nodes(self, p) :
		nll = p.get('nodes')
		if nll is None :
			return nll
		return set([tuple(n) for n in nll])

	def handle_message(self, mobj) :
		"""
		Process an inbound message, update any state that need be updated, and emit events to subscribers.		
		"""

		# TODO handle errors from invalid input. Somehow.

		m_ser = mobj['serial']
		m_prev_ser = mobj.get('prev_serial')
		parts = [{
			'type': p['type'],
			'nodes': self.process_nodes(p)
			} for p in mobj['parts']]
		n_parts = len(parts)
		last_part = parts[-1]

		if not self.synced :
			# desynced case
			if last_part['type'] != 'snapshot' :
				# if we want to emit multiple desyncs, we should do one now...
				return

			if self.net is None :
				# first case; never had a sync yet.
				self.serial = m_ser
				self.synced = True
				self.net = set(last_part['nodes'])
				self.pass_event(Snapshot(self.serial, set(self.net)))
				self.pass_event(Sync(self.serial, None))
			else :
				# we were synced once, but aren't right now. whoops!
				pass
				raise RuntimeError("woops, need to implement gap correction!")
		else :
			# we are, for now, synchronized. check out this incoming message...
			if (not m_prev_ser) or (m_prev_ser != self.serial) :
				# here's the case where the previous serial doesn't match the one we have... whoops.
				self.synced = False
				self.pass_event(Desync(self.serial, None))
				return

			self.serial = m_ser
			# handle no-op, add, remove.

			for part in parts :
				if part['type'] == 'add' :
					nodeset = set(part['nodes'])
					self.net = self.net.union(nodeset)
					self.pass_event(Add(self.serial, nodeset))
				elif part['type'] == 'remove' : 
					nodeset = set(part['nodes'])
					self.net = self.net.difference(nodeset)
					self.pass_event(Remove(self.serial, nodeset))
			
			if (self.flags & Flags.ALL_SYNCS) : 
				self.pass_event(Sync(self.serial, None))

