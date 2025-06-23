from pathlib import Path
import json
import warnings

import metadata_templates as metadata

import yaml
import pandas as pd
from scipy.io import loadmat

class Beh2Bids:
    """
    Parameters
    ----------
    n_subjects : int, number of subjects
    n_sessions : int, optional number of sessions
    subjects : list | tuple (optional) of strings that specify
               the subject label. If not specified, it creates
               labels based on n_subjects (e.g. sub-01, sub-02 etc.)  
    dataset : str, optional, dataset name
    data_dir : Path | str output directory
    sessions : list | tuple, optional, of strings that specify sessions
               names, if not specified, it creates session names as
               'ses-01'.
    """
    def __init__(
            self,
            n_subjects,
            n_sessions=None,
            subjects=None, 
            sessions=None,
            dataset=None,
            participants_columns=None, 
            bids_dir="bids"
            ):
        self.n_subjects = n_subjects
        self.n_sessions = n_sessions
        self.dataset = dataset
        self.subjects = subjects
        self.sessions = sessions
        self.participants_columns = participants_columns
        self.bids_dir = bids_dir

    def save_json(self, data, filename):
        """
        Save json file
        """
        with open(f'{filename}.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    def _create_sessions(self):

        """
        """
        pass

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
            print("Trying to open a .csv file...")
            df = pd.read_csv(data)
        except:
            print('no .csv file found')
            try:
                print('Trying to get a .mat file...')
                df = pd.DataFrame(loadmat(data))
            except:
                pass
        return df

    def _to_bids(self, df, col_names=None):
        """
        Rename original columns in bids compliant column names
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
        print(df.columns)
        df = df.drop(columns=["Unnamed: 0"])
        return df

    def _create_sidecar(self, df, filename):
        """
        Create sidecars for _beh/_events files
        """
        json_dict = {col: None for col in df.columns}
        # Add template column text
        self.save_json(json_dict, filename)

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
            for j in labels[n+1:]:
                if i.lower() == j.lower():
                    valid = False
        return valid

    def is_info_valid(self):
        """
        Check whether provided inputs
        are valid
        """
        if self.subjects is not None:
            assert self._check_labels(self.subjects), \
                    "subject labels must be all different and alphanumeric"
            assert len(self.subjects) == self.n_subjects, \
                    "subject labels and number of subjects do not match"

        if self.sessions is not None:
            assert self._check_labels(self.sessions), \
                "sessions labels must be all different and alphanumeric"

    def create_bids_struct(self):
        """
        Create a bids boilerplate
        """
        # create root directory
        if not Path(self.bids_dir).exists():
            Path(self.bids_dir).mkdir()
        # create metadata files
        metadata.create_participants(
                self.bids_dir,
                self.n_subjects,
                self.subjects, 
                self.participants_columns
                )
        metadata.create_dataset_description(self.bids_dir)
        metadata.root_metadata(self.bids_dir)

        subjects_list = [
                f"sub-{sub+1:0{len(str(self.n_subjects))}}"
                for sub in range(self.n_subjects)
                ]
        if self.subjects is not None:
            subjects_list = self.subjects

        if self.sessions or self.n_sessions:
            sessions_list = [
                        f"ses-{ses+1:0{len(str(self.n_sessions))}}"
                        for ses in range(self.n_sessions)
                        ]
            if self.sessions is not None:
                sessions_list = self.sessions

            for sub in subjects_list:
                for ses in sessions_list:
                    data_out = Path(self.bids_dir) / Path(sub) / Path(ses) / "beh"
                    data_out.mkdir(parents=True, exist_ok=True)
        else:
            for sub in subjects_list:
                data_out = Path(self.bids_dir) / Path(sub) / "beh"
                data_out.mkdir(parents=True, exist_ok=True)

    def __call__(self, data):
        """
        """
        if data['datatype'] == "beh":
            suffix = "beh"
            # create a structure for bids
            self.create_bids_struct()
            # check columns
        elif data['datatype'] == "events":
            suffix = "events"
            if "onset" not in data or "duration" not in data:
                warnings.warn("You need the onset and duration columns for events, unless you have a resting state study")
        else:
            raise NameError(f"{data['datatype']} does not exist.\n You must select between 'beh' or 'events'")

        df = self._to_bids(
                self._data2df(data['datadir']),
                data['col_names']
                )
        if data['outdir'] is not None:
            basedir = f"{data['outdir']}"
        elif data['outdir'] is None and data["datatype"] == "events":
            raise ValueError("You should specify an output directory")
        else:
            basedir = Path(self.bids_dir) / Path(f"sub-{data['sub']}") / "beh"
            if data["session"]:
                basedir = (
                    Path(self.bids_dir) / Path(f"sub-{data['sub']}") / Path(f"ses-{data['session']}") / "beh"
                )

        if data['acq_label']:
            if data["session"]:
                filename = "_".join(
                    (
                        f"sub-{data['sub']}",
                        f"ses-{data['session']}",
                        f"task-{data['task_label']}",
                        f"acq-{data['acq_label']}",
                        f"run-{data['run']}",
                        f"{suffix}"
                        )
                    )
            else: 
                filename = "_".join(
                        (
                        f"sub-{data['sub']}",
                        f"task-{data['task_label']}",
                        f"acq-{data['acq_label']}",
                        f"run-{data['run']}",
                        f"{suffix}"
                        )
                    )
        else:
            if data["session"]:
                filename = "_".join(
                        (
                        f"sub-{data['sub']}",
                        f"ses-{data['session']}",
                        f"task-{data['task_label']}",
                        f"run-{data['run']}",
                        f"{suffix}"
                        )
                    )
            else:
                filename = "_".join(
                    (
                        f"sub-{data['sub']}",
                        f"task-{data['task_label']}",
                        f"run-{data['run']}",
                        f"{suffix}"
                        )
                    )

        df.to_csv(
            basedir / f"{filename}.tsv",
            sep='\t')
        self._create_sidecar(df, basedir / f"{filename}")