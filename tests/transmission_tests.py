import unittest

import sync_logic as sl

class EventTests(unittest.TestCase) :
	def test_istype(self) :
		e = sl.Add(112598175, set())
		#self.assertTrue(e.istype(sl.Add))
		#self.assertFalse(e.istype(sl.Remove))

class TestSubscriber(object) :
	def __init__(self) :
		self.events = list()

	def recv_event(self, e) :
		self.events.append(e)

INITIAL_SNAP = {
	'serial' : 1,
	'parts' : [
		{
			'type' : 'snapshot',
			'nodes' : [['a','a','a'],[ 'b', 'b', 'b']]
		}
	]
}	

ADD_MSG = {
	'serial' : 2,
	'prev_serial' : 1,
	'parts' : [
		{
			'type' : 'add',
			'nodes' : [['c','c','c']]
		}
	]
}

REMOVE_MSG = {
	'serial' : 3,
	'prev_serial' : 2,
	'parts' : [
		{
			'type' : 'remove',
			'nodes' : [['b', 'b', 'b']]
		}
	]
}

NOP_MSG = {
	'serial' : 2,
	'prev_serial' : 1,
	'parts' : [
		{
			'type' : 'no-op',
		}
	]
}

class TestSubscription(unittest.TestCase) :
	def setup(self) :
		ts = TestSubscriber()
		nv = sl.NetworkView()
		nv.add_subscriber(ts)
		return ts, nv

	def test_empty(self) :
		ts, nv = self.setup()
		self.assertEquals(0, len(ts.events))

	def test_snap_sync(self) :
		ts, nv = self.setup()

		nv.handle_message(INITIAL_SNAP)
		snap_e = ts.events[0]
		self.assertTrue(snap_e.istype(sl.Snapshot))
		self.assertEquals(snap_e.serial, 1)
		self.assertEquals(snap_e.nodes, set([('a','a','a'), ('b','b','b')]))
		sync_e = ts.events[1]
		self.assertTrue(sync_e.istype(sl.Sync))
		self.assertEquals(sync_e.serial, 1)
		self.assertEquals(sync_e.nodes, None)
		self.assertEquals(len(ts.events), 2)

	def test_add_remove(self) :
		ts,nv = self.setup()
		
		nv.handle_message(INITIAL_SNAP)
		self.assertEquals(len(ts.events), 2)

		nv.handle_message(ADD_MSG)
		self.assertEquals(len(ts.events), 3)
		addm = ts.events[2]
		self.assertTrue(addm.istype(sl.Add))
		self.assertEquals(addm.nodes, set([('c','c','c')]))

		self.assertEquals(set([('a','a','a'), ('b','b','b'),('c','c','c')]), nv.net)
		nv.handle_message(REMOVE_MSG)
		self.assertEquals(len(ts.events), 4)
		rem = ts.events[3]
		self.assertTrue(rem.istype(sl.Remove))

		self.assertEquals(set([('a','a','a'), ('c','c','c')]), nv.net)


	def test_nop(self) :
		ts,nv = self.setup()

		nv.handle_message(INITIAL_SNAP)
		self.assertEquals(len(ts.events), 2)
		self.assertEquals(nv.serial, 1)
		
		nv.handle_message(NOP_MSG)
		self.assertEquals(len(ts.events), 2)
		self.assertEquals(nv.serial, 2)
