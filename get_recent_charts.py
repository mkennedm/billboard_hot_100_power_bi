import billboard
from datetime import datetime, timedelta
import csv
import re
import pandas as pd

# NOTE: 1958-08-04, the first date data is available, was a Monday
def most_recent_saturday():
    today = datetime.today()
    current_weekday = today.weekday()
    days_to_subtract = (current_weekday - 5) % 7
    most_recent_saturday = today - timedelta(days=days_to_subtract)
    return most_recent_saturday.strftime("%Y-%m-%d")

def get_prev_saturday(start_date=most_recent_saturday()):
    dt = datetime.strptime(start_date, '%Y-%m-%d')
    next_saturday = dt + timedelta(days=-7)
    return next_saturday.strftime("%Y-%m-%d")

# takes a song from ChartData and turns it into a dict
def song_to_dict(song, date_str, artist, collaborators):
    d = {'date': date_str, 'rank': song.rank,
         'song': song.title, 'artist': artist,
         'last-week': song.lastPos, 'peak-rank': song.peakPos,
         'weeks-on-board': song.weeks,
         'collaborators': ', '.join(collaborators)}
    return d

# special case for splitting rows where Lil Nas X is one of multiple artists
def lil_nas_x(s):
    return 'Lil Nas X' in s

def get_regex(artist):
    if lil_nas_x(artist):
        return r'(?:,|&)\s*|\b(?:With|Featuring|Feat\.|\+|/|featuring|x)\b'
    return r'(?:,|&|X)\s*|\b(?:With|Featuring|Feat\.|\+|/|featuring|x)\b'

def parens(s):
    return '(Feat' in s or '(feat' in s

def remove_parens(s):
    if parens(s):
        left = s.index('(')
        right = s.index(')')
        return ''.join([s[:left], s[left + 1:right]])
    return s

# takes a string containing multiple artists and returns a list of strings 
def split_artists(input_str):
    input_str = remove_parens(input_str)
    regex = get_regex(input_str)
    # Split the input string by the specified separators
    splits = re.split(regex, input_str)

    # Strip leading and trailing spaces from each string in the list
    artists = [s.strip() for s in splits if s.strip()]

    return artists

def create_new_csv(dest):
    columns = ['date', 'rank',
               'song', 'artist',
               'last-week', 'peak-rank',
               'weeks-on-board', 'collaborators']
    
    #start_date = most_recent_saturday()'
    start_date = '2018-10-20'
    
    # this is the latest saturday to occur before the beginning of
    # the charts on monday '1958-08-04'
    # set end date to 1958-07-26 (2 saturdays before august 4th) for full data
    #end_date = '1958-08-02'
    end_date = '1958-07-26'

    with open(dest, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        search_date = start_date
        
        while search_date != end_date:
            print(f'gathering data for week: {search_date}')
            chart = billboard.ChartData(name='hot-100', date=search_date)
            for song in chart:
                row = song_to_dict(song, chart.date, song.artist, [])
                writer.writerow(row)
            search_date = get_prev_saturday(search_date)
    return

def combine_CSVs(later_csv, earlier_csv, dest):
    df1 = pd.read_csv(later_csv, encoding = "utf-8")
    df2 = pd.read_csv(earlier_csv, encoding = "utf-8")
    combined_df = pd.concat([df1, df2], ignore_index=True)
    chunk_size = 1000
    num_rows = 0
    list_df = [combined_df[i:i+chunk_size]
               for i in range(0,len(combined_df),chunk_size)]
    
    for chunk in list_df:
        chunk.to_csv(dest, mode='a', header=(num_rows == 0), index=False)
        num_rows += min([chunk_size, len(chunk)])
        print(f'wrote {num_rows} rows')

def create_split_artists_csv(no_splits_csv):
    old_data_df = pd.read_csv(no_splits_csv)
    output_file = f'{no_splits_csv[:no_splits_csv.index(".csv")]}_split_artists.csv'

    new_df = pd.DataFrame(columns=old_data_df.columns)
    row_count = 0
    new_rows = []

    print('producing dataframe')
    for index, row in old_data_df.iterrows():
        artists = split_artists(row['artist'])
        num_artists = len(artists)

        if num_artists > 1:
            for i, artist in enumerate(artists):
                collaborators = ', '.join([a for a in artists if a != artist])
                new_row = row.copy()
                new_row['artist'] = artist
                new_row['collaborators'] = collaborators
                new_rows.append(new_row)
        else:
            new_rows.append(row)
                
        if index % 2000 == 0:
            print(f'finished row {index}')
            new_df = pd.concat([new_df, pd.DataFrame(new_rows)], ignore_index=True)
            new_rows = []

    print('producing new file')
    chunk_size = 2000
    row_count = 0
    list_df = [new_df[i:i+chunk_size]
               for i in range(0,len(new_df),chunk_size)]
    
    for chunk in list_df:
        chunk.to_csv(output_file, mode='a', header=(row_count == 0), index=False)
        row_count += min([chunk_size, len(chunk)])
        print(f'wrote {row_count} rows')
