import re
import subprocess

class Scanner(object) :
	def __init__(self) :
		pass

class ARPScanner(Scanner) :
	ARPSCAN_MATCHER = re.compile('^([0-9a-fA-F:\.]+)\t([0-9a-fA-F:\.]+)\t(.*)$')
	ARPSCAN_CMD = 'arp-scan'

	def __init__(self, interface) :
		self.interface = interface
		super(ARPScanner, self).__init__()

	def scan(self) :
		cmd = ['arp-scan', '-R', '--interface', self.interface, '--localnet']
		p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		o, trash = p.communicate()
		for l in o.split('\n') :
			m = self.ARPSCAN_MATCHER.match(l)
			if m :
				ip, mac, name = m.groups()
				yield {
					'ip' : ip,
					'mac' : mac,
					'name' : name
				}
