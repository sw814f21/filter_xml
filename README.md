# Smiley data handler

## Running
To run
```shell
$ python run.py
```

Will do the following
- Download the newest smiley XML from Fødevarestyrelsen
- Convert the smiley XML to JSON
- Append data from [Virk](https://datacvr.virk.dk/data/)
    - By running each method prefixed by `append_cvr_` in class `DataHandler`
- Append smiley report data from [FindSmiley](https://www.findsmiley.dk/Sider/Forside.aspx) for each restaurant
    - By running each method prefixed by `append_smiley_` in class `DataHandler`
- Filter the resulting data
    - By running each method prefixed by `filter_` in class `DataHandler`
- Dump the result to `smiley_json_processed.json`


### Arguments

```shell
$ python run.py --help
usage: run.py [-h] [--sample [SIZE]] [--no-scrape]

optional arguments:
  -h, --help            show this help message and exit
  --sample [SIZE], -s [SIZE]
                        sample size, default: 0 (full run)
  --no-scrape, -ns      skip scraping during run
```

#### --sample, -s
Takes one parameter, `SIZE`, as an `int`. How many rows to process.

#### --no-scrape, -ns
Takes no parameters. Skips scraping.

## Notes

Only companies with a p-number is included.

Start date and *actual* industry code (fødevarestyrelsen's data is scuffed) is scraped from virk.dk.
Only industry codes `561010, 561020, 563000` are included (restaurants | pizzarias, ice cream, etc | cafes, pubs, etc).

A company may not exist anymore - this can possibly be handled by excluding companies that have not received smiley control within the last year.

