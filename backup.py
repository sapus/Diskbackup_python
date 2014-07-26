#!/usr/bin/env python
#title           :backup.py
#description     :This will create a header for a python script.
#author          :Alessandro Impellizzeri
#date            :26.07.2014
#version         :0.1
#usage           :python backup.py
#notes           :
#python_version  :3.3  
#==============================================================================
from filecmp import cmp
import sys
import os
import shutil
MAXVERSIONS = 100
#holt Dateien in einem Verzeichnis 
def files(path):
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file
#holt unterverzeichnisse in einem Verzeichnis            
def folders(path):
    for file in os.listdir(path):
        if not os.path.isfile(os.path.join(path, file)):
            yield file
#Diese Funktion kehrt mit den aktuellsten bak files und die ensprechende nummer
def getUpToDateFiles(path):
    Files = list(files(path))
    Files = list(filter(lambda x: '.bak.' in x,Files))#nur wenn .bak. in Dateiname
    backdata = list(map(lambda x:str.split(x,'.bak.'),Files))
    backdata = [[x[1],int(x[0])] for x in backdata]
    backfiles = set([file[0] for file in backdata])

    #Get Up to Date Files
    UpToDateFiles = []
    for file in backfiles:
        backdataforfile = list(filter(lambda x: file in x[0],backdata))#hole nur die files mit dem name
        backdataforfile = sorted(backdataforfile,key=lambda l:l[1], reverse=True)
        UpToDateFiles.append([backdataforfile[0][0],backdataforfile[0][1]])
        
    return UpToDateFiles

    
def restore(backdir,dir):
    files = getUpToDateFiles(backdir)
    
    if not os.path.exists(dir):
         os.makedirs(dir)    
    for file in files:
        fileback =  os.path.join(backdir,str(file[1]) + '.bak.' + file[0])
        filedest =  os.path.join(dir,file[0])
        if os.path.isfile(filedest) and cmp(fileback, filedest, shallow=0):
            print ('File ', file[0], ': already contained')
            continue
        print ('Restoring \t', file[0] ,' Version:', file[1])
        try:
            shutil.copy(fileback, filedest)
        except OSError as e:
            pass
    thefolders = folders(backdir)
    
    for folder in thefolders:
        restore(os.path.join(backdir,folder),os.path.join(dir,folder))
            
def backup(dir, backdir=None,types=None, files=None):
    "Back up files or files with extension in passed tuple types"

    if files is None:
        files=os.listdir(dir)
    # create directory named 'bak' in current directory
    if backdir is None:
        newdir = os.path.join(dir, 'bak')
    else:
        newdir = backdir
    print('Folder : ',newdir)
        
    # Backup directory
    for file in files:
        abspath = os.path.abspath(os.path.join(dir, file))

        if os.path.isfile(abspath):
            ext=((os.path.splitext(file))[1]).lower()[1:]
            if types is None or ext in types:
                # check for existence of previous versions
                index=1


                
                if not os.path.exists(newdir):
                    os.makedirs(newdir)

                while 1:
                    if index > MAXVERSIONS:
                        break

                    bakup = os.path.join(newdir, str(index) + '.bak.' + file )
                    if not os.path.exists(bakup):
                        break
                    index += 1

                if index>1:
                    # no need to backup if file and last version are identical
                    oldbakup = os.path.join(newdir, str(index-1) + '.bak.' + file)

                    try:
                        if os.path.isfile(oldbakup) and cmp(abspath, oldbakup, shallow=0):
                            print ('File ', file, ': file is unchanged')
                            continue
                    except OSError as e:
                        pass

                try:
                    print ('Backing up file \t', file ,' Version:', index)
                    shutil.copy(abspath, bakup)
                except OSError as e:
                    pass

        elif os.path.isdir(abspath):#tiefer in die Verzeichnis Struktur file ist ein unterverzeichnis
            if backdir is None:
                backup(abspath, types)
            else:
                backup(abspath, os.path.join(backdir,file), types)
            pass

