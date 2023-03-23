import pytest
from safeds.data.tabular.containers import Table, TaggedTable
from safeds.exceptions import LearningError
from safeds.ml.classification import RandomForest as RandomForestClassifier
from tests.fixtures import resolve_resource_path


def test_logistic_regression_fit() -> None:
    table = Table.from_csv(resolve_resource_path("test_random_forest.csv"))
    tagged_table = TaggedTable(table, "T")
    random_forest = RandomForestClassifier()
    random_forest.fit(tagged_table)
    assert True  # This asserts that the fit method succeeds


def test_logistic_regression_fit_invalid() -> None:
    table = Table.from_csv(resolve_resource_path("test_random_forest_invalid.csv"))
    tagged_table = TaggedTable(table, "T")
    random_forest = RandomForestClassifier()
    with pytest.raises(LearningError):
        random_forest.fit(tagged_table)
