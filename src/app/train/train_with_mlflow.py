from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.impute import SimpleImputer
import mlflow
import mlflow.sklearn
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score
)
import warnings
warnings.filterwarnings('ignore')


class TrainMlflow:
    def __init__(
        self, df, numeric_features, categorical_features, 
        target_column, model, 
        test_size=0.2, model_params=None, mlflow_setup=None
    ):
        """
        Initialize the Train class with MLflow tracking capabilities.

        Args:
            df: Input dataframe
            numeric_features: List of numeric feature column names
            categorical_features: List of categorical feature column names
            target_column: Name of target column
            model: Model instance to train
            model_params: Dictionary of model parameters (optional)
            experiment_name: Name for MLflow experiment
            test_size: Proportion of data to use for testing
        """
        self.df = df
        self.numeric_features = numeric_features
        self.categorical_features = categorical_features
        self.target_column = target_column
        self.test_size = test_size
        self.model = model
        self.model_params = model_params if model_params is not None else {}

        # Set up MLflow tracking
        self.setup = mlflow_setup
        

    def train_test_split(self):
        X = self.df.drop(columns=[self.target_column])
        y = self.df[self.target_column]
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_size, random_state=42
        )
        return X_train, X_test, y_train, y_test

    def create_pipeline_numeric(self):
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')), 
            ('scaler', StandardScaler())
        ])
        return numeric_transformer

    def create_pipeline_categorical(self):
        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(
                strategy='constant', fill_value='Unknown'
            )),
            ('onehot', OneHotEncoder(
                drop='first', 
                sparse_output=False, 
                handle_unknown='ignore'
            ))
        ])
        return categorical_transformer

    def create_preprocessor(self):
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', self.create_pipeline_numeric(), 
                 self.numeric_features),
                ('cat', self.create_pipeline_categorical(), 
                 self.categorical_features)
            ]
        )
        return preprocessor

    def create_pipeline_train(self):
        pipeline = Pipeline(steps=[
            ('preprocessor', self.create_preprocessor()),
            ('classifier', self.model)
        ])
        return pipeline

    def train(self):
        """
        Train the model with MLflow tracking enabled.

        Returns:
            pipeline: Trained sklearn pipeline
            run_id: MLflow run ID for tracking
        """
        with mlflow.start_run() as run:
            # Log parameters
            mlflow.log_param("test_size", self.test_size)
            mlflow.log_param("model_type", type(self.model).__name__)
            mlflow.log_param(
                "n_numeric_features", len(self.numeric_features)
            )
            mlflow.log_param(
                "n_categorical_features", len(self.categorical_features)
            )
            mlflow.log_param("target_column", self.target_column)

            # Log model parameters if provided
            for param_name, param_value in self.model_params.items():
                mlflow.log_param(f"model_{param_name}", param_value)

            # Log feature names
            mlflow.log_param(
                "numeric_features", ", ".join(self.numeric_features)
            )
            mlflow.log_param(
                "categorical_features", 
                ", ".join(self.categorical_features)
            )

            # Split data
            X_train, X_test, y_train, y_test = self.train_test_split()

            # Log dataset information
            mlflow.log_param("n_train_samples", len(X_train))
            mlflow.log_param("n_test_samples", len(X_test))

            # Create and train pipeline
            pipeline = self.create_pipeline_train()

            # Fit the pipeline (autolog will capture training metrics)
            pipeline.fit(X_train, y_train)

            # Make predictions and log additional metrics
            y_train_pred = pipeline.predict(X_train)
            y_test_pred = pipeline.predict(X_test)

            # Calculate and log metrics
            train_metrics = self._calculate_metrics(
                y_train, y_train_pred, prefix="train"
            )
            test_metrics = self._calculate_metrics(
                y_test, y_test_pred, prefix="test"
            )

            # Log metrics
            all_metrics = {**train_metrics, **test_metrics}
            for metric_name, metric_value in all_metrics.items():
                mlflow.log_metric(metric_name, metric_value)

            # Get the run ID for reference
            run_id = run.info.run_id

            print(f"MLflow Run ID: {run_id}")
            print(f"Tracking URI: {mlflow.get_tracking_uri()}")
            print(f"Train Accuracy: {train_metrics['train_accuracy']:.4f}")
            print(f"Test Accuracy: {test_metrics['test_accuracy']:.4f}")

            return pipeline, run_id

    def _calculate_metrics(self, y_true, y_pred, prefix=""):
        """
        Calculate classification metrics.

        Args:
            y_true: True labels
            y_pred: Predicted labels
            prefix: Prefix for metric names (e.g., "train" or "test")

        Returns:
            Dictionary of metrics
        """
        metrics = {}

        # Calculate metrics
        accuracy = accuracy_score(y_true, y_pred)
        metrics[f"{prefix}_accuracy"] = accuracy

        # For binary and multiclass classification
        try:
            precision = precision_score(
                y_true, y_pred, average='weighted', zero_division=0
            )
            recall = recall_score(
                y_true, y_pred, average='weighted', zero_division=0
            )
            f1 = f1_score(
                y_true, y_pred, average='weighted', zero_division=0
            )

            metrics[f"{prefix}_precision"] = precision
            metrics[f"{prefix}_recall"] = recall
            metrics[f"{prefix}_f1"] = f1
        except Exception:
            # In case of any issues with multiclass metrics
            pass

        return metrics