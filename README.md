# BehToBids

## Requirements

Package         Version
--------------- -----------
numpy           2.3.5
pandas          2.3.3
scipy           1.16.3

## Set up an virtual environment

```
python3 -m venv env
. env/bin/activate
pip install numpy
pip install pandas
pip install scipy
```

## Getting Started

### Set up info about the data

Set up a main dictionary (e.g. DATA_INFO in the example below) to provide  all necessary information for the data conversion: 

- `data`: `dict` a nested dictionary containing subjects IDs (e.g. '01', '02'), potential session IDs ('e.g. 'predrug', 'postdrug') and data as file names (with relative directories) as lists.
- `datatype` : `str` indicates the kind of behavioral data you want to convert, it can be either 'beh' or 'events'
- `col_names` : `dict` | `None` (optional), keys are original column names and values are bids compliant column names (snake_case). It is needed to map the original column names into BIDS compliant column names
- `task_label` : `str`, task label for the `task-<label>` entity as defined by BIDS
- `acq_label` : `str` | `None` (optional), acquisition label for `acq-<label>` entity as defined by BIDS
- `participants_columns` : `list` (optional), list of custom extra columns for `participants.tsv`
- `inherit` : `bool`, (`True` by default) if `True` json sidecars are inhereted otherwise each files is provided with its sidecar
- `neuro_suffix` : `str` | `None` (optional) in case of events conversion, it indicates the suffix of the neuroimaging recording, mandatory when converting events

```
DATA_INFO = {
            "bids_dir": "rawdata",
            "data": {
                    '01': {
                        'predrug': [data1, data2, ...],
                        'postdrug': [data1, data2, ...],
                        },
                    '02': {
                        'predrug': [data1, data2, ...],
                        'postdrug': [data1, data2, ...],
                        },
                    ...
                    },
            "col_names": {
                "orignal Name": "new_bids_compliant_name",
                "Col Name": "col_name",
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

Create a bids directories and metadata boilerplates

```
B.create_bids_struct()
```

### Convert the data

Now convert your data

```
B.convert()
```