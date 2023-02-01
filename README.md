# PriceCypher Python SDK

Python wrapper around the different PriceCypher APIs.

## Usage
### Installation
Simply execute `pip install pricecypher-sdk`

### Dataset SDK
```python
import asyncio
from pricecypher import Datasets


async def handle_page(page, page_nr, last_page):
    """ This function will be called for each individual page of transactions that is received."""
    print(f'Handling page {page_nr}/{last_page}')
    print(f'Nr of transactions in page: {len(page)}')
    print(f'Handling page {page_nr}/{last_page} done')


async def main():
    async with Datasets(BEARER_TOKEN) as ds:
        # Specify desired columns to be requested for transactions 
        columns = [
            {'name_dataset': 'cust_group', 'filter': ['Big', 'Small'], 'key': 'group'},
            {'representation': 'cost_price', 'aggregate': 'sum', 'key': 'cost_price'}
        ]

        index = asyncio.create_task(ds.index())
        meta = asyncio.create_task(ds.get_meta(DATASET_ID))
        scopes = asyncio.create_task(ds.get_scopes(DATASET_ID))
        values = asyncio.create_task(ds.get_scope_values(DATASET_ID, SCOPE_ID))
        summary = asyncio.create_task(ds.get_transaction_summary(DATASET_ID))
        transactions = asyncio.create_task(ds.get_transactions(DATASET_ID, AGGREGATE, columns))

        print('datasets', await index)
        print('transactions', await transactions)
        print('meta', await meta)
        print('summary', await summary)
        print('scopes', await scopes)
        print('scope values', await values)

asyncio.run(main())
```

### Printing debug logs
By default, debug log messages are not printed. Debug logs can be enabled using the following.
```python
import logging

logging.basicConfig(level=logging.DEBUG)
```

### Contracts
The `Script`, `ScopeScript`, and `QualityTestScript` abstract classes can be extended with their abstract methods
implemented to create scripts usable in other services. 

The `ScopeScript` in particular is intended for scripts that calculate values of certain scopes for transactions. 

The `QualityTestScript` is intended for scripts that check the quality of a data intake and produce a standardized
output that can be visualized and/or used by other services.

See the documentation on the abstract functions for further specifics.

## Development

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. 

### Prerequisites
* Python >= 3.9

### Setup
The `endpoints` module models the different PriceCypher API endpoints. Each file represents a different API and the
contents of each file are structured into the different endpoints that are provided by the API.
Similarly, each file in the `models` module defines the models that are provided by the different APIs.

The SDK that this package provides is contained in the top-level package contents.

## Deployment
1. Execute `python -m build` to build the source archive and a built distribution.
2. Execute `python -m twine upload dist/*` to upload the package to PyPi.

### Snapshot
To deploy a snapshot release, follow the next steps instead.
1. Add `-pre` to the version in `setup.cfg`.
2. Execute `python -m build -C--global-option=egg_info -C--global-option=--tag-build=dev`.
3. Execute `python -m twine upload dist/*`.

## Authors

* **Marijn van der Horst** - *Initial work*
* **Pieter Voors** - *Contracts for Script and ScopeScript*

See also the list of [contributors](https://github.com/marketredesign/pricecypher_python_sdk/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
