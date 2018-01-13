#!/usr/bin/python
import lutin.debug as debug
import lutin.tools as tools
import os

def get_type():
	return "LIBRARY"

def get_desc():
	return "bzip2:bz2 library"

#def get_licence():
#	return "UNKNOW"

def get_compagny_type():
	return "org"

def get_compagny_name():
	return "bzip2"

#def get_maintainer():
#	return "UNKNOW"

def get_version():
	return "version.txt"

def configure(target, my_module):
	my_module.add_src_file([
	    'bzip2/blocksort.c',
	    'bzip2/huffman.c',
	    'bzip2/crctable.c',
	    'bzip2/randtable.c',
	    'bzip2/compress.c',
	    'bzip2/decompress.c',
	    'bzip2/bzlib.c',
	    ])
	
	
	my_module.add_header_file([
	    'bzip2/bzlib.h'
	    ])
	
	my_module.compile_version('c++', 2011)
	my_module.add_depend([
	    'z',
	    'm',
	    ])
	return True


