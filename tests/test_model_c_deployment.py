import importlib.util
import json
import sys
import unittest
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/materialize_model_c_deployment.py"
SPEC = importlib.util.spec_from_file_location("model_c_deployment", SCRIPT)
DEPLOYMENT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DEPLOYMENT)


class TransparentStateTests(unittest.TestCase):
    def test_synthetic_softmax_and_class_reordering(self):
        state = {
            "output_class_order": ["B", "A"],
            "standard_scaler": {"mean": [1.0, 2.0], "scale": [2.0, 4.0]},
            "logistic_regression": {
                "coefficient_class_order": ["A", "B"],
                "coefficients": [[1.0, 0.0], [0.0, 1.0]],
                "intercepts": [0.0, 0.0],
            },
        }
        probabilities = DEPLOYMENT.predict_from_state(
            np.array([[3.0, 2.0], [1.0, 6.0]]), state
        )
        self.assertEqual(probabilities.shape, (2, 2))
        self.assertTrue(np.allclose(probabilities.sum(axis=1), 1.0))
        self.assertGreater(probabilities[0, 1], probabilities[0, 0])
        self.assertGreater(probabilities[1, 0], probabilities[1, 1])

    def test_nonfinite_and_wrong_shape_block(self):
        state = {
            "output_class_order": ["A", "B"],
            "standard_scaler": {"mean": [0.0], "scale": [1.0]},
            "logistic_regression": {
                "coefficient_class_order": ["A", "B"],
                "coefficients": [[1.0], [-1.0]],
                "intercepts": [0.0, 0.0],
            },
        }
        with self.assertRaises(DEPLOYMENT.DeploymentError):
            DEPLOYMENT.predict_from_state(np.array([[np.nan]]), state)
        with self.assertRaises(DEPLOYMENT.DeploymentError):
            DEPLOYMENT.predict_from_state(np.array([[1.0, 2.0]]), state)


class FrozenDeploymentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads((ROOT / "configs/model_c_deployment.json").read_text())
        cls.state = json.loads(
            (ROOT / "metadata/model_c_deployment_estimator.json").read_text()
        )
        cls.receipt = json.loads(
            (ROOT / "metadata/model_c_deployment_estimator_receipt.json").read_text()
        )

    def test_saved_state_reconstructs_frozen_predictions(self):
        verification = DEPLOYMENT.verify_saved()
        self.assertEqual(
            verification["status"], "VERIFIED_POST_DEVELOPMENT_DEPLOYMENT_ESTIMATOR"
        )
        self.assertEqual(verification["training_rows"], 15999)
        self.assertEqual(
            verification["prediction_sha256"], self.receipt["prediction_sha256"]
        )

    def test_state_is_transparent_and_complete(self):
        self.assertEqual(self.state["feature_order"], self.config["features"])
        self.assertEqual(
            self.state["output_class_order"], self.config["output_class_order"]
        )
        self.assertEqual(len(self.state["standard_scaler"]["mean"]), 9)
        self.assertEqual(len(self.state["standard_scaler"]["scale"]), 9)
        self.assertEqual(len(self.state["logistic_regression"]["coefficients"]), 5)
        self.assertTrue(
            all(len(row) == 9 for row in self.state["logistic_regression"]["coefficients"])
        )
        self.assertEqual(len(self.state["logistic_regression"]["intercepts"]), 5)

    def test_artifact_scope_is_not_historical_evidence(self):
        for record in (self.config, self.state, self.receipt):
            self.assertFalse(record["historical_oof_reconstruction"])
            self.assertFalse(record["new_development_evidence"])
            self.assertFalse(record["longbench_inputs_read"])
            self.assertFalse(record["model_d_rerun"])

    def test_second_fit_is_refused(self):
        with self.assertRaisesRegex(DEPLOYMENT.DeploymentError, "already exists"):
            DEPLOYMENT.fit_once()

    def test_no_arbitrary_path_or_network_interface(self):
        source = SCRIPT.read_text()
        for forbidden in ("argparse", "requests", "urllib", "boto", "subprocess"):
            self.assertNotIn(forbidden, source)
        self.assertIn('if sys.argv[1:] == ["--verify"]', source)


if __name__ == "__main__":
    unittest.main()
