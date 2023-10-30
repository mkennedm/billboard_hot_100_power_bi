import billboard
from datetime import datetime, timedelta
import csv
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
def song_to_dict(song, date_str, artist):
    d = {'date': date_str, 'rank': song.rank,
         'song': song.title, 'artist': artist,
         'last-week': song.lastPos, 'peak-rank': song.peakPos,
         'weeks-on-board': song.weeks}
    return d

def create_new_csv(dest):
    columns = ['date', 'rank',
               'song', 'artist',
               'last-week', 'peak-rank',
               'weeks-on-board']
    
    start_date = most_recent_saturday()'
    
    # this is the latest saturday to occur before the beginning of
    # the charts on monday '1958-08-04'
    # set end date to 1958-07-26 (2 saturdays before august 4th) for full data
    end_date = '1958-07-26'

    with open(dest, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        search_date = start_date
        
        while search_date != end_date:
            print(f'gathering data for week: {search_date}')
            chart = billboard.ChartData(name='hot-100', date=search_date)
            for song in chart:
                row = song_to_dict(song, chart.date, song.artist)
                writer.writerow(row)
            search_date = get_prev_saturday(search_date)
    return

def combine_CSVs(later_csv, earlier_csv, dest):
    df1 = pd.read_csv(later_csv, encoding='utf-8')
    df2 = pd.read_csv(earlier_csv, encoding='utf-8')
    combined_df = pd.concat([df1, df2], ignore_index=True)
    chunk_size = 1000
    num_rows = 0
    list_df = [combined_df[i:i+chunk_size]
               for i in range(0,len(combined_df),chunk_size)]
    
    for chunk in list_df:
        chunk.to_csv(dest, mode='a', header=(num_rows == 0), index=False)
        num_rows += min([chunk_size, len(chunk)])
        print(f'wrote {num_rows} rows')


    
