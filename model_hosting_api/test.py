import unittest
import requests
from sklearn.datasets import load_iris
from sklearn.utils import Bunch
import pandas as pd
from typing import cast
import os
import random
from io import BytesIO, StringIO


API_URL = os.getenv("API_URL")
TESTS_RAN_DIR = "./tests_ran"


class TestPredictionAPI(unittest.TestCase):
    
    def setUp(self):
        os.makedirs(TESTS_RAN_DIR, exist_ok=True)

        iris: Bunch = cast(Bunch, load_iris(as_frame=True))
        self.X: pd.DataFrame = iris.data
        self.y: pd.DataFrame = iris.target
        self.target_names = iris.target_names

    def test_predict_subset(self):
        """Send a subset of the Iris dataset to the API and check predictions match y."""

        subset = self.X.iloc[:, :]
        true_labels = self.y.iloc[:]
        
        csv_buffer = BytesIO()
        subset.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)

        response = requests.post(
            f"{API_URL}/predict",
            files={"file": ("test.csv", csv_buffer, "text/csv")}
        )

        self.assertEqual(
            response.status_code, 200,
            f"[x] Predict request failed: {response.status_code} {response.text}"
        )
        
        result_df = pd.read_csv(StringIO(response.content.decode()))

        total_samples = len(true_labels)
        correct_predictions = 0
        true_class_names = []

        for i, true_label in enumerate(true_labels):
            predicted_class_name = result_df.loc[i, "predicted_class"]
            true_class_name = self.target_names[true_label]
            true_class_names.append(true_class_name)

            if predicted_class_name == true_class_name:
                correct_predictions += 1

        result_df["true_class"] = true_class_names

        print(f"[v] Calculated API predictions precision: {correct_predictions / total_samples * 100}%")

        output_path = os.path.join(TESTS_RAN_DIR, f"subset_predictions_{random.randint(111111, 999999)}.csv")
        result_df.to_csv(output_path, index=False)

        print(f"[v] Saved annotated predictions CSV to {output_path}")


if __name__ == "__main__":
    unittest.main()
