#!/usr/bin/env python
#
# turbo_sort v2.2
# This program sorts downloaded TV show and movie files
# Copyright (C) 2012 Michael Riha
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
extensions = ["mkv", "avi", "mp4"]

overwrite  = True  # Overwrite files at destination?          (Default: True)
remove_CC  = True  # Remove country codes from filename ?     (Default: True)
verbose    = True  # Verbose or silent output?                (Default: True)
truncate   = True  # Truncate the output to 80 characters?    (Default: True)
notify     = False # Show popup notifications instead of CLI? (Default: False)
stay_open  = False # Keep window open after execution?        (Default: False)
no_rename  = False # Prevent file operations for testing?     (Default: False)

if notify:
    import pynotify
    pynotify.init('turbo_sort')

# Don't change anything below unless you know what you're doing!
months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
months_short = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
quality_attributes = ["1080p", "720p", "xvid"]

# Simple titlecase adapted from titlecase.py by Stuart Colville
# https://launchpad.net/titlecase.py
# Using below regex is faster for LARGE batch processing, but slower for smaller batch
#SMALL = 'a|an|and|as|at|but|by|for|if|in|of|on|or|the|to|v\.|via|vs\.|with'
#SMALL_WORDS = re.compile(r'^(%s)$' % SMALL, re.I)
SMALL = ['a', 'an', 'and', 'as', 'at', 'but', 'by', 'for', 'if', 'in', 'of', 'on', 'or', 'the', 'to', 'v\.', 'via', 'vs\.', 'with']
COUNTRIES = ['us', 'uk', 'de', 'fr', 'nl', 'br']

def titler(title):
    """ Joins a string array and emulates titlecase returning the str result """
    joiner = []
    if len(title) > 0: # First word always capital
        if title[0] == "its": # Fix "Its Always Sunny in Philadelphia"
            joiner.append("It's")
        else: 
            joiner.append(chr(ord(title[0][0]) - 32) + title[0][1:]) 
        
    for word in title[1:]:
        #if SMALL_WORDS.search(word): for use with SMALL_WORDS regex
        if word in SMALL:
            joiner.append(word)
        elif remove_CC and len(word) == 2 and word in COUNTRIES:
            continue
        else:
            joiner.append(chr(ord(word[0]) - 32) + word[1:])
    return ' '.join(joiner)

def display_output(message, path):
    """ Resize each output line to be 80 chars wide, OR display popup notification """
    outputlength = len(message) + len(path) + 1
    if notify:
        notice = pynotify.Notification('turbo_sort', message + ' ' + path)
        notice.show()
    else:
        if truncate and outputlength > 80:
            print message + " ..." + path[outputlength - 76 % outputlength:]
        else:
            print message, path
        
def index_fs(fs):
    """ Populates indices[] with the index of each % in the format string and returns it """
    indices = []
    i = 0
    for char in fs:
        if char == '%': indices.append(i)
        i += 1
    return indices

def format_dated_show():
    """ Replaces dated show format string with available fields """
    index = 0
    final = []
    for i in range(len(dateidx)):
        final.append(dated_fs[index:dateidx[i]]) # Append literal part between % signs
        
        index   = dateidx[i]+1     # Index of format string variable
        fstemp  = dated_fs[index:] # Substring of fs starting right after a %, e.g. "t E%0e S%0s" from "%t E0e S%0s"
        index  += 1                # Move current position past first character of fstemp
        
        if fstemp[0] == '0':       # Month/day with leading 0
            if   fstemp[1] == 'm': final.append(zmonth)
            elif fstemp[1] == 'd': final.append(zday)
            index += 1
        elif fstemp[0] == 't': final.append(title) # Show Name
        elif fstemp[0] == 'T': final.append(title.upper()) # SHOW NAME
        elif fstemp[0] == 'm': final.append(month)
        elif fstemp[0] == 'd': final.append(day)
        elif fstemp[0] == 'y': final.append(year)
        elif fstemp.startswith('fm'): # March
            final.append(fmonth)
            index += 1
        elif fstemp.startswith('FM'): # MARCH
            final.append(fmonth.upper())
            index += 1
        elif fstemp.startswith('sm'): # Mar
            final.append(smonth)
            index += 1
        elif fstemp.startswith('SM'): # MAR
            final.append(smonth.upper())
            index += 1
    final.append(dated_fs[index:]) # Get the last bits of the format string
    return ''.join(final)

