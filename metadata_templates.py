from pathlib import Path
import json

import pandas as pd


def save_json(data, filename):
    """
    Save json file
    """
    with open(f'{filename}.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def create_dataset_description(out_dir, dataset_name=None):
    """
    Create the dataset_description file
    """
    ds_descr = {}
    ds_descr["Name"] = dataset_name
    ds_descr["BIDSVersion"] = None
    ds_descr["DatasetType"] = None
    ds_descr["License"] = None
    ds_descr["Authors"] = []
    ds_descr["Acknowledgements"] = None
    ds_descr["HowToAcknowledge"] = None
    ds_descr["EthicsApprovals"] = []
    ds_descr["ReferencesAndLinks"] = []
    ds_descr["DatasetDOI"] = None
    ds_descr["HEDVersion"] = None
    ds_descr["Generated"] = [
                {
                "Name": None,
                "Version": None,
                        "Container": {
                        "Type": None,
                        "Tag": None
                        }
                }
            ]
    ds_descr["SourceDatasets"] = [
                {
                "URL": None,
                "Version": None
                }
            ]

    save_json(
            ds_descr,
            f"{out_dir}/dataset_description"
            )

def create_participants(
        out_dir, 
        n_subjects, 
        subjects=None,
        participants_columns=None
        ):
    """
    Create the participants.tsv table
    and the json sidecar
    """
    columns = ["participant_id", "age", "sex", "handedness"]
    if participants_columns is not None:
        columns = participants_columns

    part_dict = {
                col: [f"sub-{sub+1:0{len(str(n_subjects))}}"
                    for sub in range(n_subjects)
                    ]
                if col == "participant_id"
                else ['n/a'] * n_subjects
                for col in columns
                }

    if subjects is not None:
        part_dict = {
                col: subjects 
                if col == "participant_id"
                else ['n/a'] * len(subjects)
                for col in columns
                }

    pd.DataFrame(part_dict).to_csv(
            f"{out_dir}/participants.tsv",
            sep="\t",
            index=False
        )

    participants = {col: None for col in columns}
    participants["participant_id"] = {"Description": "Participant identifiers"}
    participants["age"] = {
            "Description": "age of the participant",
            "Units": "years"
            }
    participants["sex"] = {
            "Description": "sex of the participant as reported by the participant",
                "Levels": {
                    "M": "male",
                    "F": "female"
                    }
            }
    participants["handedness"] = {
            "Description": "handedness of the participant as reported by the participant",
                "Levels": {
                    "left": "left",
                    "right": "right"
                    }
            }
    save_json(participants, f"{out_dir}/participants")

def _create_sidecar(df, filename):
    """
    """
    """
    Create sidecars for _beh/_events files
    """
    json_dict = {col: None for col in df.columns}
    # Add template column text
    save_json(json_dict, filename)


def root_metadata(data_dir):
    """
    produce metadata for the whole
    dataset:
    - README
    - CITATION.cff
    - CHANGES
    - LICENSE
    """
    for f in ["README", "CITATION.cff", "CHANGES", "LICENSE"]:
        Path(f"{data_dir}/{f}").touch()
