#
#		                     /$$        /$$$$$$  /$$
#		  /$$$$$$$  /$$$$$$ | $$$$$$$ |__/  \ $$ /$$
#		 /$$_____/ |____  $$| $$__  $$  /$$$$$$/| $$
#		|  $$$$$$   /$$$$$$$| $$  \ $$ /$$____/ | $$
#		 \____  $$ /$$__  $$| $$  | $$| $$      | $$
#		 /$$$$$$$/|  $$$$$$$| $$$$$$$/| $$$$$$$$| $$
#		|_______/  \_______/|_______/ |________/|__/                         
#	
#			 ~-- This python script will --~ 
#	     
#	[*] Scan a directory tree and look for maven artifacts
#	[*] Configure the sonar-project.properties based on 
#	        maven config
#
#			 ~-- Usage and Requirements --~
#
#	[*] python SonarBatchAdd.py must be on the main directory
#		that contains all the other projects

import os
import xml.etree.ElementTree as ET
from subprocess import Popen

workingDir = os.getcwd()
dirsToScan = []
namespaces = {'maven':'http://maven.apache.org/POM/4.0.0'}
dirsToAvoid = ['.sonar','CVS']
sonarServerAddr = 'http://localhost:9000'

class ProjectInformation:
	NAME = 1
	VERSION = 2
	ARTIFACT_ID = 3

def getProjectInformation(information):
	pom = ET.parse('pom.xml').getroot()
	artifactId = pom.findall('maven:artifactId', namespaces)[0].text
	name = pom.findall('maven:name', namespaces)[0].text
	version = pom.findall('maven:version', namespaces)[0].text
	
	if(information == ProjectInformation.NAME):
		return name
	elif(information == ProjectInformation.VERSION):
		return version
	elif(information == ProjectInformation.ARTIFACT_ID):
		return artifactId
	else:
		return False

def writeSonarConfig(pName, pVersion, aId):
	if(os.path.isfile('sonar-project.properties')):
		print "[e] Sonar configuration file already exists for project: " + pName
		return
	else:
		print("[i]	Writing Configuration File...")
		
		file = open('sonar-project.properties', 'w')
		file.write('#	Sonar configuration file for project: ' + pName + "\n")
		file.write("#	Automatically created with SonarBatchAdd Script\n\n")
		file.write("#   Identifier for the project (must be unique on the SonarQube Server)\n")
		file.write('sonar.projectKey=' + aId + "\n")
		file.write("#	Sonar Project Name (Visible on the SonarQube Application)\n")
		file.write('sonar.projectName=' + projectName + "\n")
		file.write("#	Project Version\n")
		file.write("sonar.projectVersion=" + pVersion + "\n")
		file.write("#	Source Path\n")
		file.write("sonar.sources=./\n")
		file.write("#	Encoding Configuration of the source code (commented to use the system default encoding)\n")
		file.write("#sonar.sourceEncoding=UTF-8\n")
		file.write("#	Sonar Server Address (Commented to use the default localserver at port 9000)\n")
		file.write("#sonar.host.url=" + sonarServerAddr + "\n")
		file.close()
		
def launchRunner(pName):
	print('[i] Launching Sonar Runner for Project: ' + pName)
	runner = Popen("sonar-runner.bat", cwd=os.getcwd())
	stdout, stderr = runner.communicate()
		
for name in os.listdir("."):
	if(name not in dirsToAvoid and os.path.isdir(os.path.join(".", name))):
		dirsToScan.append(name)

print("[i] Discovery of maven artifacts started...\n")
		
for path in dirsToScan:
	os.chdir(path)
	if(os.path.isfile("pom.xml")):
		print "[i] --> maven artifact found at " + path
		
		projectName = getProjectInformation(ProjectInformation.NAME)
		projectVersion = getProjectInformation(ProjectInformation.VERSION)
		artifactId = getProjectInformation(ProjectInformation.ARTIFACT_ID)
		
		print "[i] Project Name.........: " + projectName
		print "[i] Project Version......: " + projectVersion
		print "[i] Artifact ID..........: " + artifactId
		
		writeSonarConfig(projectName, projectVersion, artifactId)
		launchRunner(projectName)
	else:
		print "[e] not a valid maven artifact at: " + path
	os.chdir(workingDir)
