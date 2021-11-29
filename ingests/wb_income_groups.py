"""Imports World Bank income groups to Walden.

Example usage:

```
poetry run python -m ingests.wb_income_groups
```
"""
import tempfile
from datetime import datetime
import unicodedata

import pandas as pd
import click
from owid.walden import files, add_to_catalog


SOURCE_DATA_URL = "http://databank.worldbank.org/data/download/site-content/CLASS.xlsx"


def load_metadata_description():
    df_new = pd.read_excel(SOURCE_DATA_URL, sheet_name="Notes")
    s = "\n\n".join(df_new.dropna().Notes.tolist())
    return unicodedata.normalize("NFKD", s)


def create_metadata_dict():
    return {
        "namespace": "wb",
        "short_name": "wb_income",
        "name": "World Bank list of economies (June 2021)",
        "source_name": "World Bank",
        "url": "https://datahelpdesk.worldbank.org/knowledgebase/articles/906519-world-bank-country-and-lending-groups",
        "source_data_url": SOURCE_DATA_URL,
        "description": load_metadata_description(),
        "date_accessed": datetime.now().date().strftime("%Y-%m-%d"),
        "publication_year": 2021,
        "publication_date": "2021-07-01",
        "owid_data_url": "https://walden.nyc3.digitaloceanspaces.com/wb/2021-07-01/wb_income.xlsx",
        "file_extension": "xlsx",
        "license_name": "CC BY 4.0",
        "license_url": "https://www.worldbank.org/en/about/legal/terms-of-use-for-datasets",
    }


def check_date(metadata):
    s = "Income classifications set on 1 July 2021 remain in effect until 1 July 2022"
    if s not in metadata["description"]:
        raise ValueError(
            "Source data is no longer from 2021. Or something has changed in Notes sheet!"
        )


@click.command()
def main():
    metadata = create_metadata_dict()
    check_date(metadata)
    with tempfile.NamedTemporaryFile() as f:
        # fetch the file locally
        files.download(metadata["source_data_url"], f.name)
        # add it to walden, both locally, and to our remote file cache
        add_to_catalog(metadata, f.name, upload=True)


if __name__ == "__main__":
    main()
