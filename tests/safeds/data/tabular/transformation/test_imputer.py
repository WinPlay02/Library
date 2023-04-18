import pytest
from safeds.data.tabular.containers import Table
from safeds.data.tabular.exceptions import TransformerNotFittedError, UnknownColumnNameError
from safeds.data.tabular.transformation import Imputer
from safeds.data.tabular.typing import ImputerStrategy


class TestFit:
    def test_should_raise_if_column_not_found(self) -> None:
        table = Table.from_dict(
            {
                "a": [1, 3, None],
            },
        )

        with pytest.raises(UnknownColumnNameError):
            Imputer(Imputer.Strategy.Constant(0)).fit(table, ["b"])

    def test_should_not_change_original_transformer(self) -> None:
        table = Table.from_dict(
            {
                "a": [1, 3, None],
            },
        )

        transformer = Imputer(Imputer.Strategy.Constant(0))
        transformer.fit(table)

        assert transformer._wrapped_transformer is None
        assert transformer._column_names is None


class TestTransform:
    def test_should_raise_if_column_not_found(self) -> None:
        table_to_fit = Table.from_dict(
            {
                "a": [1, 3, None],
            },
        )

        transformer = Imputer(Imputer.Strategy.Constant(0)).fit(table_to_fit)

        table_to_transform = Table.from_dict(
            {
                "b": [1, 3, None],
            },
        )

        with pytest.raises(UnknownColumnNameError):
            transformer.transform(table_to_transform)

    def test_should_raise_if_not_fitted(self) -> None:
        table = Table.from_dict(
            {
                "a": [1, 3, None],
            },
        )

        transformer = Imputer(Imputer.Strategy.Constant(0))

        with pytest.raises(TransformerNotFittedError):
            transformer.transform(table)


class TestIsFitted:
    def test_should_return_false_before_fitting(self) -> None:
        transformer = Imputer(Imputer.Strategy.Mean())
        assert not transformer.is_fitted()

    def test_should_return_true_after_fitting(self) -> None:
        table = Table.from_dict(
            {
                "a": [1, 3, None],
            },
        )

        transformer = Imputer(Imputer.Strategy.Mean())
        fitted_transformer = transformer.fit(table)
        assert fitted_transformer.is_fitted()


class TestFitAndTransform:
    @pytest.mark.parametrize(
        ("table", "column_names", "strategy", "expected"),
        [
            (
                Table.from_dict(
                    {
                        "a": [1.0, 3.0, None],
                    },
                ),
                None,
                Imputer.Strategy.Constant(0.0),
                Table.from_dict(
                    {
                        "a": [1.0, 3.0, 0.0],
                    },
                ),
            ),
            (
                Table.from_dict(
                    {
                        "a": [1.0, 3.0, None],
                    },
                ),
                None,
                Imputer.Strategy.Mean(),
                Table.from_dict(
                    {
                        "a": [1.0, 3.0, 2.0],
                    },
                ),
            ),
            (
                Table.from_dict(
                    {
                        "a": [1.0, 3.0, 1.0, None],
                    },
                ),
                None,
                Imputer.Strategy.Median(),
                Table.from_dict(
                    {
                        "a": [1.0, 3.0, 1.0, 1.0],
                    },
                ),
            ),
            (
                Table.from_dict(
                    {
                        "a": [1.0, 3.0, 3.0, None],
                    },
                ),
                None,
                Imputer.Strategy.Mode(),
                Table.from_dict(
                    {
                        "a": [1.0, 3.0, 3.0, 3.0],
                    },
                ),
            ),
            (
                Table.from_dict(
                    {
                        "a": [1.0, 3.0, None],
                        "b": [1.0, 3.0, None],
                    },
                ),
                ["a"],
                Imputer.Strategy.Constant(0.0),
                Table.from_dict(
                    {
                        "a": [1.0, 3.0, 0.0],
                        "b": [1.0, 3.0, None],
                    },
                ),
            ),
        ],
    )
    def test_should_return_transformed_table(
        self,
        table: Table,
        column_names: list[str] | None,
        strategy: ImputerStrategy,
        expected: Table,
    ) -> None:
        assert Imputer(strategy).fit_and_transform(table, column_names) == expected

    def test_should_raise_if_strategy_is_mode_but_multiple_values_are_most_frequent(self) -> None:
        table = Table.from_dict(
            {
                "a": [1, 2, 3, None],
            },
        )

        with pytest.raises(IndexError):
            Imputer(Imputer.Strategy.Mode()).fit_and_transform(table)

    def test_should_not_change_original_table(self) -> None:
        table = Table.from_dict(
            {
                "a": [1, None, None],
            },
        )

        Imputer(strategy=Imputer.Strategy.Constant(1)).fit_and_transform(table)

        expected = Table.from_dict(
            {
                "a": [1, None, None],
            },
        )

        assert table == expected