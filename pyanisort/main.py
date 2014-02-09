#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    import pyanisort.utilities as utilities
    import pyanisort.seriesmatch as seriesmatch
    import pyanisort.findtitle as findtitle
    from pyanisort.__init__ import __version__
except ImportError:
    import utilities
    import seriesmatch
    import findtitle
    from __init__ import __version__
    
import logging
import logging.config
import argparse
import os
import sys

def main():
    parser = argparse.ArgumentParser(description='Will automatically sort and rename anime files in a folder based off information gathered from anidb.net')
    subparsers = parser.add_subparsers(help='subcommand help', dest='command')
    sortParser = subparsers.add_parser('sort', help='Will sort anime based on anidb info')
    sortParser.add_argument("fromDir", help="The directory with the files you want to sort")
    sortParser.add_argument("toDir", help="The directory where files will go once sorted")
    sortParser.add_argument("-s", "--silent", action="store_true",
                    help="Turn off output to console (will still log to file)")
    sortParser.add_argument("--history", help="history csv file containing the original path then the current path")

    undoParser =  subparsers.add_parser('undo', help='undo file sorting based of of a history csv file')
    undoParser.add_argument("startLine", type=int, help="the line of the csv file to start rename undo (enter 0 0 to undo entire file)")
    undoParser.add_argument("endLine", type=int, help="the line of the csv file to end rename undo (enter 0 to only undo the line of startLine)")
    undoParser.add_argument("--history", help="history csv file containing the original path then the current path")
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
        

    if args.command == 'undo':
        history=os.path.abspath(args.history)

        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        logging.config.fileConfig('conf/logger.conf', disable_existing_loggers=False)
        logger = logging.getLogger('root')
        
        logger.info('start moving file back to their original locations')
        try:
            if args.history is None:
                utilities.undoRename(args.startLine, args.endLine)
            else:
                utilities.undoRename(args.startLine, args.endLine, history)
        except ValueError:
            logger.error("Could not undo specified line please check history csv file and ensure that line isn't blank")
            return 1
        logger.info('files have finished moving back to their original locations')
        
    elif args.command == 'sort':

        #ensure that program has full path for to and from directories before program cd's to its current location
        fromDir = os.path.abspath(args.fromDir)
        toDir = os.path.abspath(args.toDir)
        silent = args.silent
        history=os.path.abspath(args.history)
        cacheDir = 'cache'

        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        logging.config.fileConfig('conf/logger.conf', disable_existing_loggers=False)
        logger = logging.getLogger('root')

        #need first character of version to use when downloading files using anidb HTTP api
        version = __version__[0]

        logger.info("Starting to group files")
        try:
            allShows = seriesmatch.groupAnimeFiles(fromDir, silentMode=silent)
        except IOError as e:
            logger.error("Program exited with an error")
            return 1
        logger.info("Finished grouping files")

        logger.info("Starting to generate filenames")
        allNewFilenames = findtitle.generateFilenames(int(version), allShows, toDir, cacheDir)
        logger.info("Finished generating filenames")

        logger.info("Starting to rename files")
        if args.history is None:
                utilities.renameFiles(allNewFilenames, storeHistory=True)
        else:
            utilities.renameFiles(allNewFilenames, history, storeHistory=True)
        logger.info("Files have been renamed")


if __name__ == '__main__':
    main()
