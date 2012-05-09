# !/usr/bin/env python
#
# turbo_sort v2.1
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
import string

# Edit these variables to your liking, make sure to use \\ for backslash or / for forward slash 
undated_fs = "%t\\Season %s\\%t S%0s E%0e"
dated_fs   = "%t\\%t %sm %0d %y"
movie_fs   = "%t (%y)"

tvdest     = "D:\\Videos\\TV"
moviedest  = "D:\\Videos\\Movies"
sourcedir  = "D:\\Downloads\\Usenet"
extensions = ["mkv", "avi", "mp4"]

overwrite  = True  # Overwrite files at destination?      (Default: True)
remove_US  = True  # Remove US from e.g. The.Office.US.*? (Default: True)
debug      = False # Allow script to crash?               (Default: False)
no_rename  = False # Prevent file operations?             (Default: False)

verbose    = True  # Verbose or silent output?            (Default: True)
stay_open  = False # Keep window open after execution?    (Default: False)
outputfull = False # Display full or truncated names in output? (Default: False)

# Don't change anything below unless you know what you're doing!
months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
months_short = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
quality_attributes = ["1080p", "720p", "xvid"]

def display_output(message, path):
    """ Resize each output line item to be standard 80 characters wide """
    outputlength = len(message) + len(path)    
    if not outputfull and outputlength > 80:
        print message + " ..." + new[outputlength - 76 % outputlength:]
    else:
        print message, path
        
def index_fs(fs):
    """ Populates indices[] with the index of each % in the format string and returns it """
    indices = []
    i = 0
    for char in fs:
        if char == '%':
            indices.append(i)
        i += 1
    return indices
        
dateidx = index_fs(dated_fs)
tvidx   = index_fs(undated_fs)
movidx  = index_fs(movie_fs)

