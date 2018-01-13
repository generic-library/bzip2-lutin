#!/usr/bin/env python
import sys
import re
import os
import copy


# DL sources:
# ...
# cd libname
# mkdir build
# cd build
# make VERBOSE=1 > ../../build.txt

# ./cmakeToLutin.py build.txt bzip2



build_output_file = sys.argv[1]
global_lib_name = sys.argv[2]

def create_directory_of_file(file):
	path = os.path.dirname(file)
	try:
		os.stat(path)
	except:
		os.makedirs(path)

def file_write_data(path, data):
	#create_directory_of_file(path)
	file = open(path, "w")
	file.write(data)
	file.close()
	return True

list_of_library_generated = []

def genrate_version(version):
	file_write_data("version.txt", version);

list_of_flags_default = {
    "c":[],
    "cpp":[],
    "S":[]
   }

def genrate_lutin_file(lib_name, list_of_files, list_of_flags):
	tmp_base = "lib" + global_lib_name + "_"
	if     len(lib_name) > len(tmp_base)\
	   and lib_name[:len(tmp_base)] == tmp_base:
		lib_name = lib_name[len(tmp_base):]
	list_of_library_generated.append(lib_name.replace("_","-"))
	# remove all unneeded element flags:
	#-I
	list_of_include = copy.deepcopy(list_of_flags_default)
	# -D
	list_of_define = copy.deepcopy(list_of_flags_default)
	# other
	list_of_other = []
	# dependency:
	list_of_dependency = []
	#print("list of flags: ")
	for type in ["c", "cpp", "S"]:
		for elem in list_of_flags[type]:
			if elem in ["-m64", "-O3", "-O2", "-O1", "-O0", "-fPIC"]:
				continue
			if elem == "-pthread":
				list_of_dependency.append("pthread")
				continue
			if elem in ["-fabi-version=0", '-I"/usr/include"']:
				# just remove it ..
				continue
			if elem[:2] == "-D":
				#print("DEFINE: " + elem)
				list_of_define[type].append(elem)
				continue
			if elem[:2] == "-I":
				if    elem == '-I"."' \
				   or elem == '-I.':
					continue
				if elem[:9] in '-I"bin.v2':
					continue
				if elem[:4] in '-I"/':
					if "/usr/include/python3.6" == elem[3:-1]:
						list_of_include[type].append(elem[3:-1]+"m")
						# TODO: depend on python lib
					else:
						list_of_include[type].append(elem[3:-1])
					continue
				# TODO : Do it better :
				
				print("INCLUDE: " + elem )
				if os.path.isdir(global_lib_name + "/" + global_lib_name + "/" +elem[3:-1]):
					list_of_include[type].append(global_lib_name + "/" + global_lib_name + "/" +elem[3:-1])
				else:
					list_of_include[type].append(global_lib_name + "/" +elem[3:-1])
				continue
			if elem[:2] in '-l':
				list_of_dependency.append(elem[2:])
				continue
			#print("???: " + elem)
			list_of_other.append(elem)
	
	out = ""
	out += "#!/usr/bin/python\n"
	out += "import lutin.debug as debug\n"
	out += "import lutin.tools as tools\n"
	out += "import os\n"
	out += "\n"
	out += "def get_type():\n"
	out += "	return \"LIBRARY\"\n"
	out += "\n"
	out += "def get_desc():\n"
	out += "	return \"" + global_lib_name + ":" + lib_name.replace("_","-") + " library\"\n"
	out += "\n"
	out += "#def get_licence():\n"
	out += "#	return \"UNKNOW\"\n"
	out += "\n"
	out += "def get_compagny_type():\n"
	out += "	return \"org\"\n"
	out += "\n"
	out += "def get_compagny_name():\n"
	out += "	return \"" + global_lib_name + "\"\n"
	out += "\n"
	out += "#def get_maintainer():\n"
	out += "#	return \"UNKNOW\"\n"
	out += "\n"
	out += "def get_version():\n"
	out += "	return \"version.txt\"\n"
	out += "\n"
	out += "def configure(target, my_module):\n"
	if len(list_of_files) != 0:
		out += "	my_module.add_src_file([\n"
		for item in list_of_files:
			out += "	    '" + global_lib_name + "/" + item +"',\n"
		out += "	    ])\n"
		out += "	\n"
	
	for type in ["c", "cpp", "S"]:
		if len(list_of_define[type]) != 0:
			if type == "cpp":
				out += "	my_module.add_flag('c++', [\n"
			elif type == "S":
				out += "	my_module.add_flag('s', [\n"
			else:
				out += "	my_module.add_flag('" + type + "', [\n"
			for item in list_of_define[type]:
				out += "	    '" + item +"',\n"
			out += "	    ])\n"
			out += "	\n"
	out += "	\n"
	if len(list_of_other) != 0:
		out += "	my_module.add_flag('c', [\n"
		for item in list_of_other:
			out += "	    '" + item +"',\n"
		out += "	    ])\n"
		out += "	\n"
	out += "	\n"
	for type in ["c", "cpp", "S"]:
		if len(list_of_include[type]) != 0:
			out += "	my_module.add_path([\n"
			for item in list_of_include[type]:
				out += "	    '" + item +"',\n"
			if type == "cpp":
				out += "	    ], type='c++')\n"
			elif type == "S":
				out += "	    ], type='s')\n"
			else:
				out += "	    ], type='" + type + "')\n"
			out += "	\n"
	
	out += "	my_module.compile_version('c++', 2011)\n"
	out += "	my_module.add_depend([\n"
	out += "	    'z',\n"
	out += "	    'm',\n"
	#out += "	    'cxx',\n"
	#out += "	    '" + global_lib_name + "-include',\n"
	for item in list_of_dependency:
		out += "	    '" + item +"',\n"
	out += "	    ])\n"
	out += "	return True\n"
	out += "\n"
	out += "\n"
	
	file_write_data("lutin_" + lib_name.replace("_","-") + ".py", out);


