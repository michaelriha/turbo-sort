#!/usr/bin/env python
#
# turbo_sort v2.2.4
# This program sorts downloaded TV show and movie files
# Copyright (C) 2012-2013 Michael Riha
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import re
import shutil
import string

# Edit these variables to your liking, make sure to use \\ for backslash or / for forward slash 
undated_fs = "%t\\Season %s\\%t S%0s E%0e"
dated_fs   = "%t\\%t %sm %0d %y"
movie_fs   = "%t (%y)"

tvdest     = "D:\\Videos\\TV"
moviedest  = "D:\\Videos\\Movies"
sourcedir  = "D:\\Downloads\\Usenet" 
extensions = ["mkv", "avi", "mp4", "ts"]
SATELLITES = ["srt", "srr"]
min_size   = 100   # in MB / Megabytes (Default: 100MB)

overwrite  = True  # Overwrite files at destination?          (Default: True)
remove_CC  = True  # Remove country codes from filename?      (Default: True)
verbose    = True  # Show output in command line interface?   (Default: True)
truncate   = True  # Truncate the output to 80 characters?    (Default: True)
satellites = True  # Move related files such as subtitles?    (Default: True)
cleanup    = True  # Cleanup after moving files?              (Default: True)
clean_mode = 2     # Cleanup mode 1 or 2.                     (Default: 1)
                   # 1 is "safe cleanup" 2 removes the whole directory after something is moved. 
notify     = False # Show popup notifications instead of CLI? (Default: False)
stay_open  = False # Keep window open after execution?        (Default: False)
no_rename  = False # Prevent file operations for testing?     (Default: False)
remove_src = True  # Allow sourcedir to be removed during cleanup? (Default: False)

# Don't change anything below unless you know what you're doing!
if notify:
    try:
        import pynotify
        pynotify.init('turbo_sort')
    except:
        notify = False
        print("\nYou must have the pynotify library installed to use popup notifications!\n")

min_size <<= 20
months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
months_short = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
quality_attributes = ["1080p", "720p", "480p", "xvid", "1080i", "1080"]
ignore_attributes = ["hdtv", "dts"]
consolesize = 80

#tvdest     = "D:\\Documents\\Scripts\\Script test files\\tvdest"
#moviedest  = "D:\\Documents\\Scripts\\Script test files\\moviedest"
#sourcedir  = "D:\\Documents\\Scripts\\Script test files\\sourcedir"

def cleanup(base, dest):
    """ Moves satellite files such as subtitles that are associated with base
        and stored in root to the correct dest. associated files that are not
        in SATELLITES will be deleted.
        base/dest: file paths
    """
    root = os.path.dirname(base) 
    base = os.path.basename(base[:base.rfind('.')]).lower()
    for f in os.listdir(root):
        if f.lower().startswith(base):
            f_ext = f[f.rfind('.')+1:]
            if satellites and f_ext in SATELLITES:
                dest = dest[:dest.rfind('.')+1] + f_ext
                show("-->Satellite:", dest)
                rename(os.path.join(root, f), dest)
            elif cleanup and clean_mode == 1 and f_ext not in SATELLITES:
                if not no_rename:
                    os.remove(os.path.join(root, f))
                show("Removed:", f)

def cleanup_brute():
    """ Use the "bruteforce cleanup" approach to remove directories that were modified
        Remove all folders that were modified by the script that do not contain "important" files
        (important = matching extension and size >= min_size)
    """
    for dir in dir_cleanup_queue:
        if os.path.exists(dir):
            delete = True
            for root, dirs, files in os.walk(dir):
                for f in files:
                    if f[f.rfind('.')+1:] in extensions and os.path.getsize(os.path.join(root, f)) >= min_size:
                        delete = False
            if delete:
                try:
                    if not no_rename:
                        shutil.rmtree(dir)
                    show("Deleted:", dir)
                except Exception as e:
                    show("Failed to delete:", dir)
                    print(e)
            
