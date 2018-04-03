#!/usr/bin/python

#
#	Deploys built artifacts to $SERVER_HOME/repository/usr
#
#   Author: Dario Del Piano

import os, sys, getopt, subprocess, json, shutil
from subprocess import call

config = json.loads(open(os.path.join(os.path.dirname(__file__), 
					'../source_setup/config.json')).read())
sourcesdir = config['sourcesdir']
target_dir = os.path.abspath(config['sourcesdir'])
doc_dir = os.path.join(target_dir, 'org.geppetto.docs')
java_doc = os.path.join(doc_dir, 'source', 'javadoc')
yes = set(['yes','y'])

def clone_repos():
	for repo in config['repos']:
		repo_folder = os.path.join(sourcesdir, repo['name'])
		print repo['name']
		if not os.path.exists(repo_folder):
			print repo['name'] + " is not present in your sources folder"
			print "Do you want to clone it to generate the documentation?"
			print "(y/n)"
			repository = raw_input(">").lower()

			if repository in yes:
				print "Cloning ..."
				subprocess.call(['git','clone',repo['url']], cwd=target_dir)
				repo['auto_install'] = "yes"
			else:
				repo['auto_install'] = "no"
		else:
			repo['auto_install'] = "yes"	

def clone_docs():
	if not os.path.exists(doc_dir):
		subprocess.call(['git','clone','https://github.com/openworm/org.geppetto.docs'], 
						cwd=target_dir)
	else:
		if os.path.exists(java_doc):
			shutil.rmtree(java_doc)
		os.makedirs(java_doc)

def create_javadoc():
	jd_sourcepath = ""
	jd_packages = ""
	for repo in config['repos']:
		if repo['auto_install'] is "yes":
			print repo['name'] + " will be included in the documentation"
			repo_src_main = os.path.join(target_dir, repo['name'], 'src', 'main', 'java')
			repo_src_main += ":"
			jd_sourcepath += repo_src_main
			repo_src_main = os.path.join(target_dir, repo['name'], 'src', 'test', 'java')
			repo_src_main += ":"
			jd_sourcepath += repo_src_main
			if jd_packages is "":
				jd_packages += repo['name']
			else:
				jd_packages = jd_packages + " " + repo['name']
	jd_sourcepath = jd_sourcepath[:-1]
	#subprocess.call(['javadoc',
	#				 '-version',
	#				 '-author',
	#				 '-private',
	#				 '-verbose',
	#				 '-d',
	#				 '{}'.format(java_doc),
	#				 '-sourcepath',
	#				 '{}'.format(jd_sourcepath),
	#				 '-subpackages',
	#				 '.',
	#				 '"{}"'.format(jd_packages)])
	# Subprocess replaced by system due to an error with the quotes with javadoc
	os.system("javadoc -version -author -private -verbose -d " \
			  "{0} -sourcepath {1} -subpackages . {2}".format(java_doc,
			  												  jd_sourcepath,
			  												  jd_packages))


def commit_and_push():
	commit_message = raw_input("Please, insert your commit message\n> ")
	subprocess.call(['git',
					 'add',
					 '.'], 
					 cwd=java_doc)
	subprocess.call(['git',
					 'commit',
					 '-m', 
					 '{}'.format(commit_message)], 
					 cwd=java_doc)
	#subprocess.call(['git',
	#				 'push',
	#				 'origin'], 
	#				 cwd=java_doc)

def main(argv):
	clone_repos()
	clone_docs()
	create_javadoc()
	commit_and_push()


if __name__ == "__main__":
	main(sys.argv[1:])