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
import logging 
logging.basicConfig(filename='pdfmerger.log', filemode='w', level=logging.DEBUG,format='%(asctime)s | %(name)s | %(levelname)s | %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
#logging.basicConfig()
#FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
#logging.basicConfig(format=FORMAT)
#d = {'clientip': '192.168.0.1', 'user': 'fbloggs'}
log = logging.getLogger('pdfmerger')
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
log.addHandler(ch)


from optparse import OptionParser

parser = OptionParser()
parser.add_option("-i", "--list", dest="in_list",default=True,help="file with list of PDF files")
parser.add_option("-o", "--outfile", dest="out_file", default='merged.pdf', help="merged PDF file")

(options, args) = parser.parse_args()
in_list = options.in_list
log.info('file list: %s', in_list)
out_file = options.out_file
log.info('out file: %s', out_file)
#print in_list, out_file
merger = PdfFileMerger()
infiles=()
with open(in_list) as f:
	infiles = f.readlines()
	print infiles
for filename in infiles:
	filename=filename.strip()
	if not  os.path.isfile(filename):
		log.error('File %s does not exists.', filename)	
	else:
		log.info('Processing file %s.', filename)	

	merger.append(PdfFileReader(file(filename, 'rb')))

merger.write(out_file)
log.info('%s created', out_file)





