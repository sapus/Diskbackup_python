Diskbackup_python
=================

A script to store data to a mass storage disk using a simple python script. 
The data in the storage will still be readable. 
The data can be updated to the storage and can also be recovered.
Main idea of this script is to minimize backup time for files.

This code is made in python 3 so maybe it is not 100% compatible with python 2.
I have only tested this code with windows so please tell me if this also work on other platforms.

usage

backup data:

  ```python backup.py store yourfiledirectory yourbackupdirectory```
  
restore data from the backup folder:

  ```python backup.py restore yourbackupdirectory yourfiledirectory ```
  
delete all old version files from the backup directory:

  ```python backup.py cleanbackup youbackupdirectory ```
  
delete a files from the working directory and tell the script to look for deleted files and delete them:

  ```python backup.py syncdeletebackup yourfiledirectory  youbackupdirectory ```
  
delete files from a working directory that have been deleted from the backup directory:

 ```python backup.py syncdeletedirectory youbackupdirectory yourfiledirectory```
