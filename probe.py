import re
import subprocess
import time

class Scanner(object) :
	def __init__(self) :
		pass

class ARPScanner(Scanner) :
	ARPSCAN_MATCHER = re.compile('^([0-9a-fA-F:\.]+)\t([0-9a-fA-F:\.]+)\t(.*)$')
	ARPSCAN_CMD = 'arp-scan'

	def __init__(self, interface, timeout_ms=40) :
		self.interface = interface
		self.timeout_ms = timeout_ms
		super(ARPScanner, self).__init__()

	def scan(self) :
		#ts = time.time()
		cmd = ['arp-scan', '-g', '-r', '7', '--timeout', str(self.timeout_ms), '-R', '--interface', self.interface, '--localnet']
		p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		o, trash = p.communicate()
		for l in o.split('\n') :
			m = self.ARPSCAN_MATCHER.match(l)
			if m :
				ip, mac, name = m.groups()
				yield (mac, ip, name)

		#print '%0.3f sec runtime' % (time.time() - ts)
