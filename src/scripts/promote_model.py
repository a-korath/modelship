from mlflow import MlflowClient
import os
import sys


def promote_model(model_name: str, model_version: str) -> None:
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5001")
    client = MlflowClient(tracking_uri=tracking_uri)
    client.set_registered_model_alias(
        name=model_name,
        alias="Production",
        version=model_version,
    )
    print(f"Model '{model_name}' version '{model_version}' promoted to Production.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python promote_model.py <model_name> <version>")
        sys.exit(1)
    promote_model(sys.argv[1], sys.argv[2])