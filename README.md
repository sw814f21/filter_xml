# Smiley data handler

Will do the following
- Download the newest smiley XML from Fødevarestyrelsen
    - Alternatively use an input file using the `--file, -f` command line arg
- Convert the smiley XML to JSON
- Append data from [Virk](https://datacvr.virk.dk/data/)
    - By running each method prefixed by `append_` in class `filter_xml.cvr.CVRHandlerBase`
- Append smiley report data from [FindSmiley](https://www.findsmiley.dk/Sider/Forside.aspx) for each restaurant
    - By running each method prefixed by `append_` in class `filter_xml.cvr.FindSmileyHandler`
- Filter the resulting data
    - By running each method prefixed by `filter_` in class `filter_xml.filters.Filters`
- Dump the result to three files: `smiley_json_processed_insert.json`, `smiley_json_processed_update.json`, and `smiley_json_processed_delete.json`
    - Alternatively push it to the API using the `--push, -p` command line arg

Only valid companies are included. That is, only companies with a p-number.

Only industry codes `561010, 561020, 563000` are included (restaurants | pizzarias, ice cream, etc | cafes, pubs, etc).

## Configuration

First copy `config.sample.ini` to `config.ini`, then fill out the missing fields.

- `[cvr]`
    - `provider`, valid choices: `[ cvrapi | cvr_elastic | scrape ]`
        - `cvrapi`, request data from [cvrapi](https://cvrapi.dk/)
            - no limit, no delay
            - requires `[cvrapi]`
        - `cvr_elastic`, request data from [Virk CVR API](https://data.virk.dk/datakatalog/erhvervsstyrelsen/system-til-system-adgang-til-cvr-data)
            - no limit, no delay & able to fetch data in batches
            - requires `[cvr_elastic]`
        - `scrape`, scrape from [Virk CVR data](https://datacvr.virk.dk/data/)
            - 10s delay
- `[cvrapi]`
    - `api_key`, API key for [cvrapi](https://cvrapi.dk/)

## Running
To run
```shell
$ python run.py
```

### Arguments

```shell
$ python run.py --help
usage: run.py [-h] [--sample [SIZE]] [--no-scrape] [--push] [--file FILE]

optional arguments:
  -h, --help            show this help message and exit
  --sample [SIZE], -s [SIZE]
                        sample size, default: 0 (full run)
  --no-scrape, -ns      skip scraping during run
  --push, -p            push output to rust server
  --file FILE, -f FILE  file path for xml to use (default: get from fødevarestyrelsen)
```

#### --sample, -s
Takes one parameter, `SIZE`, as an `int`. How many rows to process. Defaults to `0`, i.e. process all rows.

#### --no-scrape, -ns
Takes no parameters. Skips scraping. Defaults to `False`, i.e. do scrape.

#### --push, -p
Takes no parameters. Save changes to database. Defaults to `False`, i.e. saves to json file.

#### --file, -p
Takes one parameter, `FILE`, as a `str`. Input file to use in place of retrieving the smiley XML from Fødevarestyrelsen. 
Defaults to `None`, i.e. retrieve smiley XML from Fødevarestyrelsen.

## Data structure

### Fresh XML download
```xml
<?xml version="1.0" encoding="utf-8"?>
<document>
    <row>
        <navnelbnr>81615</navnelbnr>
        <cvrnr>27539629</cvrnr>
        <pnr>1010232313</pnr>
        <region />
        <brancheKode>DD.56.10.99</brancheKode>
        <branche>Serveringsvirksomhed - Restauranter m.v.</branche>
        <virksomhedstype>Detail</virksomhedstype>
        <navn1>Pizza Chianti </navn1>
        <adresse1>Odensevej 82  A</adresse1>
        <postnr>5260</postnr>
        <By>Odense S</By>
        <seneste_kontrol>1</seneste_kontrol>
        <seneste_kontrol_dato>25-02-2021 00:00:00</seneste_kontrol_dato>
        <naestseneste_kontrol>1</naestseneste_kontrol>
        <naestseneste_kontrol_dato>23-09-2020 00:00:00</naestseneste_kontrol_dato>
        <tredjeseneste_kontrol>2</tredjeseneste_kontrol>
        <tredjeseneste_kontrol_dato>19-08-2020 00:00:00</tredjeseneste_kontrol_dato>
        <fjerdeseneste_kontrol>1</fjerdeseneste_kontrol>
        <fjerdeseneste_kontrol_dato>13-11-2019 00:00:00</fjerdeseneste_kontrol_dato>
        <URL>http://www.findsmiley.dk/da-DK/Searching/DetailsView.htm?virk=81615</URL>
        <reklame_beskyttelse>0</reklame_beskyttelse>
        <Elite_Smiley>0</Elite_Smiley>
        <Kaedenavn />
        <Geo_Lng>10.391894</Geo_Lng>
        <Geo_Lat>55.366916</Geo_Lat>
        <Pixibranche>Restauranter, pizzeriaer, kantiner m.m.</Pixibranche>
    </row>
    ...
</document>
```

### After JSON conversion, before further processing
```json
[
    {
        "By": "Odense S",
        "Elite_Smiley": "0",
        "Geo_Lat": 55.366916,
        "Geo_Lng": 10.391894,
        "Kaedenavn": null,
        "Pixibranche": "Restauranter, pizzeriaer, kantiner m.m.",
        "URL": "http://www.findsmiley.dk/da-DK/Searching/DetailsView.htm?virk=81615",
        "adresse1": "Odensevej 82  A",
        "branche": "Serveringsvirksomhed - Restauranter m.v.",
        "brancheKode": "DD.56.10.99",
        "cvrnr": "27539629",
        "fjerdeseneste_kontrol": 1,
        "fjerdeseneste_kontrol_dato": "13-11-2019 00:00:00",
        "naestseneste_kontrol": 1,
        "naestseneste_kontrol_dato": "23-09-2020 00:00:00",
        "navn1": "Pizza Chianti",
        "navnelbnr": "81615",
        "pnr": "1010232313",
        "postnr": "5260",
        "region": null,
        "reklame_beskyttelse": "0",
        "seneste_kontrol": 1,
        "seneste_kontrol_dato": "25-02-2021 00:00:00",
        "tredjeseneste_kontrol": 2,
        "tredjeseneste_kontrol_dato": "19-08-2020 00:00:00",
        "virksomhedstype": "Detail"
    },
    ...
]
```

### Final output
```json
[
    {
        "cvrnr": "27539629",
        "pnr": "1010232313",
        "region": null,
        "industry_code": "561010",
        "industry_text": "Restauranter",
        "start_date": "2003-12-01T00:00:00Z",
        "smiley_reports": [
            {
                "report_id": "Virk1864537",
                "smiley": 1,
                "date": "2021-02-25T00:00:00Z"
            },
            {
                "report_id": "Virk1811639",
                "smiley": 1,
                "date": "2020-09-23T00:00:00Z"
            },
            {
                "report_id": "Virk1794678",
                "smiley": 2,
                "date": "2020-08-19T00:00:00Z"
            },
            {
                "report_id": "Virk1697390",
                "smiley": 1,
                "date": "2019-11-13T00:00:00Z"
            }
        ],
        "city": "Odense S",
        "elite_smiley": "0",
        "geo_lat": 55.366916,
        "geo_lng": 10.391894,
        "franchise_name": null,
        "niche_industry": "Restauranter, pizzeriaer, kantiner m.m.",
        "url": "http://www.findsmiley.dk/da-DK/Searching/DetailsView.htm?virk=81615",
        "address": "Odensevej 82  A",
        "name": "Pizza Chianti",
        "name_seq_nr": "81615",
        "zip_code": "5260",
        "ad_protection": "0",
        "company_type": "Detail"
    },
    ...
]
```