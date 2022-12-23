import pytest
from safe_ds.data import SupervisedDataset, Table
from safe_ds.exceptions import LearningError
from safe_ds.regression import RidgeRegression


def test_ridge_regression_fit() -> None:
    table = Table.from_csv("tests/resources/test_ridge_regression.csv")
    supervised_dataset = SupervisedDataset(table, "T")
    ridge_regression = RidgeRegression()
    ridge_regression.fit(supervised_dataset)
    assert True  # This asserts that the fit method succeeds


def test_ridge_regression_fit_invalid() -> None:
    table = Table.from_csv("tests/resources/test_ridge_regression_invalid.csv")
    supervised_dataset = SupervisedDataset(table, "T")
    ridge_regression = RidgeRegression()
    with pytest.raises(LearningError):
        ridge_regression.fit(supervised_dataset)