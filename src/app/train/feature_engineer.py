import pandas as pd
import numpy as np


class FeatureEngineer:
    def __init__(self, df):
        self.df = df
    
    def create_features(self):
        self.df['total_purchases_per_day'] = self.df['total_purchases'] / self.df['days_since_registration']
        self.df["days_between_first_and_last_purchase"] = self.df["days_since_registration"] - self.df["last_purchase_days"]
        self.df["bucket_avg_order_value"] = pd.cut(self.df["avg_order_value"], bins=3, labels=["low", "medium", "high"])
        self.df["PRUEBA"] = 1
        return self.df