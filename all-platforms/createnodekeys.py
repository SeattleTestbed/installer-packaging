""" 
Author: Justin Cappos

Module: Node Manager key pair initializer.  

Start date: October 17rd, 2008

Adapted from nminit.py

"""

# need repy portability 
from repyportability import *
_context = locals()
add_dy_support(_context)

# need to generate a public key
rsa = dy_import_module('rsa.r2py')


import os

import persist




# init the keys...
# Zack Boka: Added the functionality of changing directories so the parent
#            funciton would not have to worry about doing this.
def initialize_keys(keybitsize, nodemanager_directory="."):
  # nodemanager_directory: The directory in which the nodeman.cfg file is
  #                        located.

  # initialize my configuration file.   This involves a few variables:
  #    pollfrequency --  the amount of time to sleep after a check when "busy
  #                      waiting".   This trades CPU load for responsiveness.
  #    ports         --  the ports the node manager could listen on.
  #    publickey     --  the public key used to identify the node...
  #    privatekey    --  the corresponding private key for the node...
  #
  # Only the public key and private key are set here...
  configuration = persist.restore_object('nodeman.cfg')

  curdir = os.getcwd()
  os.chdir(nodemanager_directory)


  keys = rsa.rsa_gen_pubpriv_keys(keybitsize)
  configuration['publickey'] = keys[0]
  configuration['privatekey'] = keys[1]

  persist.commit_object(configuration, "nodeman.cfg")


  os.chdir(curdir)

if __name__ == '__main__':
  initialize_keys() 
