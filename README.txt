You will need to open turbo_sort.py in a text editor and change the variables at the start of the document.

Below is a brief description of what each option does. After you've changed them to your preferences, simply run turbo_sort.py in your favorite python interpreter and watch the magic happen.

+---------+
| General |
+---------+

tvdest
   TV shows will be moved to "tvdest\Show Name\Season #\Show Name S0# E##.ext"
			  OR "tvdest\Show Name\Show Name March 13 2011.ext"    by default

moviedest
   Movies will be moved to "moviedest\Movie Name (Year).ext" by default

sourcedir
   the directory the script will search for files ending in ext in

extensions
   specify what extensions to match. ex. ["mkv", "avi", "myextension", "mp4"]

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
   Set to true to enable popup notifications instead of shell output. This option supersedes truncate.
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