def format_show():
    """ Replaces regular show format string with available fields """
    index = 0
    final = []
    for i in range(len(tvidx)):
        final.append(undated_fs[index:tvidx[i]])
        
        index   = tvidx[i]+1
        fstemp  = undated_fs[index:]
        index  += 1
        
        if fstemp[0] == '0':     # Season/episode with leading 0
            if   fstemp[1] == 'e': final.append(zepisode)
            elif fstemp[1] == 's': final.append(zseason)
            index += 1
        elif fstemp[0] == 'e': final.append(episode)        
        elif fstemp[0] == 's': final.append(season)
        elif fstemp[0] == 't': final.append(title)
        elif fstemp[0] == 'T': final.append(title.upper())
    final.append(undated_fs[index:])
    return ''.join(final)
  
def format_movie():
    """ Replaces movie format string with available fields """
    index = 0
    final = []

    # If the fs expects an element that wasn't found, just return the title... crappy input
    if "%y" in movie_fs and not year or "%q" in movie_fs and not quality:
        return title
    
    for i in range(len(movidx)):
        final.append(movie_fs[index:movidx[i]])
        
        index   = movidx[i]+1
        fstemp  = movie_fs[index:]
        index  += 1

        if   fstemp[0] == 't': final.append(title)
        elif fstemp[0] == 'T': final.append(title.upper())
        elif fstemp[0] == 'y': final.append(year)
        elif fstemp[0] == 'q': final.append(quality)
    final.append(movie_fs[index:])
    return ''.join(final)

def populate_fields(filename):
    """ Parses the filename and populates the fields needed for renaming """
    global fmonth, smonth, zmonth, month, day, zday, year, quality, season, \
           zseason, episode, zepisode, title, type, extension
    
    # Get & Check extension first to speed up processing
    filename  = filename.lower()
    extension = filename[filename.rindex('.')+1:]
    if extension not in extensions: return -1
    
    # Initialize fields and split the filename by space, underscore, period, hyphen
    fmonth=smonth=zmonth=month=day=zday=year=quality=season=zseason=episode=zepisode=None
    title = []
    type  = "tv"
    elems = re.split('[ _.-]', filename) 
    
    # parse each filename element except the extension
    for elem in elems[0:-1]:
        # Check that the element is long enough to contain episode & season info
        if len(elem) > 2:
            
            # sanitize show.[*].*
            if elem[0] == '[': 
                closeindex = string.rfind(elem, ']')
                elem = elem[1:closeindex if closeindex != -1 else len(elem)]

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
                type = "movie"
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
                
                # Fix for other quality attributes such as multi, bluray, or proper preceding 1080p, 720p, etc.
                if elems[i+1] in quality_attributes:
                    type    = "movie"
                    quality = elems[i+1]
                    return True

                # check for 720p/1080i/etc. to match movie based on movie.title.year.quality.*
                if elem in quality_attributes:
                    type    = "movie"
                    quality = elem
                    return True
                
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
        title.append(elem)
        
    # All above breaks lead here when a show with season and episode is detected
    if zseason and zepisode:
        season  = zseason[-1] if zseason[0] == '0' else zseason
        episode = zepisode[-1] if zepisode[0] == '0' else zepisode
    else:
        type = "movie" # Show detected w/ episode and season, but no ep/s found so try movie
    return True

def rename(root, old, new):
    """ Handles special cases for moving the files to their sorted locations
        Thanks to Saad Javed for fixing file permission issues, and a bug
        where the sourcedir was being removed if empty"""
    # -Creates the destination folder to move to if it doesn't exist
    # -Moves the file to the new location
    # -Removes the directory that old was in if it is empty and not sourcedir
    if not no_rename:
        if not os.path.exists(os.path.dirname(new)):
            os.makedirs(os.path.dirname(new))
        old = os.path.join(root, old)
        shutil.move(old, new)
        if (root != sourcedir and not os.listdir(root)):
            shutil.rmtree(root)

dateidx = index_fs(dated_fs)
tvidx   = index_fs(undated_fs)
movidx  = index_fs(movie_fs)

# Attempt to process all the files in sourcedir and its subdirectories
for root, dirs, files in os.walk(sourcedir):
    for old_filename in files:
        success = populate_fields(old_filename)
        if success == True:
            title = titler(title)
            if type == "movie":
                new_path = os.path.join(moviedest, format_movie())
            else:
                new_path = os.path.join(tvdest, format_show() if episode else format_dated_show())
            new_path = "%s.%s" % (new_path, extension)

            if os.path.exists(new_path):
                if overwrite:
                    os.remove(new_path)
                    rename(root, old_filename, new_path)
                    if verbose: display_output("Overwriting:", new_path)
                else: display_output("File already exists:", new_path)
            else:
                rename(root, old_filename, new_path)
                if verbose: display_output("Moved:", new_path)
        elif success == None:
            if verbose: display_output("Failed to process:", old_filename)
            
if stay_open: raw_input("\nFiles processed successfully, press Enter to exit.")
