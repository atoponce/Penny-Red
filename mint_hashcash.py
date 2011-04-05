#!/usr/bin/env python

import csv
import fileinput
import rfc822
import subprocess
import sys

subprocess.call("vim %s" % sys.argv[1], shell=True)

file = open(sys.argv[1], 'r')
headers = rfc822.Message(file)

to_emails = headers.getaddrlist("To")
cc_emails = headers.getaddrlist("Cc")

email_addrs = []
tokens = []

# Harvest all email addresses from the header
for email in to_emails:
    email_addrs.append(email[1])

for email in cc_emails:
    email_addrs.append(email[1])

# Remove duplicate emails from the list, requires Python 2.5 and later
email_addrs = list(set(email_addrs))

# Check if an appropriate token is already generated for the mail
if headers.has_key("X-Hashcash"):
    for list in headers.getheaders("X-Hashcash"):
        email_addrs.remove(list.split(":")[3])
if headers.has_key("Hashcash"):
    for list in headers.getheaders("Hashcash"):
        email_addrs.remove(list.split(":")[3])

# Call the hashcash function from the operating system to mint tokens
if email_addrs:
    for email in email_addrs:
        t = subprocess.Popen("hashcash -m %s -X -Z 2" % email, shell=True, stdout=subprocess.PIPE)
        tokens.append(t.stdout.read())

# Write the newly minted tokens to the header
f = fileinput.FileInput(sys.argv[1], inplace=1)
for line in f:
    line = line.rstrip()
    if f.lineno() == 1:
        for token in tokens:
            print token,
        print line
        continue
    else:
        print line

file.close()
