import warnings

import mlflow
import mlflow.sklearn
import optuna
from optuna.integration.mlflow import MLflowCallback
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier  # noqa: F401
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, f1_score, precision_score,
                             recall_score, roc_auc_score)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

warnings.filterwarnings('ignore')


class TrainMlflowOptuna:
    def __init__(
        self, df, numeric_features, categorical_features, 
        target_column, model_class=LogisticRegression, 
        test_size=0.2, model_params=None, mlflow_setup=None,
        n_trials=10, optimization_metric='accuracy',
        param_distributions=None
    ):
        """
        Initialize the Train class with MLflow and Optuna capabilities.

        Args:
            df: Input dataframe
            numeric_features: List of numeric feature column names
            categorical_features: List of categorical feature column names
            target_column: Name of target column
            model_class: Model class to instantiate (not an instance)
            model_params: Dictionary of fixed model parameters (optional)
            mlflow_setup: MLflow configuration
            test_size: Proportion of data to use for testing
            n_trials: Number of Optuna trials to run
            optimization_metric: Metric to optimize ('accuracy', 'f1', 'precision', 'recall', 'roc_auc')
            param_distributions: Dictionary defining parameter search space
                Example: {
                    'C': ('float', 0.001, 100, True),  # (type, min, max, log)
                    'penalty': ('categorical', ['l1', 'l2']),
                    'max_iter': ('int', 100, 1000)
                }
        """
        self.df = df
        self.numeric_features = numeric_features
        self.categorical_features = categorical_features
        self.target_column = target_column
        self.test_size = test_size
        self.model_class = model_class
        self.model_params = model_params if model_params is not None else {}
        self.n_trials = n_trials
        self.optimization_metric = optimization_metric
        self.param_distributions = param_distributions or {}

        # Set up MLflow tracking
        self.setup = mlflow_setup
        
        # Store best model and parameters
        self.best_model = None
        self.best_params = None
        self.best_pipeline = None
        self.best_score = None
        

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

    def create_pipeline_train(self, model):
        """Create pipeline with a specific model instance."""
        pipeline = Pipeline(steps=[
            ('preprocessor', self.create_preprocessor()),
            ('classifier', model)
        ])
        return pipeline

    def create_objective(self, X_train, X_test, y_train, y_test):
        """Create an Optuna objective function for hyperparameter optimization."""
        
        def objective(trial):
            # Suggest hyperparameters from the provided distributions
            params = {}
            for param_name, param_config in self.param_distributions.items():
                param_type = param_config[0]
                
                if param_type == 'float':
                    min_val, max_val = param_config[1], param_config[2]
                    log = param_config[3] if len(param_config) > 3 else False
                    params[param_name] = trial.suggest_float(
                        param_name, min_val, max_val, log=log
                    )
                elif param_type == 'int':
                    min_val, max_val = param_config[1], param_config[2]
                    params[param_name] = trial.suggest_int(
                        param_name, min_val, max_val
                    )
                elif param_type == 'categorical':
                    choices = param_config[1]
                    params[param_name] = trial.suggest_categorical(
                        param_name, choices
                    )
            
            # Merge with fixed params if provided
            all_params = {**self.model_params, **params}
            
            # Create model instance with suggested parameters
            model = self.model_class(**all_params)
            
            # Create and train pipeline
            pipeline = self.create_pipeline_train(model)
            
            # Fit the pipeline
            pipeline.fit(X_train, y_train)
            
            # Calculate the optimization metric
            if self.optimization_metric == 'accuracy':
                y_pred = pipeline.predict(X_test)
                score = accuracy_score(y_test, y_pred)
            elif self.optimization_metric == 'f1':
                y_pred = pipeline.predict(X_test)
                score = f1_score(y_test, y_pred, average='weighted')
            elif self.optimization_metric == 'precision':
                y_pred = pipeline.predict(X_test)
                score = precision_score(y_test, y_pred, average='weighted', zero_division=0)
            elif self.optimization_metric == 'recall':
                y_pred = pipeline.predict(X_test)
                score = recall_score(y_test, y_pred, average='weighted', zero_division=0)
            elif self.optimization_metric == 'roc_auc':
                # For ROC AUC, we need probability predictions
                if hasattr(pipeline, 'predict_proba'):
                    y_pred_proba = pipeline.predict_proba(X_test)
                    # For binary classification, use the positive class probability
                    if y_pred_proba.shape[1] == 2:
                        y_pred_proba = y_pred_proba[:, 1]
                    score = roc_auc_score(y_test, y_pred_proba, multi_class='ovr')
                else:
                    # Fallback to accuracy if model doesn't support predict_proba
                    y_pred = pipeline.predict(X_test)
                    score = accuracy_score(y_test, y_pred)
            else:
                raise ValueError(f"Unknown optimization metric: {self.optimization_metric}")
            
            return score
        
        return objective
    
    def train_with_optuna(self):
        """
        Train the model with Optuna hyperparameter optimization and MLflow tracking.

        Returns:
            best_pipeline: Best trained sklearn pipeline
            best_run_id: MLflow run ID for the best model
            study: Optuna study object with optimization results
        """
        # Split data once for all trials
        X_train, X_test, y_train, y_test = self.train_test_split()
        
        # Create Optuna study
        study = optuna.create_study(
            direction='maximize',
            study_name=f"optuna_{self.model_class.__name__}"
        )
        
        # Create objective function
        objective = self.create_objective(X_train, X_test, y_train, y_test)
        
        # Set up MLflow callback for Optuna
        mlflow_callback = MLflowCallback(
            tracking_uri=mlflow.get_tracking_uri(),
            metric_name=self.optimization_metric
        )
        
        # Run optimization
        print(f"Starting Optuna optimization with {self.n_trials} trials...")
        print(f"Optimizing for: {self.optimization_metric}")
        print(f"Model type: {self.model_class.__name__}")
        
        study.optimize(
            objective, 
            n_trials=self.n_trials,
            callbacks=[mlflow_callback]
        )
        
        # Get best parameters
        self.best_params = study.best_params
        self.best_score = study.best_value
        
        print(f"\nOptimization complete!")
        print(f"Best {self.optimization_metric}: {self.best_score:.4f}")
        print(f"Best parameters: {self.best_params}")
        
        # Train final model with best parameters and log to MLflow
        best_run_id = self._train_best_model(X_train, X_test, y_train, y_test)
        
        return self.best_pipeline, best_run_id, study
    
    def _train_best_model(self, X_train, X_test, y_train, y_test):
        """Train the final model with best parameters and comprehensive MLflow logging."""
        
        with mlflow.start_run(run_name=f"best_model_{self.model_class.__name__}") as run:
            # Log basic parameters
            mlflow.log_param("test_size", self.test_size)
            mlflow.log_param("model_type", self.model_class.__name__)
            mlflow.log_param("n_numeric_features", len(self.numeric_features))
            mlflow.log_param("n_categorical_features", len(self.categorical_features))
            mlflow.log_param("target_column", self.target_column)
            mlflow.log_param("n_trials", self.n_trials)
            mlflow.log_param("optimization_metric", self.optimization_metric)
            
            # Log best hyperparameters
            for param_name, param_value in self.best_params.items():
                mlflow.log_param(f"best_{param_name}", param_value)
            
            # Log fixed parameters if any
            for param_name, param_value in self.model_params.items():
                mlflow.log_param(f"fixed_{param_name}", param_value)
            
            # Log feature names
            mlflow.log_param("numeric_features", ", ".join(self.numeric_features))
            mlflow.log_param("categorical_features", ", ".join(self.categorical_features))
            
            # Log dataset information
            mlflow.log_param("n_train_samples", len(X_train))
            mlflow.log_param("n_test_samples", len(X_test))
            
            # Create model with best parameters
            all_params = {**self.model_params, **self.best_params}
            self.best_model = self.model_class(**all_params)
            
            # Create and train pipeline
            self.best_pipeline = self.create_pipeline_train(self.best_model)
            self.best_pipeline.fit(X_train, y_train)
            
            # Make predictions
            y_train_pred = self.best_pipeline.predict(X_train)
            y_test_pred = self.best_pipeline.predict(X_test)
            
            # Calculate and log metrics
            train_metrics = self._calculate_metrics(y_train, y_train_pred, prefix="train")
            test_metrics = self._calculate_metrics(y_test, y_test_pred, prefix="test")
            
            all_metrics = {**train_metrics, **test_metrics}
            for metric_name, metric_value in all_metrics.items():
                mlflow.log_metric(metric_name, metric_value)
            
            # Log the optimization score from Optuna
            mlflow.log_metric(f"optuna_best_{self.optimization_metric}", self.best_score)
            
            # Log the model
            mlflow.sklearn.log_model(
                self.best_pipeline,
                "model",
                input_example=X_train.iloc[:5],
                signature=mlflow.models.infer_signature(X_train, y_train_pred)
            )
            
            # Get the run ID for reference
            run_id = run.info.run_id
            
            print(f"\nBest Model MLflow Run ID: {run_id}")
            print(f"Tracking URI: {mlflow.get_tracking_uri()}")
            print(f"Train Accuracy: {train_metrics['train_accuracy']:.4f}")
            print(f"Test Accuracy: {test_metrics['test_accuracy']:.4f}")
            
            return run_id
    
    def train(self):
        """Alias for train_with_optuna to maintain compatibility."""
        return self.train_with_optuna()

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