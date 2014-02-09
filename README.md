# pyAniSort

pyAniSort is a command line utility that will sort and rename anime video files into folders separated by the name of the series.

## Usage

There are two different commands that pyAnisort has:  
The first being `sort`  
And the second `undo`

### The sort command

The sort command requires two arguments the from directory and the to directory

The silent option turns off any parts of the script that would ask for user input
`-s, --silent`     Turn off console interactivity

The history argument takes the name of a csv file that will store the renaming history
`--history FILE`     changes where to save history file ('history.csv' is the default)

`> pyAniSort sort 'from/directory' 'to/directory' -s --history history.csv`

The program will sort this:
```
|-- From Folder/
|   | [Sub Group A] Series Name - 01 [ABCD1234].mkv
|   | [Sub Group A] Series Name - 02 [ABCD1234].mkv
|   | [Sub Group A] Series Name - 03 [ABCD1234].mkv
|   | [Sub Group B] Other Series Name Ep01 [ABCD1234].mkv
|   | [Sub Group B] Other Series Name Ep02 [ABCD1234].mkv
|   | [Sub Group B] Other Series Name Ep03 [ABCD1234].mkv
```

To This:
```
|-- To Folder/
|   |-- Series Name/
|   |   |-- Series Name - 01 - title.mkv
|   |   |-- Series Name - 02 - title.mkv
|   |   |-- Series Name - 03 - title.mkv
|   |-- Other Series Name/
|   |   |-- Other Series Name - 01 - title.mkv
|   |   |-- Other Series Name - 02 - title.mkv
|   |   |-- Other Series Name - 03 - title.mkv
```

### The undo command

The undo command will use the history.csv file to undo the sorting operation in case there was an error.

There are two required positional arguments that are required for the undo command

The history argument takes the name of a csv file that will store the renaming history
`--history FILE`     changes where to save history file ('history.csv' is the default)

`> pyanisort undo startLine endLine --history history.csv`

The first one will tell the program what line of the file to start on and the second will tell it what line to end on.  
This allows better control of what files to undo

Running the following command will start undoing the files stored in history.csv from line 30 to line 40, or until the end of the file if there are less than 40 lines.  
`> pyanisort undo 30 40`

this next command will undo all of the files stored in the history.csv file.  
`> pyanisort undo 0 0`

Both of the following commands will only undo the file at line 44 of the history.csv file  
`> pyanisort undo 44 44`  
`> pyanisort undo 44 0`

After any one of these commands are used the history.csv file will be modified to reflect the undo operation.

## Important Files

There are two files that are automatically created when pyAniSort is run.  
prefNames.csv and history.csv

As of right now they will be stored along with the log files in the python `lib/site-packages`
Windows: `C:\Python33\Lib\site-packages`

### prefNames.csv - Prefered show names
This file is for storing information about the show. This helps save time when gathering show information multiple times.
There are three values stored in the csv file the **anime ID (aid)**, **official show name**, and the **parsed name**

The **aid** is the unique id that the anidb database uses for the show  
The **official show name** is the full series name pulled from the anidb. 
It is also the name that will be used when renaming and sorting the video files.  
The **parsed name** is the name that has been pulled from the filename before it was sorted.  

| aid  | Official Name | Parsed Name |
| ------------- | ------------- | ------------- |
| 9541  | Shingeki no Kyojin  | Shingeki no Kyojin  |
| 9787  | Ore no Nounai Sentakushi ga, Gakuen Lovecome o Zenryoku de Jama Shiteiru  | NouCome  |

This is the contents of prefNames.csv that match the table
```
prefName.csv
9541,Shingeki no Kyojin,Shingeki no Kyojin
9787,"Ore no Nounai Sentakushi ga, Gakuen Lovecome o Zenryoku de Jama Shiteiru",NouCome
```


### history.csv - File rename history

There are two columns in the history.csv file. The first refers to the original location of a video file and the second refers to the sorted location

| Original Name  | Sorted Name |
| ------------- | ------------- |
| D:\test_files\[Sub Group A] Series Name - 01 [ABCD1234].mkv | D:\Anime\Series Name\Series Name - 01 - title.mkv |
| D:\test_files\[Sub Group B] Other Series Name Ep01 [ABCD1234].mkv | D:\Anime\Other Series Name\Other Series Name - 01 - title.mkv |

This is an example ot the contents of history.csv useig real filenames
```
history.csv
D:\test_files\[EveTaku] Shingeki no Kyojin - 25 (1280x720 x264-Hi10P AAC)[783716E5].mkv,D:\Anime\Shingeki no Kyojin\Shingeki no Kyojin - 25 - The Wall Raid on Stohess District (3).mkv
D:\test_files\[Irrational Typesetting Wizardry] NouCome - 01 [F87C6CC0].mkv,"D:\Anime\Ore no Nounai Sentakushi ga, Gakuen Lovecome o Zenryoku de Jama Shiteiru\Ore no Nounai Sentakushi ga, Gakuen Lovecome o Zenryoku de Jama Shiteiru - 01 - That Choice Put My Life in Motion.mkv"
```

## Installation

`> pip install pyanisort`

## Possible Errors
There are a few possible errors that may occur when running this script

##### Banned

`0000-00-00 00:00:00,000 - pyanisort.findtitle - ERROR - findtitle : 62 - Error parsing through cache\0000.xml.gz: Banned`

This means that the anidb.net server has gotten too many requests from the machines IP address.  
It will refuse any more connections for the next couple hours.

This is a security measure put in place by the server and I have not found any other method of getting around it other than by waiting a couple hours to run the script again



## Contact Me

Questions or comments about `pyAniSort`? send me an email at [jotaro0010@gmail.com](mailto:jotaro0010@gmail.com).
