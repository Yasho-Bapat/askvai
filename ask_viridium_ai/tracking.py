import pandas as pd

class Logger:
    def __init__(self):
        """Initialize the Logger class."""
        self.columns = [
            'time', 'user_id', 'material_name',
            'tokens_used_for_chemical_composition', 'cost_chemical_composition',
            'tokens_used_for_analysis', 'cost_analysis', 'total_cost', 'chemical_composition', 'PFAS_status'
        ]
        self.df = pd.DataFrame(columns=self.columns)

    def log(self, info):
        """Log information provided in the 'info' dictionary.

        Args:
            info (dict): A dictionary containing information to log.
        """
        tdf = pd.DataFrame(info, index=[0])
        self.df = pd.concat([self.df, tdf])

    def experiment_log(self, info):
        tdf = pd.DataFrame(info, index=[0])

        self.df = pd.concat([self.df, tdf])

    def save(self, filename):
        # tdf = pd.read_csv(filename)
        # self.df = pd.concat([tdf, self.df])
        self.df.to_csv(filename, index=False)

class ExperimentLogger():
    def __init__(self):
        self.columns = ["material_id", "material_name", "manufacturer_id", "manufacturer_name", "pfas_status"]
        self.df = pd.DataFrame(columns=self.columns)
        self.logger = Logger()

    def log(self, info):
        tdf = pd.DataFrame(info, index=[0])
        self.df = pd.concat([self.df, tdf])

    def save(self, filename):
        tdf = pd.read_csv(filename)
        self.df = pd.concat([tdf, self.df])
        self.df.to_csv(filename, index=False) # saving