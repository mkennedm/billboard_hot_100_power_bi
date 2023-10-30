# billboard_hot_100_power_bi

## Visualizations

This report contains data from the Billboard Hot 100 Chart from its beginning on August 4, 1958 to October 21, 2023. The report contains two pages.

The first page is Data by Year, which allows users to filter the data down to a specific year or range of years (ex: 2003 - 2008). Once a time period is selected, this page will display a list of all the artists who appeared on the chart within that time period and the number of times they appeared on the chart. There’s also a column chart of the top 5 artists.

![data_by_year](https://github.com/mkennedm/billboard_hot_100_power_bi/assets/8769212/85d819e1-7d8e-42bd-85ca-ca96395c8167)


The second page is Data by Artist which allows users to search for any artist that appeared on the chart from August 4, 1958 to October 21, 2023. Once an artist is selected, the page shows a table that includes the names of their songs and each song’s peak rank. There’s a card which displays the unique number of songs that made it to the #1 rank, and a column chart that shows the number of times the artist appeared on the chart each year.

![data_by_artist](https://github.com/mkennedm/billboard_hot_100_power_bi/assets/8769212/adebfb26-38b2-43ca-a67d-d7e4715bad7a)


## Data Collection

I started by writing the python file get_recent_charts.csv. The function create_new_csv produces a csv containing columns date, rank, song, artist, last-week, peak-rank, weeks-on-board, and collaborators. 100 rows are populated for each week starting with the most recent Saturday the function is run and works backward to August 4, 1958. This 1958 starting date was chosen because it is the beginning of the Hot 100 chart. It’s also, notably, a Monday. Beginning on January 6, 1962, the charts have Saturday dates.

This project relies on the billboard Python library function ChartData which takes in a chart name (“hot-100” in this case) and a date as a string (“2023-10-21” for example). It returns a ChartData object containing the relevant chart. If there was no chart released on the given day then the function returns the chart for the closest chart in the future. For example, if the input date is “2023-10-20” then the chart for “2023-10-21” will be returned.

Finally, I wanted to discuss the combine_CSVs function briefly. Gathering over 60 years worth of data takes over an hour for the code to execute. During development it was more efficient to work with portions of the data then combine them into one later on. This function made use of Pandas DataFrames for faster execution.

## Data Modeling

My data source was the file combined_1958_08_04_to_2023_10_21.csv. I used Power Query to make the report faster by dropping some unneeded columns.

I dropped the columns for “weeks-on-board”, “peak-rank”, and “last-week”. The only one of these that was used in any of the visualizations was “peak-rank”. I chose to remove it because it contained multiple peaks for songs that rose in the chart from one week to another. I only needed the highest of the peaks and knew I could get this same information by creating a new measure in the “rank” column.

The full set of Power Query steps can be found below.
```
let
    Source = Csv.Document(File.Contents("G:\My Drive\Career\data analyst projects\music charts\csv_file_that_should_be_used_in_pwer_bi\billboard_hot_100_1958_08_04_to_2023_10_21.csv"),[Delimiter=",", Columns=8, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"date", type date}, {"rank", Int64.Type}, {"song", type text}, {"artist", type text}, {"last-week", Int64.Type}, {"peak-rank", Int64.Type}, {"weeks-on-board", Int64.Type}}),
    #"Removed Columns" = Table.RemoveColumns(#"Changed Type",{"weeks-on-board", "peak-rank", "last-week", ""})
in
    #"Removed Columns"
```

I had to create two additional tables for the visualizations present in the report. The first was ArtistYearCount, which is used to calculate the number of times each artist appeared on the Billboard Chart each year. To make this table, I first had to add a Year column to charts_for_project with the following DAX expression: `Year = YEAR('charts_for_project'[date])`





Next, I was able to use this DAX expression to create the new table.
```
ArtistYearCount =
SUMMARIZE('charts_for_project', 'charts_for_project'[Year], 'charts_for_project'[artist], "Count", COUNTROWS('charts_for_project'))
```



Then I created an active many-to-many relationship between the ArtistsYearCount and charts_for_project table on the artist column in both tables.


The last table I created was UniqueSongs which is used to reduce the data from charts_for_project to just one row for each song and store the peak rank out of all the times the song appeared in the Hot 100. The DAX expression is below.

```
UniqueSongs =
SUMMARIZE(
    charts_for_project,
    charts_for_project[artist],
    charts_for_project[song]
)
```

Here, I also created an active many-to-many relationship between the UniqueSongs and charts_for_project_table on the artist column of both tables.


Then I added the column “peak”.

```
peak =
MINX(
    FILTER(
        charts_for_project,
        charts_for_project[artist] = UniqueSongs[artist] && charts_for_project[song] = UniqueSongs[song]
    ),
    charts_for_project[rank]
)
```

The Data by Artist page of the report contains a card that shows the number of songs a selected artist has that made it to a number 1 rank. This required the creation of an additional measure on the UniqueSongs table.

```
Number Ones Count =
CALCULATE(
    COUNTROWS(UniqueSongs),
    UniqueSongs[peak] = 1
)
```

Below is an image of the model view from Power BI desktop.