def cleanup_safe():
    """ Use the "safe cleanup" approach to remove newly emptied directories
        Removes only files that have the same prefix as moved files
    """
    for dir in dir_cleanup_queue:
        if os.path.exists(dir) and not os.listdir(dir):
            try:
                shutil.rmtree(dir)
                show("Deleted:", dir)
            except Exception as e:
                show("Failed to delete:", dir)
                print(e)
                    
def finalize_fields():
    """ Perform a few functions so the formatter gets the right input """
    global special, title
    title = titler(title)
    special = titler(special)
    
def format_dated_show():
    """ Replaces dated show format string with available fields """
    index = 0
    final = ""
    for i in range(len(dateidx)):
        final  += dated_fs[index:dateidx[i]] # Append literal part between % signs 
        index   = dateidx[i]+1     # Index of format string variable
        fstemp  = dated_fs[index:] # Substring of fs starting right after a %, e.g. "t E%0e S%0s" from "%t E0e S%0s"
        index  += 1                # Move current position past first character of fstemp
        
        if fstemp[0] == '0':       # Month/day with leading 0
            if   fstemp[1] == 'm': final += zmonth
            elif fstemp[1] == 'd': final += zday
            index += 1
        elif fstemp[0] == 't': final += title # Show Name
        elif fstemp[0] == 'T': final += title.upper() # SHOW NAME
        elif fstemp[0] == 'm': final += month
        elif fstemp[0] == 'd': final += day
        elif fstemp[0] == 'y': final += year
        elif fstemp[0] == 'o': final += old_filename[:old_filename.rfind('.')]
        elif fstemp.startswith('fm'): # March
            final += fmonth
            index += 1
        elif fstemp.startswith('FM'): # MARCH
            final += fmonth.upper()
            index += 1
        elif fstemp.startswith('sm'): # Mar
            final += smonth
            index += 1
        elif fstemp.startswith('SM'): # MAR
            final += smonth.upper()
            index += 1
    final += dated_fs[index:] # Get the last bits of the format string
    return final

def format_show():
    """ Replaces regular show format string with available fields """
    index = 0
    final = ""
    for i in range(len(tvidx)):
        final  += undated_fs[index:tvidx[i]]        
        index   = tvidx[i]+1
        fstemp  = undated_fs[index:]
        index  += 1
        
        if fstemp[0] == '0':     # Season/episode with leading 0
            if   fstemp[1] == 'e': final += zepisode
            elif fstemp[1] == 's': final += zseason
            index += 1
        elif fstemp[0] == 'e': final += episode  
        elif fstemp[0] == 's': final += season
        elif fstemp[0] == 't': final += title
        elif fstemp[0] == 'T': final += title.upper()
        elif fstemp[0] == 'o': final += old_filename[:old_filename.rfind('.')]
    final += undated_fs[index:]
    return final
  
def format_movie():
    """ Replaces movie format string with available fields """
    index = 0
    final = ""
    
    # If the fs expects an element that wasn't found, just return the title... crappy input
    if "%y" in movie_fs and not year or "%q" in movie_fs and not quality:
        return title
    
    for i in range(len(movidx)):
        final  += movie_fs[index:movidx[i]]        
        index   = movidx[i]+1
        fstemp  = movie_fs[index:]
        index  += 1

        if   fstemp[0] == 't': final += title
        elif fstemp[0] == 'T': final += title.upper()
        elif fstemp[0] == 'y': final += year
        elif fstemp[0] == 'q': final += quality
        elif fstemp[0] == 'o': final += old_filename[:old_filename.rfind('.')]
    final += movie_fs[index:]
    return final

def index_fs(fs):
    """ Returns int[] with the indices of each % in the format string fs """
    indices = []
    i = 0
    for char in fs:
        if char == '%': indices.append(i)
        i += 1
    return indices

