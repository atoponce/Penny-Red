#!/usr/bin/env python

import rfc822
import StringIO
import subprocess
import sys

# Change the DB path in COMMAND as needed, and change your email address(es)
COMMAND="hashcash -cdb '%s' -r '%s' -f ~/.mutt/hashcash.db '%s'"
EMAILADDR=("foo@example.com", "bar@example.com")

tokens = []
token_status = []

# converting a list to a file-type object for parsing rfc822 headers
original = sys.stdin.read()
emailmsg = StringIO.StringIO(''.join(original))
message = rfc822.Message(emailmsg)

# check for the presence of "X-Hashcash" and "Hashcash" headers
# and extract only matches from EMAILADDR
if message.has_key("X-Hashcash"):
    for hc_list in message.getheaders("X-Hashcash"):
        if hc_list.split(":")[3] in EMAILADDR:
            tokens.append(hc_list)
if message.has_key("Hashcash"):
    for hc_list in message.getheaders("Hashcash"):
        if hc_list.split(":")[3] in EMAILADDR:
            tokens.append(hc_list)

# check each token
if tokens:
    token_status.append("[-- Begin Hashcash output --]")
    for token in tokens:
        bits = token.split(":")[1]
        emailaddr = token.split(":")[3]
        p = subprocess.Popen(COMMAND % (bits, emailaddr, token),
            shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        out = p.stderr.read().strip()
        token_status.append(out)
    token_status.append("[-- End Hashcash output --]")

print >> sys.stdout, ''.join(message.headers)
for status in token_status:
    print >> sys.stdout, ''.join(status)
if tokens:
    print ''
emailmsg.seek(message.startofbody)
print >> sys.stdout, ''.join(emailmsg.readlines())
