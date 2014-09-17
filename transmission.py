import threading
from zmqfan import zmqsub
import time, pprint


SCANTIME_BUFFER = 100
TARGET_LATENCY = 10.0 # how "behind" any given result will be
SYNC_TARGET = 30.0 # the amount of time a client can reasonably expect to achieve a full picture in

# TODO use the scantimes, scantime_buffer options

class NetworkStatus(object) :
	def __init__(self, p, jzp, scantime_buffer=SCANTIME_BUFFER, target_latency=TARGET_LATENCY, sync_target=SYNC_TARGET) :
		"""
		@param p a probe object that will emit results upon calling .scan
		@param jzp a json zmq publisher from zmqfan
		"""
		# object relationships		
		self.p = p
		self.jzp = jzp

		# settings
		self.target_latency = target_latency
		self.scantime_buffer = scantime_buffer
		self.sync_target = sync_target

		# state
		self.serial = None
		self.previous_serial = None
		self.scantimes = []
		self.net = set()
		
		# loop state
		self.seq = 0
		self.ok = True
		self.transmitted_snapshot = False

	# derived setting
	@property
	def snapshot_period(self) :
		return int(self.sync_target / self.target_latency)

	def seqmode(self) :
		"""
		Returns true if this sequence run, an entire network snapshot should be sent out.
		"""
		self.seq += 1
		if self.seq >= self.snapshot_period :
			self.seq = 0
			return True
		else :
			return False

	def genserial(self, tsf=None) :
		if tsf is None :
			tsf = time.time()

		return long(tsf * 1000)

	def step(self, verbose=False) :
		seq_mode = self.seqmode()

		added = set()
		present = set()
		for tup in self.p.scan() :
			if tup in self.net :
				# nodes still here..
				present.add(tup)
			else :
				# an addition!
				added.add(tup)
		removed = self.net.difference(present)

		def create_message_part(msg_type, nodes=None) :
			obj = {
				'type' : msg_type,
			}
			if nodes is not None :
				nl = list(nodes)
				nl.sort()
				obj['nodes'] = nl
			return obj

		def send_message(message_parts_list) :
			message_object = {
				'serial' : self.serial,
				'parts' : message_parts_list
			}
			if self.previous_serial is not None :
				message_object['prev_serial'] = self.previous_serial
			
			if verbose :
				pprint.pprint(message_object)
			if self.jzp :
				self.jzp.send(message_object)

		self.previous_serial = self.serial
		self.serial = self.genserial()

		message_parts = list()

		if removed :
			# until a snapshot has been transmitted, removes are not usable; there is nothing to remove from
			if self.transmitted_snapshot :
				message_parts.append(create_message_part('remove', removed))
			self.net = present
		if added :
			# until a snapshot has been transmitted, add is not usable, and we also don't know that its presence is fresh
			if self.transmitted_snapshot :
				message_parts.append(create_message_part('add', added))
			self.net = self.net.union(added)

		if seq_mode :
			message_parts.append(create_message_part('snapshot', self.net))
			self.transmitted_snapshot = True

		if not message_parts :
			message_parts.append(create_message_part('no-op'))

		send_message(message_parts)

	def loop(self, verbose=False) :
		while self.ok :
			ts = time.time()
			self.step(verbose=verbose)
			rem = self.target_latency - max(0, time.time() - ts)
			if rem > 0.0 :
				time.sleep(rem)


class ConsumerThread(threading.Thread) :
	def __init__(self, s, nv) :
		self.s = s
		self.nv = nv
		self.ok = True
		threading.Thread.__init__(self)

	def run(self) :
		while self.ok :
			try :
				msg = self.s.recv(timeout=1.0)
				self.nv.handle_message(msg)
			except zmqsub.NoMessagesException :
				pass

	def stop(self) :
		self.ok = False