def populate_fields(filename):
    """ Parses the filename and populates the fields needed for renaming """
    global fmonth, smonth, zmonth, month, day, zday, year, quality, season, \
           zseason, episode, zepisode, title, type, extension, special
    
    # Get & Check extension first to speed up processing
    filename  = filename.lower()
    extension = filename[filename.rfind('.')+1:]
    if extension not in extensions: return False

    # remove scenegroup from scenegroup-movie.title.*
    hyph = string.find(filename, '-')
    if hyph < 10:
        filename = filename[hyph + 1:]
    
    # Initialize fields and split the filename by space, underscore, period, hyphen
    fmonth=smonth=zmonth=month=day=zday=year=quality=season=zseason=episode=zepisode=None
    title, special = [], []
    type  = "tv"
    elems = re.split('[ _.-]', filename) 
    
    # parse each filename element except the extension
    for elem in elems[0:-1]:
        # Check that the element is long enough to contain episode & season info
        if len(elem) > 2:
            
            # sanitize show.[*].* and show.(*).*
            if elem[0] == '[': 
                closeindex = string.rfind(elem, ']')
                elem       = elem[1:closeindex if closeindex != -1 else len(elem)]
            elif elem[0] == '(':
                closeindex = string.rfind(elem, ')')
                elem       = elem[1:closeindex if closeindex != -1 else len(elem)]
                
            # show.s01e01.* / show.s01e01e02.* TODO: Fix multiepisode w/ non-def fs here
            if elem[0] == 's' and elem[1].isdigit():
                temp     = elem[1:].split('e')
                zseason  = temp[0]
                zepisode = temp[1] if len(temp) == 2 else 'E'.join(temp[1:3])
                break
            
            # show.1x01.*
            if elem[1] == 'x':  
                zseason  = "0" + elem[0]
                zepisode = elem[2:4]
                break
            
            # show.01x01.*
            if elem[2] == 'x' and elem[3].isdigit():
                zseason  = elem[0:2]
                zepisode = elem[3:5]
                break            

            # Order of the above parse attempts does not matter, but those below do            
            # prevent title from elongating when no year/seas/ep found - assume movie
            if elem in quality_attributes:
                quality = elem
                type    = "movie"
                return True

            # found a year, so this is either a movie or dated show
            if elem[0:2] in ["19", "20"] and elem[2:4].isdigit():
                i       = elems.index(elem) + 1 # index of the next element
                zseason = ""        # (Probably) no season for this file
                elem    = elems[i]  # The new current element in the array
                year    = elems[i-1]
                
                # show.2009.s01e01.* break to format normal show
                if elem[0] == 's':
                    temp     = elem[1:].split('e')
                    zseason  = temp[0]
                    zepisode = temp[1] if len(temp) == 2 else 'E'.join(temp[1:3])
                    break
                
                # Movie without quality attributes
                if len(elems) == i + 1:
                    type = "movie"
                    return True
                
                # Get special attributes (e.g. multi, bluray, extended cut) and quality
                # also try to match movie based on movie.title.year.quality.* or
                #                         movie.title.year.something.here.quality.*
                special = []
                for j in range(i, len(elems) - 1):
                    if elems[j] in quality_attributes:
                        if len(elems[i]) > 2: # elem after year is not month/day
                            type    = "movie"
                            quality = elems[j]
                            return True
                        break
                    if not elems[j].isdigit() and elems[j] not in file_cleanup_queue:
                        special.append(elems[j])
                
                # show named using a date, assume show.year.month.day format
                zmonth = str(int(elem)-1)
                month  = zmonth[-1] if zmonth[0] == '0' else zmonth
                fmonth = months[int(elem)-1]
                smonth = months_short[int(elem)-1]
                zday   = elems[i+1]
                day    = zday[-1] if zday[0] == '0' else zday
                return True
            
            # show.0101.* / show.101.*
            if elem.isdigit():
                if len(elem) == 4:
                    zseason  = elem[0:2]
                    zepisode = elem[2:4]
                else:
                    zseason  = "0" + elem[0]
                    zepisode = elem[1:3]
                break

        # Determined this element to be part of the title so add it
        if elem not in file_cleanup_queue:
            title.append(elem)
        
    # All above breaks lead here when a show with season and episode is detected
    if zseason and zepisode:
        season  = zseason[-1]  if zseason[0]  == '0' else zseason
        episode = zepisode[-1] if zepisode[0] == '0' else zepisode
    else:
        type = "movie" # Show detected w/ episode and season, but no ep/s found so try movie
    return True

