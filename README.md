# Checklist REMOVE AFTER CHECKING 

Go through this checklist after creating your repository. It should only take a couple of minutes. If you encounter any issues, let someone from IT know.

### README
- [ ] Manually go through and edit the rest of the README.

### Dotfiles
- [ ] Add a `.gitignore` file.

### GitHub Settings
- [ ] Add a short description to the repository.
- [ ] Add a develop branch.
- [ ] Set develop branch as default branch.
- [ ] Enable all data services (read-only analysis, dependency graph, security alerts).
- [ ] Create branch protection rules for master:
  - [ ] Require pull request review before merging.
    - [ ] Require 2 reviews. (One for the code and testing (DevOps), and one for semantics)
    - [ ] Dismiss stale pull request approvals when new commits are pushed.
  - [ ] Require status checks before merging.
- [ ] Create branch protection rules for develop:
  - [ ] Require pull request review before merging.
    - [ ] Require 2 reviews. (One for the code and testing (DevOps), and one for semantics)
    - [ ] Dismiss stale pull request approvals when new commits are pushed.
  - [ ] Require status checks before merging.
- [ ] Add a .travis.yml file.
  - [ ] Add the codecov token to env variables.
- [ ] [OPTIONAL] Add a codecov.yml
- [ ] Enable the status checks for travis and codecov.

# PriceCypher Python SDK

Python wrapper around the different PriceCypher APIs.

## Usage
### Installation
TODO

### Dataset SDK
```python
from pricecypher import Datasets

datasets = Datasets(BEARER_TOKEN)

datasets.index()
datasets.get_meta(DATASET_ID)
datasets.get_scopes(DATASET_ID)
datasets.get_scope_values(DATASET_ID, SCOPE_ID)
datasets.get_transaction_summary(DATASET_ID)

columns = [
    {'name_dataset': 'cust_group', 'filter': ['Big', 'Small'], 'key': 'group'},
    {'representation': 'cost_price', 'aggregate': 'sum', 'key': 'cost_price'}
]
datasets.get_transactions(DATASET_ID, AGGREGATE, columns)
```

## Development

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. 

### Prerequisites
* Python >= 3.9

### Setup
The `endpoints` module models the different PriceCypher API endpoints. Each file represents a different API and the
contents of each file are structured into the different endpoints that are provided by the API.
Similarly, each file in the `models` module defines the models that are provided by the different APIs.

The SDK that this package provides is contained in the top-level package contents.

## Authors

* **Marijn van der Horst** - *Initial work*

See also the list of [contributors](https://github.com/marketredesign/pricecypher_python_api/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
