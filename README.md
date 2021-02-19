# Smiley data handler

To run
```python
from data_handler import DataHandler

handler = DataHandler()
handler.collect()
```

Will do the following
- Download the newest smiley XML from Fødevarestyrelsen
- Convert the smiley XML to JSON
- Append data from [Virk](https://datacvr.virk.dk/data/)
    - By running each method prefixed by `append_` in class `DataHandler`
- Filter the resulting data
    - By running each method prefixed by `filter_` in class `DataHandler`
- Dump the result to `smiley_json_processed.json`

## TODO
Method for extracting a sample 

## Notes

Only companies with a p-number is included.

Start date and *actual* industry code (fødevarestyrelsen's data is scuffed) is scraped from virk.dk.
Only industry codes `561010, 561020, 563000` are included (restaurants | pizzarias, ice cream, etc | cafes, pubs, etc).

A company may not exist anymore - this can possibly be handled by excluding companies that have not received smiley control within the last year.

