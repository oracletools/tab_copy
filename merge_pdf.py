#!/usr/bin/python2.4
#
# Copyright 2014 Citi.  All Rights Reserved.
# 
# Original author Alex.Buzunov@citi.com (Alex Buzunov)

"""PDF file merger
"""

__author__ = 'Alex.Buzunov@citi.com (Alex Buzunov)'

from PyPDF2 import PdfFileMerger, PdfFileReader
import os, sys
#cd C:\tmp\Python27.2.5\_TabZilla_5
#..\\python merge_pdf.py --list=test.txt --outfile=test.pdf
import logging as log
log.basicConfig(filename='merger.log', filemode='w', level=log.DEBUG)
FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
log.basicConfig(format=FORMAT)
d = {'clientip': '192.168.0.1', 'user': 'fbloggs'}
logger = log.getLogger('pdfmerger')
logger.warning('Protocol problem: %s', 'connection reset', extra=d)


from optparse import OptionParser

parser = OptionParser()
parser.add_option("-i", "--list", dest="in_list",default=True,help="file with list of PDF files")
parser.add_option("-o", "--outfile", dest="out_file", default='merged.pdf', help="merged PDF file")

(options, args) = parser.parse_args()
in_list = options.in_list
out_file = options.out_file
print in_list, out_file
merger = PdfFileMerger()
infiles=()
with open(in_list) as f:
	infiles = f.readlines()
	print infiles
for filename in infiles:
	filename=filename.strip()
	assert os.path.isfile(filename), 'File %s does not exists.' % filename	
	merger.append(PdfFileReader(file(filename, 'rb')))

merger.write(out_file)
print out_file, 'created'