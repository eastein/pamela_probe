import unittest

import sync_logic as sl

class TestSubscriber(object) :
	def test_empty(self) :
		ts = TestSubscriber()
		nv = sl.NetworkView()
		nv.add_subscriber(ts)
