"""
<Program Name>
  rebuild_base_installers.py


<Purpose>
  This program creates new base installers for the Custom Installer Builder. 
  (A base installer is a Seattle installer that lacks the user keys and 
  assigned resource proportions per a `vesselinfo` file. It cannot be 
  installed as-is. The Custom Installer Builder will add the required 
  file to make a fully working installer.)

  It is assumed that you followed the steps to check out the required 
  dependencies (via `./scripts/initialize.py`) and build the initial 
  directory layout (via `./scripts/build.py`) as outlined in 
  `README.md` already.


<Usage>
  Configuration
  =============
  Before starting this program, adapt the configuration variables 
  below to suit your setup. These include the softwareupdater URL 
  and key files, the nodemanager version string your installers will 
  use, the user name for which to build the installers, the desired 
  output dir for new installers, and the backup dir for old installers.

  Make sure that the directories exist. Also, ensure that your 
  `seattle_repy/softwareupdater.py`'s software updater URL and 
  public key agree with what is given here.
  BE VERY CAREFUL about the softwareupdater-related items. 
  Making mistakes here will likely result in installers that you 
  will not be able to push updates to!

  Execution
  =========
  Once configured, run this program under a user account with `sudo` 
  privileges. (Don't run under `sudo` right away, we will invoke it 
  when we need it.)

    python ./rebuild_base_installers.py NODEMANAGER_VERSION_STRING

  We force you to give `seattle_repy/nmmain.py`'s version string 
  on the command line when you want to rebuild, so that your shell's 
  history contains a record of what you did.


<Historical Footnote>
  This program is a Python port of the shell script used for this purpose 
  previously, `rebuild_base_installers_for_seattlegeni.sh`
"""

###########################################################
# Customize the variables below to your setup / config!

software_update_url = 'http://blackbox.poly.edu/updatesite/'
public_key_file = '/full/path/to/softwareupdater.publickey'
private_key_file = '/full/path/to/softwareupdater.privatekey'

base_installer_directory = '/full/path/to/baseinstaller/target/dir'
base_installer_archive_dir = '/full/path/to/baseinstaller/archive'

user = 'installer_package_owner'

# End of customizable config items
###########################################################


import sys
import string
import os
import shutil
import subprocess
import pwd
import grp
import glob

# Add `./seattle_repy` to the sys path so we can import and check the 
# actual files thaast will end up in the base installers.
# We can do this as `./seattle_repy` is on the same hierarchy 
# level in the filesystem as this program file.
my_path = os.path.abspath(os.path.dirname(__file__))
seattle_repy_path = os.path.join(my_path, "seattle_repy")
sys.path.insert(0, seattle_repy_path)
from softwareupdater import softwareupdatepublickey
from softwareupdater import softwareurl
from nmmain import version

import package_installers

from repyportability import *
add_dy_support(locals())

dy_import_module_symbols("rsa.r2py")


def rebuild_base_installers(newversion):                                         
  software_update_key = rsa_file_to_publickey(public_key_file)

  repo_parent_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../DEPENDENCIES")

  # Check variables first
  if newversion == "":
    print "You must supply a version string."
    print "usage: " + sys.argv[0] + " version"
    sys.exit(1)

  if software_update_url == "":
    print "software_update_url isn't set."
    sys.exit(1)

  if not os.path.exists(base_installer_directory):
    print "base_installer_directory doesn't exist."
    sys.exit(1)

  if not os.path.exists(base_installer_archive_dir):
    print "base_installer_archive_dir doesn't exist."
    sys.exit(1)

  if not os.path.exists(repo_parent_dir):
    print "repo_parent_dir doesn't exist."
    sys.exit(1)

  if not version:
    print "You need to set the version string in nmmain.py"
    sys.exit(1)

  if not version == newversion:
    print "You need to set the version string which is same as the version string in nmmain.py"
    sys.exit(1)

  if not software_update_url == softwareurl:
    print "Did not find the correct update url in softwareupdater.py" 
    sys.exit(1)

  if not software_update_key == softwareupdatepublickey:
    print "Did not find the correct update key in softwareupdater.py"
    sys.exit(1)

  try:
    pwd.getpwnam(user)
  except KeyError:
   print "user account " + user + " does not exist."
   sys.exit(1)

  # Now let's start building!
  print "Archiving old base installers to " + base_installer_archive_dir
  print "Warning: failure after this point may leave you with no base installers!"

  for files in glob.glob(base_installer_directory + '/seattle_*' ):
    if os.path.isfile(files):
      shutil.move(files, base_installer_archive_dir)
    else:
      print "Skipping link/directory", files

  print "Building new base installers at " + base_installer_directory

  try:
    package_installers.package_installers(base_installer_directory, version, private_key_file, public_key_file)

  except Exception, e:
    print "Building base installers failed. Exception:", repr(e)
    sys.exit(1)

  print "Changing base installer symlinks."

  os.chdir(base_installer_directory)

  if not os.path.exists("seattle_"+ version +"_android.zip") or not os.path.exists("seattle_"+ version +"_linux.tgz") or not os.path.exists("seattle_"+ version +"_mac.tgz"):
    print "The base installers don't appear to have been created."
    sys.exit(1)

  uid = pwd.getpwnam(user).pw_uid
  gid = grp.getgrnam(user).gr_gid
  for files in glob.glob('./seattle_*'):
    if os.path.isfile(files):
      os.chown(files, uid, gid)

  os.symlink("seattle_" + version + "_android.zip", 'seattle_android.zip')
  os.symlink("seattle_" + version + "_linux.tgz", 'seattle_linux.tgz')
  os.symlink("seattle_" + version + "_mac.tgz", 'seattle_mac.tgz')
  os.symlink("seattle_" + version + "_win.zip", 'seattle_win.zip')

  print 'New base installers created and installed.'

def main():
  if not public_key_file:
    print "public_key_file isn't set." 
    sys.exit(1)

  if not private_key_file:
    print "private_key_file isn't set."
    sys.exit(1)

  try:
    newversion = sys.argv[1]
  except:
    print "Usage: python ./rebuild_base_installers.py version_STRING" 
    sys.exit(1)

  rebuild_base_installers(newversion)

if __name__ == '__main__':
  main()
