import mlflow
import os
from transformers import pipeline  
import mlflow.transformers
from mlflow.tracking import MlflowClient
from transformers import pipeline
import tempfile
ARTIFACT_ROOT = "/mlflow/artifacts"

def register_model(model_name: str, model_path: str, tracking_uri: str) -> None:
    mlflow.set_tracking_uri(tracking_uri)
    client = mlflow.tracking.MlflowClient()

    experiment = client.get_experiment_by_name("Default")
    if experiment is None:
        mlflow.create_experiment("Default", artifact_location=ARTIFACT_ROOT)
    mlflow.set_experiment("Default")
    pipe = pipeline("sentiment-analysis", model=model_path)
    with tempfile.TemporaryDirectory() as tmpdir:
        mlflow.transformers.save_model(pipe, tmpdir)
        
        with mlflow.start_run():
            mlflow.log_artifacts(tmpdir, artifact_path=model_name)
            model_uri = f"runs:/{mlflow.active_run().info.run_id}/{model_name}"
            res = mlflow.register_model(model_uri, model_name)
            client.set_registered_model_alias(
                name=model_name,
                alias="Production",
                version=res.version
            )
            print(f"Model '{model_name}' registered successfully from path '{model_path}'.")


if __name__ == "__main__":
    MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english"
    MODEL_PATH = "distilbert-base-uncased-finetuned-sst-2-english"
    MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "sqlite:////mlflow/mlflow.db")
    
    register_model(MODEL_NAME, MODEL_PATH, MLFLOW_TRACKING_URI) 