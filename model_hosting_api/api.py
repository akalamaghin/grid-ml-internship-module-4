import io
import pandas as pd
from flask import Flask, request, abort, send_file
from sklearn.utils import Bunch
from sklearn.datasets import load_iris
from sklearn.neighbors import KNeighborsClassifier
from typing import cast
from werkzeug.datastructures import FileStorage
import time
import os


class IrisModel:

    def __init__(self):
        self.iris: Bunch = cast(Bunch, load_iris(as_frame=True))

        X: pd.DataFrame = self.iris.data
        y: pd.Series = self.iris.target

        self.model = KNeighborsClassifier(n_neighbors=3)
        print("Loading the iris model...")
        start_time = time.time()

        self.model.fit(X, y)

        end_time = time.time()
        elapsed = end_time - start_time
        print(f"Model loaded in {elapsed:.4f} seconds")

        self.target_names: list[str] = list(self.iris.target_names)


api = Flask(__name__)

hosted_model = IrisModel()


ALLOWED_EXTENSIONS = {"csv"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@api.route("/predict", methods=["POST"])
def predict():
    """
    Accepts a CSV file with iris features and returns the same CSV
    with an added 'predicted_class' column.
    """
    if "file" not in request.files:
        abort(400, "No file part in request")

    file: FileStorage = request.files["file"]
    if file.filename == "":
        abort(400, "No file selected")

    if not allowed_file(file.filename):
        abort(400, "Only CSV files are allowed")

    try:
        df = pd.read_csv(io.BytesIO(file.read()))

        # Validate columns
        expected_cols = hosted_model.iris.feature_names
        if not all(col in df.columns for col in expected_cols):
            abort(400, f"CSV must contain columns: {expected_cols}")

        # Run inference
        preds = hosted_model.model.predict(df[expected_cols])
        df["predicted_class"] = [hosted_model.target_names[p] for p in preds]

        # Return updated CSV as attachment
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)

        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype="text/csv",
            as_attachment=True,
            download_name="predictions.csv",
        )
    except Exception as e:
        abort(400, f"Error processing file: {str(e)}")


if __name__ == "__main__":
    api.run(
        debug=os.getenv("DEBUG", "false").lower() in ("1", "true", "yes", "on"),
        port=int(os.getenv("API_PORT", "8000"))
    )
