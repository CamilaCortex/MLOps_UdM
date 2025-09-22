from src.app.train.etl import UserGenerator
from src.app.train.feature_engineer import FeatureEngineer
from src.app.train.train import Train
from src.app.train.train_with_mlflow import Train as TrainWithMlflow


def task_train():
    # generate data
    user_generator = UserGenerator(n_samples=25000)
    df = user_generator.create_dataset()

    # feature engineer
    feature_engineer = FeatureEngineer(df)
    df_engineered = feature_engineer.create_features()

    # train
    numeric_features = ['days_since_registration', 'total_purchases', 'avg_order_value', 
                   'last_purchase_days', 'sessions_last_30_days', 'time_on_site_minutes', 
                   'pages_per_session', 'cart_abandonment_rate', 'purchase_frequency']
    categorical_features = ['age_group', 'location', 'device_type', 'subscription_type']
    target_column = 'dar_promocion'
    test_size = 0.25
    model = LogisticRegression(random_state=42, max_iter=1000)

    train = Train(df_engineered, numeric_features, categorical_features, target_column, test_size, model)
    pipeline = train.train()
    
    return pipeline