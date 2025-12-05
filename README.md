# BehToBids
-----------
Just a very simple helper to make annoying behavioral data BIDS compliant.

- It creates a BIDS folders structure for behavioral datasets
- It creates templates for metadata (e.g. json sidecars)
- It allows to convert tabular non-bids-compliant data to compliant .tsv files 
- It can be used to create `beh` or `events` type of files.

   ```
    rawdata
    ├── CHANGES
    ├── CITATION.cff
    ├── dataset_description.json
    ├── LICENSE
    ├── participants.json
    ├── participants.tsv
    ├── README
    ├── sub-01
    │   └── beh
    │       ├── sub-01_task-posner_run-01_beh.tsv
    │       └── sub-01_task-posner_run-02_beh.tsv
    ├── sub-02
    │   └── beh
    │       ├── sub-02_task-posner_run-01_beh.tsv
    │       └── sub-02_task-posner_run-02_beh.tsv
    └── task-posner_beh.json
    ```



## Requirements
----------------

| Package  | Version  |
|----------|----------|
| numpy    | 2.3.5    |
| pandas   | 2.3.3    |
| scipy    | 1.16.3   |

Code was tested on Ubuntu 24.04 LTS

## Getting Started

### Provide data info about the data

Set up a dictionary (e.g. DATA_INFO in the example below) to provide  all necessary information for the data conversion: 

- `data`: `dict` a dictionary containing participants IDs (e.g. '01', '02'), potential session IDs ('e.g. 'predrug', 'postdrug') and data file names (with relative directories) in a list.
Participants IDs must be valid subject labels or indeces. They constitute keys of the nested dictionary, while data directories are must be provided in a list as values for each participant ID.
    ```
    DATA_INFO = {
            'data': {
                "01": [</data/run-1.csv>, </data/run-2.csv>, ...],
                "02": [</data/run-1.csv>, </data/run-2.csv>, ...]
            }
        }
    ```
    In case of multiple sessions, you can simply add another nested dictionary for each participant, as in the following example, where session labels or indeces are the keys of the dictionary and :
        ```
    DATA_INFO = {
            'data': {
                "01": {
                    'predrug': [</data/run-1.csv>, </data/run-2.csv>, ...],
                    'postdrug':  [</data/run-1.csv>, </data/run-2.csv>, ...]
                }
                "02": {
                    'predrug': [</data/run-1.csv>, </data/run-2.csv>, ...],
                    'postdrug':  [</data/run-1.csv>, </data/run-2.csv>, ...]
                }
            }
        }
    ```

- `datatype` : `str` indicates the kind of behavioral data you want to convert, it can be either 'beh' or 'events'
- `col_names` : `dict` | `None` (optional), keys are column names currently used in your data and values are bids compliant column names (they must  follow snake_case style). This optional dictionary is used to replace non-compliant column names with the BIDS compliant version.
- `task_label` : `str`, task label for the `task-<label>` entity as defined by BIDS
- `acq_label` : `str` | `None` (optional), acquisition label for `acq-<label>` entity as defined by BIDS
- `participants_columns` : `list` (optional), list of additional custom columns that you want to add to `participants.tsv`. By default the `participants.tsv` file comes with the columns: `participant_id`, `age`, `sex` and `handedness`.
- `inherit` : `bool`, (`True` by default) if `True` json sidecars are inhereted otherwise each files is provided with its own sidecar.
- `neuro_suffix` : `str` | `None` (optional) in case you want to convert `events` files, here you can provide the suffix of the neuroimaging directory where the data should be saved, mandatory when converting events

```
DATA_INFO = {
            "bids_dir": "rawdata",
            "data": {
                    '01': {
                        'predrug': [</data/run-1.csv>, </data/run-2.csv>, ...],
                        'postdrug': [</data/run-1.csv>, </data/run-2.csv>, ...],
                        },
                    '02': {
                        'predrug': [</data/run-1.csv>, </data/run-2.csv>, ...],
                        'postdrug': [</data/run-1.csv>, </data/run-2.csv>, ...],
                        },
                    ...
                    },
            "col_names": {
                "Condition name": "trial_type",
                "Some COLUMN name": "some_column_name",
                ...
            },
            "datatype": "beh",
            "task_label": "task name",
            "acq_label": None,
            "participants_columns": None,
            "inherit": True,
            "neuro_suffix": None,
            }
```

Provide the dataset info

```
B = BehToBids(DATA_INFO)
```

### BIDS scaffolding

Create a bids directories and metadata templates

```
B.create_bids_struct()
```

### Convert the data

Now make the data hopefully BIDS compliant

```
B.convert()
```

Now carefully fill in the metadata and run the bids validator