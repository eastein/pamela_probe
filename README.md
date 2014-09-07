<A name="toc1-0" title="pamela_probe" />
# pamela_probe

Pamela is, for the purposes of this project, Persistent Automatic Meatspace Existence List Agent. I don't know why Heatsync labs called theirs Pamela, but that's what I think it means. So therefore, it does. Because I'm stealing the name of their software to make it do something sorta similar but not quite.

<A name="toc2-5" title="Purpose" />
## Purpose

The purpose of pamela_probe is to be a long running process that is capable of mapping the nodes on a netblock and efficiently transmitting over the network both the entire picture of the network and incremental changes thereto.

<A name="toc1-10" title="Status" />
# Status

Incomplete. Just a wrapper around arp-scan for now.

    sudo python -c "import probe; s=probe.ARPScanner('wlan0'); import pprint; pprint.pprint(list(s.scan()))"
