This is a very fast parsing script for downloaded TV shows and movies. It will use scene-standard naming conventions (and a lot of nonstandard ones, too) to match TV shows and movies and rename / move them as you like.

My script now supports format strings similar to SABnzbd! It should also work on all platforms that have a Python interpreter available, though you will need to change the directory structure of the format strings from using \\ to / for it to work on UNIX.

Since this script is written in python, you will need a python interpreter installed on your system. If you do not have one, you can get one from http://python.org/.
Getting Started

 1. Download archive
 2. Extract somewhere
 3. Open turbo_sort.py in a text editor
 4. Edit the variables at the top of the script per the README or see below for what the options do.
 5. Save & Run the script

Options to Consider:

+---------+
| General |
+---------+

tvdest
   TV shows will be moved to tvdest/undated_fs or tvdest/dated_fs

   By default these locations are "tvdest\Show Name\Season #\Show Name S## E##.ext"
                              and "      ...       \Show Name Mar 03 2012.ext"

moviedest
   Movies will be moved to moviedest\movie_fs
   By default this location is "moviedest\Movie Name (Year).ext"

sourcedir
   the directory the script will search for files ending in an extension specified in extensions

extensions
   specify which extensions to match. ex. ["mkv", "avi", "myextension", "mp4"]

min_size
   Files below this size, in megabytes (MB) will be ignored

----------------------------------------------------------------------------------------

overwrite
   Set to True to overwrite files in the destination directory with ones from the source.

remove_CC
   Set to True to remove country codes such as US, UK, DE, NL, BR from filenames -- specified in COUNTRIES

verbose
   Set to True to get command line output

truncate
   Set to True to enable 80-char wide output truncation

notify
   Set to true to enable popup notifications instead of shell output. This option supersedes truncate and verbose.
   YOU MUST INSTALL PYNOTIFY TO USE THIS FUNCTION!! http://home.gna.org/py-notify/      

stay_open
   Set to True to keep the shell window open after script has finished execution

no_rename
   Set to True to disable the script from performing file operations (will only display output)

+----------------+
| Format Strings |
+----------------+
All format strings support:
   %t - Title of the movie or show
   %T - TITLE of the movie or show in caps

undated_fs
   Format string for shows without a date. Specific options include:
     %e  - Episode number
     %0e - Zero-padded episode number
     %s  - Season number
     %0s - Zero-padded season number
     
dated_fs
   Format string for shows with a date. Specific options include:
     %0m - Zero-padded month (e.g. 03)
     %m  - Month (e.g. 3)
     %fm - Month (e.g. March)
     %FM - MONTH (e.g. MARCH)
     %sm - Mon (e.g. Mar)
     %SM - MON (e.g. MAR)
     %0d - Zero-padded day
     %d  - Day
     %y  - Year (e.g. 2011)

movie_fs
   Format string for movies. Specific options include:
     %y  - Year (e.g. 2011)
     %q  - Quality (e.g. 1080p)

+----------+
| Examples |
+----------+
undated_fs:
    "%t/Season %s/%t S%0s E%0e"     - The Office/Season 6/The Office S06 E03.mkv
    "Shows/%T Season %s/%t S%s E%e" - Shows/THE OFFICE Season 6/The Office S6 E3.mkv

dated_fs:
    "%t/%t %sm %0d %y"      - The Daily Show/The Daily Show Mar 05 2012.mkv
    "%t/%y/%fm/%t %y-%m-%d" - The Daily Show/2012/March/The Daily Show 2012-3-5.mkv

movie_fs:
    "%t (%y)"  - Pulp Fiction (1994).mkv
    "%q/%t %y" - 1080p/Pulp Fiction 1994.mkv
    "%y/%t"    - 1994/Pulp Fiction.mkv