def generate_global_include_module():
	out = ""
	out += "#!/usr/bin/python\n"
	out += "import lutin.debug as debug\n"
	out += "import lutin.tools as tools\n"
	out += "import os\n"
	out += "\n"
	out += "def get_type():\n"
	out += "	return \"LIBRARY\"\n"
	out += "\n"
	out += "def get_desc():\n"
	out += "	return \"" + global_lib_name + " include library\"\n"
	out += "\n"
	out += "#def get_licence():\n"
	out += "#	return \"UNKNOW\"\n"
	out += "\n"
	out += "def get_compagny_type():\n"
	out += "	return \"org\"\n"
	out += "\n"
	out += "def get_compagny_name():\n"
	out += "	return \"" + global_lib_name + "\"\n"
	out += "\n"
	out += "#def get_maintainer():\n"
	out += "#	return \"UNKNOW\"\n"
	out += "\n"
	out += "def get_version():\n"
	out += "	return \"version.txt\"\n"
	out += "\n"
	out += "def configure(target, my_module):\n"
	out += "	my_module.compile_version('c++', 2011)\n"
	out += "	my_module.add_header_file(\n"
	out += "	    '" + global_lib_name + "/" + global_lib_name + "/*',\n"
	out += "	    recursive=True,\n"
	out += "	    destination_path='" + global_lib_name + "')\n"
	out += "	return True\n"
	out += "\n"
	out += "\n"
	
	file_write_data("lutin_" + global_lib_name + "-include.py", out);
	

def generate_global_module(list_of_module):
	out = ""
	out += "#!/usr/bin/python\n"
	out += "import lutin.debug as debug\n"
	out += "import lutin.tools as tools\n"
	out += "import os\n"
	out += "\n"
	out += "def get_type():\n"
	out += "	return \"LIBRARY\"\n"
	out += "\n"
	out += "def get_desc():\n"
	out += "	return \"" + global_lib_name + " include library\"\n"
	out += "\n"
	out += "#def get_licence():\n"
	out += "#	return \"UNKNOW\"\n"
	out += "\n"
	out += "def get_compagny_type():\n"
	out += "	return \"org\"\n"
	out += "\n"
	out += "def get_compagny_name():\n"
	out += "	return \"" + global_lib_name + "\"\n"
	out += "\n"
	out += "def get_version():\n"
	out += "	return \"version.txt\"\n"
	out += "\n"
	out += "def configure(target, my_module):\n"
	out += "	my_module.compile_version('c++', 2011)\n"
	out += "	my_module.add_depend([\n"
	out += "	    '" + global_lib_name + "-include',\n"
	for item in list_of_module:
		out += "	    '" + item +"',\n"
	out += "	    ])\n"
	out += "\n"
	out += "\n"
	file_write_data("lutin_" + global_lib_name + ".py", out);



