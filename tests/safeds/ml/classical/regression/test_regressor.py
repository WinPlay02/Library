from __future__ import annotations

import itertools
from typing import TYPE_CHECKING, Any

import pandas as pd
import pytest
from safeds.data.tabular.containers import Column, Table, TaggedTable
from safeds.exceptions import (
    ColumnLengthMismatchError,
    DatasetContainsTargetError,
    DatasetMissesDataError,
    DatasetMissesFeaturesError,
    MissingValuesColumnError,
    ModelNotFittedError,
    NonNumericColumnError,
    UntaggedTableError,
)
from safeds.ml.classical.regression import (
    AdaBoostRegressor,
    DecisionTreeRegressor,
    ElasticNetRegressor,
    GradientBoostingRegressor,
    KNearestNeighborsRegressor,
    LassoRegressor,
    LinearRegressionRegressor,
    RandomForestRegressor,
    Regressor,
    RidgeRegressor,
    SupportVectorMachineRegressor,
)

# noinspection PyProtectedMember
from safeds.ml.classical.regression._regressor import _check_metrics_preconditions

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from sklearn.base import RegressorMixin


def regressors() -> list[Regressor]:
    """
    Return the list of regressors to test.

    After you implemented a new regressor, add it to this list to ensure its `fit` and `predict` method work as
    expected. Place tests of methods that are specific to your regressor in a separate test file.

    Returns
    -------
    regressors : list[Regressor]
        The list of regressors to test.
    """
    return [
        AdaBoostRegressor(),
        DecisionTreeRegressor(),
        ElasticNetRegressor(),
        GradientBoostingRegressor(),
        KNearestNeighborsRegressor(2),
        LassoRegressor(),
        LinearRegressionRegressor(),
        RandomForestRegressor(),
        RidgeRegressor(),
        SupportVectorMachineRegressor(),
    ]


@pytest.fixture()
def valid_data() -> TaggedTable:
    return Table(
        {
            "id": [1, 4],
            "feat1": [2, 5],
            "feat2": [3, 6],
            "target": [0, 1],
        },
    ).tag_columns(target_name="target", feature_names=["feat1", "feat2"])


@pytest.mark.parametrize("regressor", regressors(), ids=lambda x: x.__class__.__name__)
class TestFit:
    def test_should_succeed_on_valid_data(self, regressor: Regressor, valid_data: TaggedTable) -> None:
        regressor.fit(valid_data)
        assert True  # This asserts that the fit method succeeds

    def test_should_not_change_input_regressor(self, regressor: Regressor, valid_data: TaggedTable) -> None:
        regressor.fit(valid_data)
        assert not regressor.is_fitted()

    def test_should_not_change_input_table(self, regressor: Regressor, request: FixtureRequest) -> None:
        valid_data = request.getfixturevalue("valid_data")
        valid_data_copy = request.getfixturevalue("valid_data")
        regressor.fit(valid_data)
        assert valid_data == valid_data_copy

    @pytest.mark.parametrize(
        ("invalid_data", "expected_error", "expected_error_msg"),
        [
            (
                Table(
                    {
                        "id": [1, 4],
                        "feat1": ["a", 5],
                        "feat2": [3, 6],
                        "target": [0, 1],
                    },
                ).tag_columns(target_name="target", feature_names=["feat1", "feat2"]),
                NonNumericColumnError,
                r"Tried to do a numerical operation on one or multiple non-numerical columns: \n\{'feat1'\}",
            ),
            (
                Table(
                    {
                        "id": [1, 4],
                        "feat1": [None, 5],
                        "feat2": [3, 6],
                        "target": [0, 1],
                    },
                ).tag_columns(target_name="target", feature_names=["feat1", "feat2"]),
                MissingValuesColumnError,
                r"Tried to do an operation on one or multiple columns containing missing values: \n\{'feat1'\}",
            ),
            (
                Table(
                    {
                        "id": [],
                        "feat1": [],
                        "feat2": [],
                        "target": [],
                    },
                ).tag_columns(target_name="target", feature_names=["feat1", "feat2"]),
                DatasetMissesDataError,
                r"Dataset contains no rows",
            ),
        ],
        ids=["non-numerical data", "missing values in data", "no rows in data"],
    )
    def test_should_raise_on_invalid_data(
        self,
        regressor: Regressor,
        invalid_data: TaggedTable,
        expected_error: Any,
        expected_error_msg: str,
    ) -> None:
        with pytest.raises(expected_error, match=expected_error_msg):
            regressor.fit(invalid_data)

    @pytest.mark.parametrize(
        "table",
        [
            Table(
                {
                    "a": [1.0, 0.0, 0.0, 0.0],
                    "b": [0.0, 1.0, 1.0, 0.0],
                    "c": [0.0, 0.0, 0.0, 1.0],
                },
            ),
        ],
        ids=["untagged_table"],
    )
    def test_should_raise_if_table_is_not_tagged(self, regressor: Regressor, table: Table) -> None:
        with pytest.raises(UntaggedTableError):
            regressor.fit(table)  # type: ignore[arg-type]