def deleteUpToVersionFiles(directory,filename,version):
    for i in range(version):
        filetodelete =  os.path.join(directory,str(i+1) + '.bak.' + filename)
        print ('Removing : ',filetodelete)
        os.remove(filetodelete)    
            
def cleanbackup(backdir):
    files = getUpToDateFiles(backdir)
    for file in files:
        if file[1]>1:
            deleteUpToVersionFiles(backdir,file[0],file[1]-1)#Delete old versions
            #renaming newest version
            filebackupdate =  os.path.join(backdir,str(file[1]) + '.bak.' + file[0])
            fileback =  os.path.join(backdir,'1.bak.' + file[0])
            os.rename(filebackupdate,fileback)
            
    thefolders = folders(backdir)    
    for folder in thefolders:
        cleanbackup(os.path.join(backdir,folder))    

def syncdeletebackup(dir,backdir):
    backfiles = getUpToDateFiles(backdir)
    dirfiles = list(files(dir))

    for file in backfiles:
        if not file[0] in dirfiles:
            print('Deleting:',file[0],' from Backup directory')
            deleteUpToVersionFiles(backdir,file[0],file[1])#delete files not contained in backdir
            
    thefolders = folders(dir)    
    for folder in thefolders:
        syncdeletebackup(os.path.join(dir,folder),os.path.join(backdir,folder))    

def syncdeletedirectory(backdir,dir):
    backfiles = getUpToDateFiles(backdir)
    backonlyfiles = [file[0] for file in backfiles]
    dirfiles = list(files(dir))

    for file in dirfiles:
        if not file in backonlyfiles:
            print('Deleting:',file,' from directory')
            os.remove(os.path.join(dir,file))#delete files not contained in dir
            
    thefolders = folders(backdir)    
    for folder in thefolders:
        syncdeletebackup(os.path.join(backdir,folder),os.path.join(dir,folder))        
        
if __name__=="__main__":
    if len(sys.argv)<3:
        sys.exit("""Usage: %s [action] [directory input] [directory action]\n 
                    action:\n
                            store (store in a backup folder (directory action))\n
                            restore (restore data to original folder (directory action))\n
                            cleanbackup (clean all version files)\n
                            syncdeletebackup (delete all file that have been deleted in the working directory (input working directory action in backup directory))\n
                            syncdeletedirectory """ % sys.argv[0])
        
    tree_top = os.path.abspath(os.path.expanduser(os.path.expandvars(sys.argv[2])))
    if sys.argv[1]=='store':
        if len(sys.argv)>=3:
            bakfolder = os.path.abspath(os.path.expanduser(os.path.expandvars(sys.argv[3])))
            backup(tree_top,bakfolder)
        else:
            backup(tree_top)
            
            
    if sys.argv[1]=='restore':
        if len(sys.argv)==4:
            destination = os.path.abspath( os.path.expanduser(os.path.expandvars(sys.argv[3])  )  )
            restore(tree_top,destination)#tree_top here is the backup folders
        else:
            sys.exit("This action needs [directory input] and [directory action]")

    if sys.argv[1]=='syncdeletebackup':
        if len(sys.argv)==4:
            backupdir = os.path.abspath( os.path.expanduser(os.path.expandvars(sys.argv[3])  )  )
            syncdeletebackup(tree_top,backupdir)
        else:
            sys.exit("This action needs [directory input] and [directory action]")
            
    if sys.argv[1]=='syncdeletedirectory':
        if len(sys.argv)==4:
            directory = os.path.abspath( os.path.expanduser(os.path.expandvars(sys.argv[3])  )  )
            syncdeletedirectory(tree_top,directory)
        else:
            sys.exit("This action needs [directory input] and [directory action]")            
            
    if sys.argv[1]=='cleanbackup':
        if len(sys.argv)==3:
            cleanbackup(tree_top)
        else:
            sys.exit("This action needs only [directory input]")    