def format_dated_show():
    """ Replaces dated show format string with available fields """
    index = 0
    final = []
    for i in range(len(dateidx)):
        final.append(dated_fs[index:dateidx[i]]) # Append literal part between % signs
        
        index   = dateidx[i]+1     # Index of format string variable
        fstemp  = dated_fs[index:] # Substring of fs starting right after a %, e.g. "t E%0e S%0s" from "%t E0e S%0s"
        index  += 1                # Move current position past first character of fs substring
        
        if fstemp[0] == '0':       # Month/day with leading 0 (e.g. 03 or 12)
            if   fstemp[1] == 'm': final.append(zmonth)
            elif fstemp[1] == 'd': final.append(zday)
            index += 1
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
        elif fstemp[0] == 't': final.append(title) # Show Name
        elif fstemp[0] == 'T': final.append(title.upper()) # SHOW NAME
        elif fstemp[0] == 'm': final.append(month) # 03
        elif fstemp[0] == 'd': final.append(day)
        elif fstemp[0] == 'y': final.append(year) # 2010
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
        
        if fstemp[0] == '0':     # Season/episode with leading 0 (e.g. 06 or 13)
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
    global fmonth, smonth, zmonth, month, day, zday, year, quality, season, zseason, episode, zepisode, title, type, ext
    
    filename = filename.lower()

    ext = filename[filename.rindex('.')+1:]
    if ext not in extensions:  # Speed boost by checking extension first
        return None
    
    # Initialize fields
    fmonth=smonth=zmonth=month=day=zday=year=quality=season=zseason=episode=zepisode=None
    title = []
    type  = "tv"
    elems = re.split('[ _.-]', filename) # Split the filename by space, underscore, period, hyphen

    for elem in elems[0:-1]:        # parse each filename element except the extension
        if elem[0] == '[': # sanitize show.[*].*
            closeindex = string.find(elem, ']')
            if closeindex == -1: closeindex = len(elem)
            elem = elem[1:closeindex]
        if elem[0:3] not in ["198", "199", "200", "201", "202", "203"]: # check for year in range 1980-2039
            if elem[0] == 's' and elem[1].isdigit():
                temp     = elem[1:].split('e')
                zseason  = temp[0]  # show.s01e01.* / show.s01e01e02.*
                zepisode = temp[1] if len(temp) == 2 else 'E'.join(temp[1:3]) # [temp[1], temp[2]] possible way to fix multi episode?
                break
            elif len(elem) > 2:
                if elem[1] == 'x':  # show.1x01.*
                    zseason  = "0" + elem[0]
                    zepisode = elem[2:4]
                    break
                elif elem[2] == 'x' and elem[3].isdigit():
                    zseason  = elem[0:2]
                    zepisode = elem[3:5]
                    break           # show.01x01.*
                elif elem.isdigit():
                    if len(elem) == 4: # show.0101.*
                        zseason  = elem[0:2]
                        zepisode = elem[2:4]
                    else:           # show.101.*
                        zseason  = "0" + elem[0]
                        zepisode = elem[1:3]
                    break
            # prevent title from elongating when no year/seas/ep found - assume movie
            if elem in quality_attributes:
                quality = elem
                type = "movie"
                break
            title.append(elem)                
            
        # determine if it's movie, dated show, or a non-dated show with a year (e.g. Archer.2009.s02e03.*)
        else:                       
            i       = elems.index(elem) + 1
            zseason = ""        # (Probably) no season for this file
            cur     = elems[i]  # The current element in the array

            # Fix for other quality attributes such as multi, bluray, or proper preceding 1080p, 720p, etc.
            if elems[i+1] in quality_attributes:
                type    = "movie"
                title   = titler(title)
                year    = elems[i-1]
                quality = elems[i+1]
                return 1

            # check for 720p/1080i/etc. to match movie based on the.title.year.quality.*
            if cur in quality_attributes:
                type    = "movie"
                title   = titler(title)
                year    = elems[i-1]
                quality = cur
                return 1
            
            # show.2009.s01e01.* break to format normal show
            elif cur[0] == 's':
                temp     = cur[1:].split('e')
                zseason  = temp[0]
                zepisode = temp[1] if len(temp) == 2 else 'E'.join(temp[1:3])
                break
            
            # show named using a date, assume year.month.day format
            else:
                print elem
                title  = titler(title)
                year   = elems[i-1]
                zmonth = str(int(cur)-1)
                month  = zmonth[-1] if zmonth[0] == '0' else zmonth
                fmonth = months[int(cur)-1]
                smonth = months_short[int(cur)-1]
                zday   = elems[i+1]
                day    = zday[-1] if zday[0] == '0' else zday
                return 1
    # Show with season and episode detected
    title = titler(title)
    if zseason and zepisode:
        season  = zseason[-1] if zseason[0] == '0' else zseason
        episode = zepisode[-1] if zepisode[0] == '0' else zepisode
    else:
        type = "movie" # Show detected w/ episode and season, but no ep/s found so try movie
    return 1
    
def titler(title):
    """ Joins a string array and emulates titlecase returning the str result """
    title = string.capwords(' '.join(title))
    if remove_US: title = title.replace("Us", "").replace("(us)", "")
    return title.replace("In", "in").replace("And", "and").replace("Its", "It's").strip()

for root, dirs, files in os.walk(sourcedir):
    for old in files:
        # Debug mode allows script to crash
        if debug: new = populate_fields(old)
        else:
            try: new = populate_fields(old)
            except:
                if verbose: display_output("Failed to process ", old)
                
        # If file could be parsed, generate the new filename and rename it
        if new:
            if type == "movie":
                new = os.path.join(moviedest, format_movie())
            else:
                new = os.path.join(tvdest, format_show() if episode else format_dated_show())
            new = "%s.%s" % (new, ext)

            if os.path.exists(new):
                if overwrite:
                    if not no_rename:
                        os.remove(new)
                        os.renames(os.path.join(root, old), new)
                    if verbose: display_output("Overwriting", new)
                else: display_output("File already exists:", new)
            else:
                if not no_rename: os.renames(os.path.join(root, old), new)
                if verbose: display_output("Moved", new)
        
if stay_open: raw_input("\nFiles processed successfully, press Enter to exit.")