def rename(old, new):
    """ Handles special cases for moving the files to their sorted locations
        It creates any necessary directories to place the new file, moves it,
        and then removes the root directory the file was in unless it's sourcedir
    """
    if not no_rename:
        if os.path.exists(new):
            if overwrite:
                os.remove(new)
                shutil.move(old, new)
                show("Overwrote:", new)
            else:
                show("File already exists:", new_path)
        else:
            if not os.path.exists(os.path.dirname(new)):
                os.makedirs(os.path.dirname(new))
            shutil.move(old, new)
            show("Moved:", new_path)
        file_cleanup_queue.append([old, new])

sep = " ..."
offset = consolesize - len(sep)
def show(message, path):
    """ Resize each output line to be consolesize chars wide, OR show popup notification """
    if notify:
        notice = pynotify.Notification('turbo_sort', message + ' ' + path)
        notice.show()
    elif verbose:
        outputlength = len(message) + len(path)
        if truncate and outputlength >= consolesize:
            print(message + sep + path[outputlength - offset:])
        else:
            print(message + ' ' + path)

# Simple titlecase adapted from titlecase.py by Stuart Colville https://launchpad.net/titlecase.py
SMALL = ['a', 'an', 'and', 'as', 'at', 'but', 'by', 'for', 'if', 'in', 'of', 'on', 'or', 'the', 'to', 'v', 'via', 'vs', 'with']
COUNTRIES = ['us', 'uk', 'de', 'fr', 'nl', 'br']

def titler(title):
    """ Joins a string array and emulates titlecase returning the str result """
    result = ""
    if len(title) > 0: # First word always capital
        if title[0] == "its": # Fix "Its Always Sunny in Philadelphia"
            result += "It's "
        else:
            result += string.upper(title[0][0])
            result += title[0][1:]
            result += " "
        
    for word in title[1:]:
        if word in SMALL:
            result += word
            result += " "
        elif remove_CC and len(word) == 2 and word in COUNTRIES:
            continue
        else:
            result += string.upper(word[0])
            result += word[1:]
            result += " "
    return result[:-1]        
            
# Get the indices of the % in each format string for replacement
dateidx = index_fs(dated_fs)
tvidx   = index_fs(undated_fs)
movidx  = index_fs(movie_fs)

# Keep track of directories and files to potentially remove after initial renaming
dir_cleanup_queue = set()
file_cleanup_queue = list()

# Attempt to process all the files in sourcedir and its subdirectories
for root, dirs, files in os.walk(sourcedir):
    for old_filename in files:
        try:
            old_path = os.path.join(root, old_filename)
            if os.path.getsize(old_path) >= min_size and populate_fields(old_filename):
                finalize_fields()

                if root != sourcedir or remove_src:
                    dir_cleanup_queue.add(root)
                    
                new_path = os.path.join(moviedest, format_movie()) if type == "movie" \
                      else os.path.join(tvdest, format_show() if episode else format_dated_show())
                new_path += '.' + extension
                      
                rename(old_path, new_path)
                
        except WindowsError as e:
            show("Windows Error:", e.strerror)
            print(e)
        except Exception as e:
            show("*FAILED TO PROCESS*:", old_filename)
            print(e)
            
# Cleanup / handle satellites, then remove directories that are now empty
if cleanup or satellites:
    for q in file_cleanup_queue:
        try:
            cleanup(q[0], q[1])
        except:
            pass # sometimes gets files like *.*; easier to just skip when it happens
    if cleanup:
        if clean_mode == 1:
            cleanup_safe()
        elif clean_mode == 2:
            cleanup_brute()
            
if stay_open: raw_input("\nFiles processed successfully, press Enter to exit.")