with open(build_output_file) as commit:
	lines = commit.readlines()
	if len(lines) == 0:
		print("Empty build ....")
		sys.exit(1)
	list_of_file = []
	list_of_flags = copy.deepcopy(list_of_flags_default)
	# first line
	for line in lines:
		#print("line : " + line[-6:-2])
		"""
		if     len(line) > 6 \
		   and line[-6:-2] == ".cpp":
			print("element : " + line)
		"""
		
		m = re.search('^/usr/bin/(cc|clang|gcc|g\+\+|clang\+\+)(.*) -c (.*)' + global_lib_name + '/((.*)\.(cpp|c|cxx|S|s))$', line)
		if m != None:
			
			print("element : " + str(len(m.groups())))
			for elem in m.groups():
				print("     " + elem)
			
			if len(m.groups()) == 6:
				#print("element : " + line)
				## print("  value : " + m.groups()[1])
				type_of_file = m.groups()[3].split(".")[-1]
				"""
				for flag in m.groups()[3].split(" "):
					if flag in ["", "-x", "c", "assembler-with-cpp"]:
						continue
					if "assembler-with-cpp" == flag:
						print("element : " + line)
					if flag not in list_of_flags[type_of_file]:
						#print("      " + flag)
						list_of_flags[type_of_file].append(flag)
				"""
				list_of_file.append(m.groups()[3])
				continue
		#continue
		
		m = re.search('^/usr/bin/ar(.*)lib(.*)\.a(.*)$', line)
		if m != None:
			
			print("element : " + str(len(m.groups())))
			for elem in m.groups():
				print("     " + elem)
			if len(m.groups()) == 3:
				genrate_lutin_file(m.groups()[1], list_of_file, list_of_flags)
				list_of_file = []
				list_of_flags = copy.deepcopy(list_of_flags_default)
				continue
			
		
		
		"""
		
		m = re.search('^(.*)/usr/bin/ar"(.*)"((.*)/([a-zA-Z0-9_\-.]*)\.a)"(.*)$', line)
		if m != None:
			## we do not use AR element ==> in boost just a double compilation ...
			if len(m.groups()) == 6:
				#print("element : " + line)
				## print("  to: " + m.groups()[4] + " (.a)")
				# Remove it only keep the .so
				list_of_file = []
				list_of_flags = copy.deepcopy(list_of_flags_default)
				continue
		# ln -f -s 'libboost_wave.so.1.66.0' 'stage/lib/libboost_wave.so'
		"""
		
		"""
		#m = re.search('(.*/([a-zA-Z0-9_\-\.]*?)\.so)', line)
		m = re.search('^(.*)"(g\+\+|gcc|clang)"(.*)$', line)
		if m != None:
			#print("element : " + str(len(m.groups())))
			for elem in m.groups():
				#print("     " + elem)
				list_elem = elem.split('" "')
				list_elem[-1] = list_elem[-1].split('"')[0]
				for val in list_elem:
					if val[-2:] == ".o":
						continue
					lib_name = val.split('/')[-1].split(".so")[0]
					if lib_name[:3] == "lib":
						lib_name = lib_name[3:].replace("_","-")
						#print("         " + lib_name)
						list_of_flags["cpp"].append('-l' + lib_name)
		"""
		"""
		m = re.search('^(.*)\'((.*)/([a-zA-Z0-9_\-.]*)\.so)\'$', line)
		if m != None:
			 " ""
			print("element : " + str(len(m.groups())))
			for elem in m.groups():
				print("     " + elem)
			"" "
			if len(m.groups()) == 4:
				#print("element : " + line)
				#print("  to: " + m.groups()[3] + " (.so)")
				#if "libboost_container" == m.groups()[3]:
				#	exit(0)
				genrate_lutin_file(m.groups()[3], list_of_file, list_of_flags)
				##for item in list_of_file:
				##	print("          " + item)
				list_of_file = []
				list_of_flags = copy.deepcopy(list_of_flags_default)
				continue
		"""
		

"""
#create version file
genrate_version("1.66.0")
# generate a global inclue
generate_global_include_module()
# generate a global library
generate_global_module(list_of_library_generated)
"""

