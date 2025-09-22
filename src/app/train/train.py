from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.impute import SimpleImputer


class Train:
    def __init__(self, df, numeric_features, categorical_features, target_column, model, test_size=0.2):
        self.df = df
        self.numeric_features = numeric_features
        self.categorical_features = categorical_features
        self.target_column = target_column
        self.test_size = test_size
        self.model = model

    def train_test_split(self):
        X_train, X_test, y_train, y_test = train_test_split(self.df.drop(columns=[self.target_column]), self.df[self.target_column], test_size=self.test_size, random_state=42)
        return X_train, X_test, y_train, y_test
    
    def create_pipeline_numeric(self):
        numeric_transformer = Pipeline(steps=[('imputer', SimpleImputer(strategy='median')), ('scaler', StandardScaler())])
        return numeric_transformer
    
    def create_pipeline_categorical(self):
        categorical_transformer = Pipeline(steps=[('imputer', SimpleImputer(strategy='constant', fill_value='Unknown')), ('onehot', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'))])
        return categorical_transformer
    
    def create_preprocessor(self):
        preprocessor = ColumnTransformer(transformers=[('num', self.create_pipeline_numeric(), self.numeric_features), ('cat', self.create_pipeline_categorical(), self.categorical_features)])
        return preprocessor

    def create_pipeline_train(self):
        pipeline = Pipeline(steps=[('preprocessor', self.create_preprocessor()), ('classifier', self.model)])
        return pipeline

    def train(self):
        X_train, X_test, y_train, y_test = self.train_test_split()
        pipeline = self.create_pipeline_train()
        pipeline.fit(X_train, y_train)
        return pipeline