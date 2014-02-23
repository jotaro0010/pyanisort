#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
import urllib.error
import shutil
import os
import sys
import csv
import gzip
import io
import string
import unicodedata
import re
import errno
import zlib
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
    
    if path != '':
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



def checkFileAge(filename, daysOld=1):
    checkTime = datetime.now() - timedelta(days=daysOld)
    filetime = datetime.fromtimestamp(os.path.getmtime(filename))
    if filetime < checkTime:
        return True
    else:
        return False

def validateFilename(filename):
    # removes any invalid characters \/'":?"<>|
    drive, filePath = os.path.splitdrive(filename)
    folder, file = os.path.split(filePath)
    folder = re.sub('[\':?*"<>|]', '', folder) # doesn't remove \/ since it is a path
    file = re.sub('[\'\\/:?*"<>|]', '', file)
    return os.path.join(drive, folder, file)

def getCRC(filename, message='Calculating CRC'):
    buffer = 65536
    crc = 0
    data = 0
    totalSize = os.path.getsize(filename)
    index = 0
    if buffer > totalSize:
        buffer = totalSize
    # prevents a divde by zero
    if totalSize == 0:
        totalSize = 1
    with open(filename, 'rb') as f:
        while data != b'':
            data = f.read(buffer)
            index += 1
            sys.stdout.write('{0}: {1:.0%}\r'.format(message, (buffer*index)/totalSize))
            sys.stdout.flush()
            crc = zlib.crc32(data, crc)
        sys.stdout.write('{0}: {1:.0%}: {2:8X}'.format(message, (buffer*index)/totalSize, crc))
    sys.stdout.write('\n')
    sys.stdout.flush()
    return '{0:8X}'.format(crc)

def undoRename(lineStart, lineStop, verify=False, filename='history.csv'):
    
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
            renameFiles(fileArr, verify=verify)
        elif lineStart == lineStop or lineStop == -1:
            renameFiles([fileArr[lineStart]], verify=verify)
        else:
            # add one to lineStop or that line would not have been included
            renameFiles(fileArr[lineStart:(lineStop+1)], verify=verify)
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
                histCSVWriter.writerows(lineArr[:lineStart] + lineArr[(lineStart+1):])
            else:
                histCSVWriter.writerows(lineArr[:lineStart] + lineArr[(lineStop+1):])

    except IOError as e:
        logger.error("IOError[{0}] in file {1}: {2}".format(e.errno, filename, e.strerror))

def renameFiles(filenameList, verify=False, copy=False, histFile='history.csv', storeHistory=False):
    # open csv writer for creating rename history file
    if storeHistory:
        try:
            histWriter = open(histFile, 'a', newline='')
            histCSVWriter = csv.writer(histWriter)
        except IOError as e:
            logger.error("IOError[{0}] in file {1}: {2}".format(e.errno, histFile, e.strerror))

    for oldName, newName in filenameList:
        newPath, newFile = os.path.split(newName)
        oldPath, oldFile = os.path.split(oldName)

        logger.info("'{0} --moving to-> '{1}'".format(oldName, newName))
        # make any directories that where not there before
        try:
            os.makedirs(newPath)
        except (IOError, OSError) as e:
            if (errno.errorcode[e.errno] == 'EEXIST'):
                pass
            else:
                logger.error("Error[{0}] in directory {1}: {2}".format(e.errno, newPath, e.strerror))
                
        if verify:
            logger.debug("Calculating CRC before sorting for '{0}'".format(oldFile))
            beforeCRC = getCRC(oldName,'Calculating CRC before moving')
            logger.debug("'{0}': {1}".format(oldFile, beforeCRC))
        try:
            #move or copy the file
            if copy:
                sys.stdout.write('Copying File...\r')
                shutil.copy(oldName, newName)
                logger.debug("'{0} --copied to-> '{1}'".format(oldName, newName))
            else:
                sys.stdout.write('Moving File...\r')
                shutil.move(oldName, newName)
                if storeHistory: histCSVWriter.writerow([oldName, newName])
                logger.debug("'{0} --moved to-> '{1}'".format(oldName, newName))
        except IOError as e:
            if (errno.errorcode[e.errno] == 'ENOENT'):
                if len(newName) >= 255:
                    logger.error('New name too long must be less than 255 chars was {0} chars: {1}'.format(len(newName), newName))
                    continue
            else:
                logger.error("IOError[{0}] in file {1}: {2}".format(e.errno, oldName, e.strerror))
                continue
        if verify:
            logger.debug("Calculating CRC after move for '{0}'".format(newFile))
            afterCRC = getCRC(newName, 'Calculating CRC after move')
            logger.debug("'{0}': {1}".format(newFile, afterCRC))
            if beforeCRC == afterCRC:
                logger.info('{0} has been sorted succesfully to {1}'.format(oldFile, newFile))
                logger.debug('{0} is equal to {1}'.format(beforeCRC, afterCRC))
            else:
                logger.warning('{0} has not been sorted succesfully to {1}'.format(oldFile, newFile))
                logger.warning('{0} is not equal to {1}'.format(beforeCRC, afterCRC))
    if storeHistory: histWriter.close()


