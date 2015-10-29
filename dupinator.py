#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create a bash script to remove duplicate files

Built from Bill Bumgarner's Dupinator recipe.
http://code.activestate.com/recipes/362459/
"""
import os
import stat
import hashlib
import filecmp
from optparse import OptionParser
import sys

options = {}
dirMove = "~/zzz"

def scanDir(listDirs):
    """
    Scan all files in each directory from listDirs.
    """
    filesBySize = {}

    for dirname in listDirs:
        print '# Scanning directory "%s"....' % dirname
        #os.path.walk(x, walker, filesBySize)
        
        for fname in os.listdir(dirname):
            f = os.path.join(dirname, fname)
            
            if not os.path.isfile(f):
                if options.debug: print "# " + f + " is not a file"
                continue
            
            if os.path.islink(f):
                if options.debug: print "# " + f + " is a symlink"
                continue
            
            size = os.stat(f)[stat.ST_SIZE]
            
            if size == 0:
                continue
            
            if filesBySize.has_key(size):
                a = filesBySize[size]
            else:
                a = []
                filesBySize[size] = a
            a.append(f)
    return filesBySize

def scanDirs(listDirs):
    """
    Recursively scan all files in each directory from listDirs.
    Called when using parser option : "-R / --recursive"
    """
    filesBySize = {}
    
#    if options.modeKeep1:
#        print "# Keep files in %s." % listDirs[0]
    
    for sDir in listDirs:
        print '# Scanning directory "%s"....' % sDir
        
        for dirname, dummyDirs, fnames in os.walk(sDir):
            for fname in fnames:
                f = os.path.join(dirname, fname)
                
                if not os.path.isfile(f):
                    if options.debug: print "# " + f + " is not a file"
                    continue
                
                if os.path.islink(f):
                    if options.debug: print "# " + f + " is a symlink"
                    continue
                
                size = os.stat(f)[stat.ST_SIZE]
                
                if size == 0:
                    continue
                
                if filesBySize.has_key(size):
                    a = filesBySize[size]
                else:
                    a = []
                    filesBySize[size] = a
                a.append(f)
    return filesBySize

def findDuplicates(filesBySize):
    print '# Finding potential dupes...'
    
    dupes = []
    total = len(filesBySize)
    
    while len(filesBySize):
        (k, inFiles) = filesBySize.popitem()
        #outFiles = []
        hashes = {}
        if len(inFiles) is 1: continue
        inFiles.sort()
        prevFile = ""
        if options.debug:
            print '# %d / %d Testing %d files of size %d.' % (len(filesBySize), total, len(inFiles), k)
        elif options.verbose:
            sys.stderr.write('# %d / %d Testing %d files of size %d.\n' % (len(filesBySize), total, len(inFiles), k))
            
        for fileName in inFiles:
            if not os.path.isfile(fileName):
                continue
            if (fileName == prevFile):
                """ We do not want to delete a file because it is a duplicate of itself """
                if options.debug:
                    print "# File already processed : " + fileName
                continue
            prevFile = fileName
            try:
                aFile = file(fileName, 'r')
            except:
                print "# Cannot open file %s !!!" % (fileName)
                continue
            #hasher = md5.new(aFile.read(1024))
            #hashValue = hasher.digest()
            hashValue = hashlib.md5(aFile.read(1024)).digest() # 4096 ?
            aFile.close()
            if hashes.has_key(hashValue):
                if options.debug:
                    print "  # hash found"
                listOfLists = hashes[hashValue]
                isDup = False
                for listOfDupes in listOfLists:
                    if options.debug:
                        print "    # filecmp"
                    if filecmp.cmp(fileName, listOfDupes[0], False):
                        listOfDupes.append(fileName)
                        isDup = True
                        if options.debug:
                            print "      # dupes %s\n              %s" % (listOfDupes[0], fileName)
                        break
                    else:
                        if options.debug:
                            print "      # difs %s\n             %s" % (listOfDupes[0], fileName)
                       
                if not isDup:
                    listOfLists.append([fileName])    # Add a new list of files to the list of lists
            else:
                if options.debug:
                    print "  # new hash"
                hashes[hashValue] = [[fileName]]    # New list of list of files
        
        while len(hashes):
            (dummy, listF) = hashes.popitem()
            while len(listF):
                listF2 = listF.pop()
                if len(listF2) > 1:
                    listF2.sort()
                    #listF2.reverse()
                    dupes.append(listF2)
    return dupes

def outputScript(dupes, listDirs):
    dupes.sort()
    dupes.reverse()
    
    #for d in dupes:
    while dupes:
        d = dupes.pop() # Unstack dupes until it's empty
        found = False
        if options.modeKeep1:
            for f in d[:]:      # Loop on a copy of d to be able to modify it
                                # d is the duplicates' list.
                if f.rfind(listDirs[0]) == 0:
                    found = True
                    print '#     "%s"' % f
                    d.remove(f)
    
        if options.modeKmail and not found:
            for f in d[:]:      # Loop on a copy of d to be able to modify it
                                # d is the duplicates' list.
                if f[-5:] == ":2,RS":   # Keep answered emails in priority
                    found = True
                    print '#     "%s"' % f
                    d.remove(f)
                    break
        
        if options.modeKmail and not found:
            for f in d[:]:      # Loop on a copy of d to be able to modify it
                                # d is the duplicates' list.
                if f[-4:] == ":2,S":   # Keep read emails in 2nd priority
                    found = True
                    print '#     "%s"' % f
                    d.remove(f)
                    break
        
        if not found:
            f = d.pop(0)        # Save the first one if none else
            print '#     "%s"' % f
            
        for f in d:
            if options.modeMove:
                print 'mv "%s" %s' % (f, os.path.join(dirMove, f))
                if not os.path.exists(os.path.dirname(os.path.join(dirMove, f))):
                    os.makedirs(os.path.dirname(os.path.join(dirMove, f)))
            else:
                print 'rm -fv "%s"' % f
        #        os.remove(f)
        print


def main():
    global options

    parser = OptionParser()
    parser.set_usage("usage: %prog [options] [dir]...")
    parser.add_option("-1", "--keep1",  
                    action="store_true", dest="modeKeep1", default=False,
                    help="Keep files in first target directory")
    parser.add_option("-m", "--move",
                    action="store_true", dest="modeMove", default=False,
                    help="Move duplicate files to ~/zzz instead of deleting them")
    parser.add_option("-k", "--kmail",
                    action="store_true", dest="modeKmail", default=False,
                    help="In kmail maildirs, delete unread mails first")
    parser.add_option("-R", "--recursive",
                    action="store_true", dest="recursive", default=False,
                    help="Visit subdirectories recursively.")
    parser.add_option("-d", "--debug",
                    action="store_true", dest="debug", default=False,
                    help="Verbose output for debugging")
    parser.add_option("-v", "--verbose",
                    action="store_true", dest="verbose", default=False,
                    help="Verbose output but less than debug")
                    
    (options, listDirs) = parser.parse_args()
    
    if not len(listDirs):
        listDirs.append(".")    # Default to current directory.
    
    print '#!/bin/bash'
    
    if options.modeKeep1:
        print "# Keep files in %s." % listDirs[0]

    if options.recursive:
        filesBySize = scanDirs(listDirs)
    else:
        filesBySize = scanDir(listDirs)
    
    dupes = findDuplicates(filesBySize)
    outputScript(dupes, listDirs)

if __name__=='__main__': main()
