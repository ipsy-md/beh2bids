from pathlib import Path
import json
import warnings

import metadata_templates as metadata

import pandas as pd
from scipy.io import loadmat


class BehToBids:
    """
    Converts Behavioral data
    to BIDS format, right now it accepts only
    tabular data such as .txt, .csv
    and .txt and .mat files as long as
    they are not nested

    Parameters
    ----------
    data : dict
        bids_dir : str, bids data directory
        data : dict, a dictionary containing as
               keys the subject ID meant to create the
               sub-<label> entity and list of data as values.
               Sessions must be a dictionary of each subject ID
               and must contain as keys the session labels and
               as values a list of data per session key
        col_names : dict | None (optional), keys are original column
                    names and values are bids compliant
                    column names (snake_case)
        datatype : str, 'beh' or 'events'
        task_label : str, task label for
                    the task-<label> entity
                    as defined by BIDS
        acq_label : str | None (optional), acquisition label
                   for acq-<label> entity as
                   defined by BIDS
        participants_columns : list (optional), list of
                    custom columns
        inherit : bool, True by default, if True json sidecars
                  are inhereted otherwise
                  each files is provided with its
                  sidecar
        neuro_suffix : str | None (optional) in case of events
                       conversion, it indicates the
                       suffix of the neuroimaging
                       recording, mandatory when
                       converting events

    Example:

    INFO: {
            "bids_dir": "rawdata",
            "data": {
                    01: {
                        'predrug': [data],
                        'postdrug': [data]
                        },
                    02: {
                        'predrug': [data],
                        'postdrug': [data]
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
    """

    def __init__(self, data):
        self.data = data
        # Set optional keys to None or default values
        self.data["col_names"] = None
        self.data["acq_label"] = None
        self.data["participants_columns"] = None
        self.data["inherit"] = True
        self.data["neuro_suffix"] = None

    def _check_labels(self, labels):
        """
        Check whether labels are
        alphanumeric and are all different
        Parameters
        ----------

        labels : list or tuple of strings

        Returns
        -------

        valid : boolean
        """
        valid = True
        for n, i in enumerate(labels):
            if not i.isalnum():
                valid = False
            for j in labels[n + 1 :]:
                if i.lower() == j.lower():
                    valid = False
        return valid

    def is_info_valid(self):
        """
        Check whether provided inputs
        are BIDS compliant
        """
        sub_labels = list(self.data["data"].keys())
        assert self._check_labels(
            sub_labels
        ), "subject labels must be all different and alphanumeric"

        if isinstance(list(self.data["data"].values())[0], dict):
            ses_labels = {
                label for ses in self.data["data"].values() for label in ses.keys()
            }
            assert self._check_labels(
                list(ses_labels)
            ), "sessions labels must be all different and alphanumeric"

    def create_bids_struct(self):
        """
        Create a bids boilerplate
        """
        # check inputs validity
        self.is_info_valid()
        # create root directory
        if not Path(self.data["bids_dir"]).exists():
            Path(self.data["bids_dir"]).mkdir()

        subjects_list = []
        for sub, val in self.data["data"].items():
            subjects_list.append(f"sub-{sub}")
            ## create sub dir
            if isinstance(val, dict):
                ## create ses dir and and beh dir
                for ses in val.keys():
                    data_out = (
                        Path(self.data["bids_dir"])
                        / Path(f"sub-{sub}")
                        / Path(f"ses-{ses}")
                        / "beh"
                    )
                    data_out.mkdir(parents=True, exist_ok=True)
            else:
                # create beh dir
                data_out = Path(self.data["bids_dir"]) / Path(f"sub-{sub}") / "beh"
                data_out.mkdir(parents=True, exist_ok=True)

        # create metadata files
        metadata.create_participants(
            self.data["bids_dir"], subjects_list, self.data["participants_columns"]
        )
        metadata.create_dataset_description(self.data["bids_dir"])
        metadata.root_metadata(self.data["bids_dir"])

    def _data2df(self, data):
        """
        Reads data, either .csv or simple .mat files.
        Parameters
        ----------
        data : .csv | .mat files, for now .mat
               cannot be complicated nested files

        Returns
        -------
        df : pandas DataFrame with columns derived by
             the original files
        """
        try:
            df = pd.read_csv(data, index_col=False, sep="\t")
        except:
            print("no .csv file found")
            try:
                df = pd.DataFrame(loadmat(data))
            except:
                pass
        return df

    def _to_bids(self, df, col_names=None):
        """
        Rename original columns in bids compliant column names,
        make column names lower capital
        TODO: check whether onsets and duration are in seconds

        Parameters
        ----------
        df : pandas DataFrame with data
        col_names : None | dict, with original names as keys and
                    bids compliant names as values
        Returns
        -------
        df : pandas DataFrame, with correct column names
        """
        if col_names:
            df = df.rename(columns=col_names)
        df = df.rename(columns={i: i.lower() for i in df.columns})
        if "Unnamed: 0" in df.columns:
            df = df.drop(["Unnamed: 0"], axis=1)
        df = df.fillna("n/a")
        return df

    def _get_file_names(self, sub, session, run, task_label, acq_label, datatype):
        """
        Create all the necessary filename
        and directory names
        """
        if self.data["datatype"] == "events":
            basedir = (
                Path(self.data["bids_dir"])
                / Path(f"sub-{sub}")
                / self.data["neuro_suffix"]
            )
            if session:
                basedir = (
                    Path(self.data["bids_dir"])
                    / Path(f"sub-{sub}")
                    / Path(f"ses-{session}")
                    / self.data["neuro_suffix"]
                )
        else:
            basedir = Path(self.data["bids_dir"]) / Path(f"sub-{sub}") / "beh"
            if session:
                basedir = (
                    Path(self.data["bids_dir"])
                    / Path(f"sub-{sub}")
                    / Path(f"ses-{session}")
                    / "beh"
                )
        file_dict = {"ses": session, "task": task_label, "acq": acq_label, "run": run}
        filename = f"sub-{sub}"
        for key, val in file_dict.items():
            if val is not None:
                filename = f"{filename}_{key}-{val}"
        filename = f"{filename}_{datatype}"
        return filename, basedir

    def convert(self):
        """
        The actual data conversion
        """
        for sub, val in self.data["data"].items():
            if isinstance(val, dict):
                for ses in val.keys():
                    for run, data in enumerate(val[ses]):
                        if len(val) == 1:
                            run_index = None
                        else:
                            run_index = run + 1
                        filename, basedir = self._get_file_names(
                            sub,
                            ses,
                            run_index,
                            self.data["task_label"],
                            self.data["acq_label"],
                            self.data["datatype"],
                        )
                        df = self._to_bids(self._data2df(data), self.data["col_names"])
                        df.to_csv(basedir / f"{filename}.tsv", index=False)
                        metadata._create_sidecar(
                            df,
                            self.data["inherit"],
                            self.data["task_label"],
                            basedir / f"{filename}",
                            self.data["bids_dir"],
                        )
            else:
                for run, data in enumerate(val):
                    if len(val) == 1:
                        run_index = None
                    else:
                        run_index = run + 1
                    filename, basedir = self._get_file_names(
                        sub,
                        None,
                        run_index,
                        self.data["task_label"],
                        self.data["acq_label"],
                        self.data["datatype"],
                    )
                    df = self._to_bids(self._data2df(data), self.data["col_names"])
                    df.to_csv(basedir / f"{filename}.tsv", index=False)
                    metadata._create_sidecar(
                        df,
                        self.data["inherit"],
                        self.data["task_label"],
                        basedir / f"{filename}",
                        self.data["bids_dir"],
                    )
