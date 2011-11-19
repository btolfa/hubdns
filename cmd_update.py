#!/usr/bin/python
# 
# Copyright (c) 2011 Alon Swartz <alon@turnkeylinux.org>
# 
# This file is part of HubDNS
# 
# HubDNS is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your
# option) any later version.
#
"""
Update FQDN with IP address of client

Options:

    -q --quiet                Be less verbose

"""

import sys
import getopt

from hubdns import HubDNS
from utils import HubAPIError
from registry import registry
from miniupnpc import UPnP

def fatal(e):
    print >> sys.stderr, "error: " + str(e)
    sys.exit(1)

def usage(e=None):
    if e:
        print >> sys.stderr, "error: " + str(e)

    print >> sys.stderr, "Syntax: %s" % sys.argv[0]
    print >> sys.stderr, __doc__.strip()
    sys.exit(1)

def upnp():
    u = UPnP()
    u.discoverdelay = 2000
    if u.discover():
        u.selectigd()
        eport = 81
         
        r = u.getspecificportmapping(eport, 'TCP')
        while r != None and eport < 65536:
            eport = eport + 1
	    r = u.getspecificportmapping(eport, 'TCP')
        
	u.addportmapping(eport, 'TCP', u.lanaddr, 80,
	                'HubDNS port forwarding', '')
        

def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "hq", ["help", "quiet"])
    except getopt.GetoptError, e:
        usage(e)

    verbose = True
    for opt, val in opts:
        if opt in ('-h', '--help'):
            usage()

        if opt in ('-q', '--quiet'):
            verbose = False

    if args:
        usage()

    if not registry.sub_apikey and registry.fqdn:
        fatal("not initialized")

    try:
        hubdns = HubDNS(subkey=registry.sub_apikey)
        ipaddress = hubdns.update(registry.fqdn)
	upnp()
    except HubAPIError, e:
        fatal(e.description)

    if verbose:
        print "Updated %s with %s" % (registry.fqdn, ipaddress)

if __name__=="__main__":
    main()
