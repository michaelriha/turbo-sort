You will need to open turbo_sort.py in a text editor and change the variables at the start of the document.

Below is a brief description of what each option does. After you've changed them to your preferences, simply run turbo_sort.py in your favorite python interpreter and watch the magic happen.

+---------+
| General |
+---------+
extensions
   specify what extensions to match. ex. ["mkv", "avi", "myextension", "mp4"]

sourcedir
   the directory the script will search for files ending in ext in

tvdest
   TV shows will be moved to "tvdest\Show Name\Season #\Show Name S0# E##.ext"
			  OR "tvdest\Show Name\Show Name March 13 2011.ext"    by default

moviedest
   Movies will be moved to "moviedest\Movie Name (Year).ext" by default

----------------------------------------------------------------------------------------

overwrite
   Set to True to overwrite files in the destination directory with ones from the source.

remove_US
   Set to True to remove (US) and US from filenames (does not work for other countries.. add it yourself)

debug
   Set to True to disable error handling (allow script to crash when it fails to parse)

no_rename
   Set to True to disable the script from performing file operations (will only display output)

verbose
   Set to True to get command line output

stay_open
   Set to True to keep the console open after script has finished execution

outputfull
   Set to True to disable 80-char wide output truncation

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
