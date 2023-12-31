from sklearn.svm import LinearSVC
import argparse
import numpy as np
from sklearn.model_selection import train_test_split
import mlflow
from azureml.core import Workspace, Dataset

def clean_data(data):
    # Dict for cleaning data
    label_maps = {
        "Iris-setosa" : 0,
        "Iris-versicolor": 1,
        "Iris-virginica": 2
    }
    data = data.to_pandas_dataframe().dropna()
    data = data.drop("Id", axis=1)
    y_df = data.pop("Species").apply(lambda s: label_maps[s])
    return data, y_df

def main():
    # Add arguments to script
    parser = argparse.ArgumentParser()

    parser.add_argument('--C', type=float, default=1.0, help="Inverse of regularization strength. Smaller values cause stronger regularization")
    parser.add_argument('--max_iter', type=int, default=100, help="Maximum number of iterations to converge")
    parser.add_argument('--dataset_name', help="Dataset name")

    args = parser.parse_args()
    # Start Logging
    mlflow.start_run()

    # enable autologging
    mlflow.sklearn.autolog()

    ws = Workspace.from_config()
    ds = Dataset.get_by_name(ws, args.dataset_name)
    
    x, y = clean_data(ds)

    # TODO: Split data into train and test sets.

    x_train, x_test, y_train, y_test = train_test_split(x, y)

    model = LinearSVC(C=args.C, max_iter=args.max_iter).fit(x_train, y_train)

    accuracy = model.score(x_test, y_test)
    mlflow.log_metric('Accuracy', float(accuracy))
    registered_model_name="hp"
    mlflow.sklearn.log_model(
        sk_model=model,
        registered_model_name=registered_model_name,
        artifact_path=registered_model_name
    )
if __name__ == '__main__':
    main()