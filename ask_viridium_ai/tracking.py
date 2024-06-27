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
        time = info["time"]
        user_id = info["user_id"]
        material_name = info["material_name"]
        tokens_used_for_chemical_composition = info["tokens_used_for_chemical_composition"]
        cost_chemical_composition = info["cost_chemical_composition"]
        tokens_used_for_analysis = info["tokens_used_for_analysis"]
        cost_analysis = info["cost_analysis"]
        total_cost = info["total_cost"]
        chemical_composition = info["chemical_composition"]
        pfas = info["PFAS_status"]

        data = [time, user_id, material_name, tokens_used_for_chemical_composition, cost_chemical_composition,
                tokens_used_for_analysis, cost_analysis, total_cost, chemical_composition, pfas]
        tdf = pd.DataFrame(info, index=[0])
        self.df = pd.concat([self.df, tdf])

    def save(self):
        tdf = pd.read_csv("log.csv")
        self.df = pd.concat([tdf, self.df])
        self.df.to_csv('log.csv', index=False)