@pytest.mark.parametrize("regressor", regressors(), ids=lambda x: x.__class__.__name__)
class TestPredict:
    def test_should_include_features_of_input_table(self, regressor: Regressor, valid_data: TaggedTable) -> None:
        fitted_regressor = regressor.fit(valid_data)
        prediction = fitted_regressor.predict(valid_data.features)
        assert prediction.features == valid_data.features

    def test_should_include_complete_input_table(self, regressor: Regressor, valid_data: TaggedTable) -> None:
        fitted_regressor = regressor.fit(valid_data)
        prediction = fitted_regressor.predict(valid_data.features)
        assert prediction.features == valid_data.features

    def test_should_set_correct_target_name(self, regressor: Regressor, valid_data: TaggedTable) -> None:
        fitted_regressor = regressor.fit(valid_data)
        prediction = fitted_regressor.predict(valid_data.features)
        assert prediction.target.name == "target"

    def test_should_not_change_input_table(self, regressor: Regressor, request: FixtureRequest) -> None:
        valid_data = request.getfixturevalue("valid_data")
        valid_data_copy = request.getfixturevalue("valid_data")
        fitted_classifier = regressor.fit(valid_data)
        fitted_classifier.predict(valid_data.features)
        assert valid_data == valid_data_copy

    def test_should_raise_if_not_fitted(self, regressor: Regressor, valid_data: TaggedTable) -> None:
        with pytest.raises(ModelNotFittedError):
            regressor.predict(valid_data.features)

    def test_should_raise_if_dataset_contains_target(self, regressor: Regressor, valid_data: TaggedTable) -> None:
        fitted_regressor = regressor.fit(valid_data)
        with pytest.raises(DatasetContainsTargetError, match="target"):
            fitted_regressor.predict(valid_data)

    def test_should_raise_if_dataset_misses_features(self, regressor: Regressor, valid_data: TaggedTable) -> None:
        fitted_regressor = regressor.fit(valid_data)
        with pytest.raises(DatasetMissesFeaturesError, match="[feat1, feat2]"):
            fitted_regressor.predict(valid_data.features.remove_columns(["feat1", "feat2"]))

    @pytest.mark.parametrize(
        ("invalid_data", "expected_error", "expected_error_msg"),
        [
            (
                Table(
                    {
                        "id": [1, 4],
                        "feat1": ["a", 5],
                        "feat2": [3, 6],
                    },
                ),
                NonNumericColumnError,
                (
                    r"Tried to do a numerical operation on one or multiple non-numerical columns: \n\{'feat1'\}\nYou"
                    r" can use the LabelEncoder or OneHotEncoder to transform your non-numerical data to numerical"
                    r" data.\nThe OneHotEncoder should be used if you work with nominal data. If your data contains too"
                    r" many different values\nor is ordinal, you should use the LabelEncoder."
                ),
            ),
            (
                Table(
                    {
                        "id": [1, 4],
                        "feat1": [None, 5],
                        "feat2": [3, 6],
                    },
                ),
                MissingValuesColumnError,
                (
                    r"Tried to do an operation on one or multiple columns containing missing values: \n\{'feat1'\}\nYou"
                    r" can use the Imputer to replace the missing values based on different strategies.\nIf you want to"
                    r" remove the missing values entirely you can use the method"
                    r" `Table.remove_rows_with_missing_values`."
                ),
            ),
            (
                Table(
                    {
                        "id": [],
                        "feat1": [],
                        "feat2": [],
                    },
                ),
                DatasetMissesDataError,
                r"Dataset contains no rows",
            ),
        ],
        ids=["non-numerical data", "missing values in data", "no rows in data"],
    )
    def test_should_raise_on_invalid_data(
        self,
        regressor: Regressor,
        valid_data: TaggedTable,
        invalid_data: Table,
        expected_error: Any,
        expected_error_msg: str,
    ) -> None:
        regressor = regressor.fit(valid_data)
        with pytest.raises(expected_error, match=expected_error_msg):
            regressor.predict(invalid_data)


@pytest.mark.parametrize("regressor", regressors(), ids=lambda x: x.__class__.__name__)
class TestIsFitted:
    def test_should_return_false_before_fitting(self, regressor: Regressor) -> None:
        assert not regressor.is_fitted()

    def test_should_return_true_after_fitting(self, regressor: Regressor, valid_data: TaggedTable) -> None:
        fitted_regressor = regressor.fit(valid_data)
        assert fitted_regressor.is_fitted()


