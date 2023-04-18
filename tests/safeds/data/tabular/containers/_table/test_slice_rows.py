import pytest
from safeds.data.tabular.containers import Table


def test_slice_rows_valid() -> None:
    table = Table.from_dict({"col1": [1, 2, 1], "col2": [1, 2, 4]})
    test_table = Table.from_dict({"col1": [1, 2], "col2": [1, 2]})
    second_test_table = Table.from_dict({"col1": [1, 1], "col2": [1, 4]})
    new_table = table.slice_rows(0, 2, 1)
    second_new_table = table.slice_rows(0, 3, 2)
    third_new_table = table.slice_rows()
    assert new_table == test_table
    assert second_new_table == second_test_table
    assert third_new_table == table


@pytest.mark.parametrize(
    ("start", "end", "step"),
    [
        (3, 2, 1),
        (4, 0, 1),
        (0, 4, 1),
        (-4, 0, 1),
        (0, -4, 1),
    ],
)
def test_slice_rows_invalid(start: int, end: int, step: int) -> None:
    table = Table.from_dict({"col1": [1, 2, 1], "col2": [1, 2, 4]})

    with pytest.raises(ValueError, match="The given index is out of bounds"):
        table.slice_rows(start, end, step)