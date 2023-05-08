import pytest
from safeds.data.image.containers import Image
from safeds.data.tabular.containers import Table
from safeds.exceptions import NonNumericColumnError

from tests.helpers import resolve_resource_path


def test_should_match_snapshot() -> None:
    table = Table({"A": [1, 2, 3]})
    table.get_column("A").plot_boxplot()
    current = table.get_column("A").plot_boxplot()
    snapshot = Image.from_png_file(resolve_resource_path("./image/snapshot_boxplot.png"))

    # Inlining the expression into the assert causes pytest to hang if the assertion fails when run from PyCharm.
    assertion = snapshot._image.tobytes() == current._image.tobytes()
    assert assertion


def test_should_raise_if_column_contains_non_numerical_values() -> None:
    table = Table({"A": [1, 2, "A"]})
    with pytest.raises(NonNumericColumnError):
        table.get_column("A").plot_boxplot()