class TestHash:
    @pytest.mark.parametrize(
        ("regressor1", "regressor2"),
        ([(x, y) for x in regressors() for y in regressors() if x.__class__ == y.__class__]),
        ids=lambda x: x.__class__.__name__,
    )
    def test_should_return_same_hash_for_equal_regressor(self, regressor1: Regressor, regressor2: Regressor) -> None:
        assert hash(regressor1) == hash(regressor2)

    @pytest.mark.parametrize(
        ("regressor1", "regressor2"),
        ([(x, y) for x in regressors() for y in regressors() if x.__class__ != y.__class__]),
        ids=lambda x: x.__class__.__name__,
    )
    def test_should_return_different_hash_for_unequal_regressor(
        self,
        regressor1: Regressor,
        regressor2: Regressor,
    ) -> None:
        assert hash(regressor1) != hash(regressor2)

    @pytest.mark.parametrize("regressor1", regressors(), ids=lambda x: x.__class__.__name__)
    def test_should_return_different_hash_for_same_regressor_fit(
        self,
        regressor1: Regressor,
        valid_data: TaggedTable,
    ) -> None:
        regressor1_fit = regressor1.fit(valid_data)
        assert hash(regressor1) != hash(regressor1_fit)

    @pytest.mark.parametrize(
        ("regressor1", "regressor2"),
        (list(itertools.product(regressors(), regressors()))),
        ids=lambda x: x.__class__.__name__,
    )
    def test_should_return_different_hash_for_regressor_fit(
        self,
        regressor1: Regressor,
        regressor2: Regressor,
        valid_data: TaggedTable,
    ) -> None:
        regressor1_fit = regressor1.fit(valid_data)
        assert hash(regressor1_fit) != hash(regressor2)


class DummyRegressor(Regressor):
    """
    Dummy regressor to test metrics.

    Metrics methods expect a `TaggedTable` as input with two columns:

    - `predicted`: The predicted targets.
    - `expected`: The correct targets.

    `target_name` must be set to `"expected"`.
    """

    def fit(self, training_set: TaggedTable) -> DummyRegressor:  # noqa: ARG002
        return self

    def predict(self, dataset: Table) -> TaggedTable:
        # Needed until https://github.com/Safe-DS/Library/issues/75 is fixed
        predicted = dataset.get_column("predicted")
        feature = predicted.rename("feature")
        dataset = Table.from_columns([feature, predicted])

        return dataset.tag_columns(target_name="predicted")

    def is_fitted(self) -> bool:
        return True

    def _get_sklearn_regressor(self) -> RegressorMixin:
        pass


class TestMeanAbsoluteError:
    @pytest.mark.parametrize(
        ("predicted", "expected", "result"),
        [
            ([1, 2], [1, 2], 0),
            ([0, 0], [1, 1], 1),
            ([1, 1, 1], [2, 2, 11], 4),
            ([0, 0, 0], [10, 2, 18], 10),
            ([0.5, 0.5], [1.5, 1.5], 1),
        ],
    )
    def test_valid_data(self, predicted: list[float], expected: list[float], result: float) -> None:
        table = Table(
            {
                "predicted": predicted,
                "expected": expected,
            },
        ).tag_columns(
            target_name="expected",
        )

        assert DummyRegressor().mean_absolute_error(table) == result

    @pytest.mark.parametrize(
        "table",
        [
            Table(
                {
                    "a": [1.0, 0.0, 0.0, 0.0],
                    "b": [0.0, 1.0, 1.0, 0.0],
                    "c": [0.0, 0.0, 0.0, 1.0],
                },
            ),
        ],
        ids=["untagged_table"],
    )
    def test_should_raise_if_table_is_not_tagged(self, table: Table) -> None:
        with pytest.raises(UntaggedTableError):
            DummyRegressor().mean_absolute_error(table)  # type: ignore[arg-type]


class TestMeanSquaredError:
    @pytest.mark.parametrize(
        ("predicted", "expected", "result"),
        [([1, 2], [1, 2], 0), ([0, 0], [1, 1], 1), ([1, 1, 1], [2, 2, 11], 34)],
        ids=["perfect_prediction", "bad_prediction", "worst_prediction"],
    )
    def test_valid_data(self, predicted: list[float], expected: list[float], result: float) -> None:
        table = Table({"predicted": predicted, "expected": expected}).tag_columns(
            target_name="expected",
        )

        assert DummyRegressor().mean_squared_error(table) == result

    @pytest.mark.parametrize(
        "table",
        [
            Table(
                {
                    "a": [1.0, 0.0, 0.0, 0.0],
                    "b": [0.0, 1.0, 1.0, 0.0],
                    "c": [0.0, 0.0, 0.0, 1.0],
                },
            ),
        ],
        ids=["untagged_table"],
    )
    def test_should_raise_if_table_is_not_tagged(self, table: Table) -> None:
        with pytest.raises(UntaggedTableError):
            DummyRegressor().mean_squared_error(table)  # type: ignore[arg-type]


class TestCheckMetricsPreconditions:
    @pytest.mark.parametrize(
        ("actual", "expected", "error"),
        [
            (["A", "B"], [1, 2], TypeError),
            ([1, 2], ["A", "B"], TypeError),
            ([1, 2, 3], [1, 2], ColumnLengthMismatchError),
        ],
    )
    def test_should_raise_if_validation_fails(
        self,
        actual: list[str | int],
        expected: list[str | int],
        error: type[Exception],
    ) -> None:
        actual_column: Column = Column("actual", pd.Series(actual))
        expected_column: Column = Column("expected", pd.Series(expected))
        with pytest.raises(error):
            _check_metrics_preconditions(actual_column, expected_column)
