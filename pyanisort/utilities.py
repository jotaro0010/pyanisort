#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
import urllib.error
import shutil
import os
import csv
import gzip
import io
import string
import unicodedata
import re
import errno
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

#TODO add error handling and logging
def listAllfiles(startDir):
    startDir = os.path.abspath(startDir)
    files = []
    for dirname, dirnames, filenames in os.walk(startDir):
    # print path to all filenames.
        for filename in filenames:
            files.append(os.path.join(dirname, filename))
    return files

#returns string file object
def openFile(filename):
    try:
        binaryFile = gzip.open(filename).read()
        stringFile = io.StringIO(binaryFile.decode('utf8'))
    except IOError as e:
        if str(e) == 'Not a gzipped file':
            logger.warning('\'{0}\' is not a gzipped file'.format(filename))
            try:
                stringFile = open(filename)
            except IOError as e:
                raise e
        else:
            raise e
    return stringFile

def downloadFile(url, filename):
    # only supports relative paths
    
    path, file = os.path.split(filename)
    
    # make any directories that where not there before
    try:
        os.makedirs(path)
    except (IOError, OSError) as e:
        if (errno.errorcode[e.errno] == 'EEXIST'):
            pass
        else:
            logger.error("Error[{0}] in directory {1}: {2}".format(e.errno, path, e.strerror))
            
    try:
        with urllib.request.urlopen(url) as response,\
             open(filename, 'wb') as outFile:
            shutil.copyfileobj(response, outFile)
    except IOError as e:
        logger.error("IOError[{0}] in file {1}: {2}".format(e.errno, filename, e.strerror))
    except (ValueError, urllib.error.HTTPError) as e:
        logger.error("Error downloading file {0} from '{1}': {2}".format(filename, url, e.strerror))



def checkFileAge(file, daysOld=1):
    checkTime = datetime.now() - timedelta(days=daysOld)
    filetime = datetime.fromtimestamp(os.path.getmtime(file))
    if filetime < checkTime:
        return True
    else:
        return False

def validateFilename(filename):
    # removes any invalid characters \/'":?"<>|
    drive, filePath = os.path.splitdrive(filename)
    folderTree, file = os.path.split(filePath)
    folderTree = re.sub('[\':?*"<>|]', '', folderTree) # doesn't remove \/ since it is a path
    file = re.sub('[\'\\/:?*"<>|]', '', file)
    return os.path.join(drive, folderTree, file)

def renameFiles(filenameList, histFile='history.csv', storeHistory=False):
    # open csv writer for creating rename history file
    if storeHistory:
        try:
            histWriter = open(histFile, 'a', newline='')
            histCSVWriter = csv.writer(histWriter)
        except IOError as e:
            logger.error("IOError[{0}] in file {1}: {2}".format(e.errno, histFile, e.strerror))

    for oldName, newName in filenameList:
        newPath, newFile = os.path.split(newName)

        # make any directories that where not there before
        try:
            os.makedirs(newPath)
        except (IOError, OSError) as e:
            if (errno.errorcode[e.errno] == 'EEXIST'):
                pass
            else:
                logger.error("Error[{0}] in directory {1}: {2}".format(e.errno, newPath, e.strerror))

        try:
            #move the file
            shutil.move(oldName, newName)
            if storeHistory: histCSVWriter.writerow([oldName, newName])
            logger.debug("'{0} -> '{1}'".format(oldName, newName))
        except IOError as e:
            if (errno.errorcode[e.errno] == 'ENOENT'):
                if len(newName) >= 255:
                    logger.error('New name too long must be less than 255 chars was {0} chars: {1}'.format(len(newName), newName))
            else:
                logger.error("IOError[{0}] in file {1}: {2}".format(e.errno, oldName, e.strerror))
    if storeHistory: histWriter.close()

def undoRename(lineStart, lineStop, filename='history.csv'):
    
    # decrement value by one to use in array
    lineStart -= 1
    lineStop -= 1
    # get all rows store them in an array use array to rename certain amount of files
    try:
        fileArr=[] # for the actually renaming the files
        lineArr=[] # for storing the files that where not renamed back into the file
        with open(filename, newline='') as histReader:
            histCSVReader = csv.reader(histReader)
            i=0
            for line in histCSVReader:
                try:
                    originalDir, newDir = line
                    lineArr.append(line)
                    fileArr.append([newDir, originalDir])

                except ValueError as e:
                    #keep line numbers relevent since if blank lines exist in the middle of file
                    if (i == lineStart and lineStart == lineStop) or (i == lineStart and lineStop == -1):
                        logger.error("Line {0} is invalid. might be a blank line".format(lineStart + 1))
                        raise e
                    if i < lineStart:
                        lineStart -= 1
                        lineStop -= 1
                    elif i > lineStart and i < lineStop:
                        lineStop -=1
                i += 1

        # if both numbers are the same copy one line
        # do the same if the second number is 0

        #rename all files specified in history file
        if lineStart == lineStop and lineStart == -1:
            renameFiles(fileArr)
        elif lineStart == lineStop or lineStop == -1:
            renameFiles([fileArr[lineStart]])
        else:
            # add one to lineStop or that line would not have been included
            renameFiles(fileArr[lineStart:(lineStop+1)])
    except IOError as e:
        logger.error("IOError[{0}] in file {1}: {2}".format(e.errno, filename, e.strerror))
        return
    try:
        # save history file with whatever files where not just moved
        with open(filename, 'w', newline='') as histWriter:
            histCSVWriter = csv.writer(histWriter)
            #inverse of what was renamed earlier
            if lineStart == lineStop and lineStart == -1:
                # since entire file was run remove all lines from history
                histCSVWriter.writerows([])
            elif lineStart == lineStop or lineStop == -1:
                # removing only one line
                histCSVWriter.writerows(lineArr[:lineStart] + lineArr[(lineStart+1):])#buggy
            else:
                histCSVWriter.writerows(lineArr[:lineStart] + lineArr[(lineStop+1):])

    except IOError as e:
        logger.error("IOError[{0}] in file {1}: {2}".format(e.errno, filename, e.strerror))


