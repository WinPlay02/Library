import pytest
from safeds.data.tabular.containers import Table, TaggedTable
from safeds.exceptions import OutOfBoundsError
from safeds.ml.classical.classification import SupportVectorMachineClassifier


@pytest.fixture()
def training_set() -> TaggedTable:
    table = Table({"col1": [1, 2, 3, 4], "col2": [1, 2, 3, 4]})
    return table.tag_columns(target_name="col1", feature_names=["col2"])


class TestC:
    def test_should_be_passed_to_fitted_model(self, training_set: TaggedTable) -> None:
        fitted_model = SupportVectorMachineClassifier(c=2).fit(training_set=training_set)
        assert fitted_model.c == 2

    def test_should_be_passed_to_sklearn(self, training_set: TaggedTable) -> None:
        fitted_model = SupportVectorMachineClassifier(c=2).fit(training_set)
        assert fitted_model._wrapped_classifier is not None
        assert fitted_model._wrapped_classifier.C == 2

    @pytest.mark.parametrize("c", [-1.0, 0.0], ids=["minus_one", "zero"])
    def test_should_raise_if_less_than_or_equal_to_0(self, c: float) -> None:
        with pytest.raises(OutOfBoundsError, match=rf"c \(={c}\) is not inside \(0, \u221e\)\."):
            SupportVectorMachineClassifier(c=c)


class TestKernel:
    def test_should_be_passed_to_fitted_model(self, training_set: TaggedTable) -> None:
        kernel = SupportVectorMachineClassifier.Kernel.Linear()
        fitted_model = SupportVectorMachineClassifier(c=2, kernel=kernel).fit(training_set=training_set)
        assert isinstance(fitted_model.kernel, SupportVectorMachineClassifier.Kernel.Linear)

    def test_should_be_passed_to_sklearn(self, training_set: TaggedTable) -> None:
        kernel = SupportVectorMachineClassifier.Kernel.Linear()
        fitted_model = SupportVectorMachineClassifier(c=2, kernel=kernel).fit(training_set)
        assert fitted_model._wrapped_classifier is not None
        assert isinstance(fitted_model.kernel, SupportVectorMachineClassifier.Kernel.Linear)

    def test_should_get_sklearn_kernel_linear(self) -> None:
        svm = SupportVectorMachineClassifier(c=2, kernel=SupportVectorMachineClassifier.Kernel.Linear())
        assert isinstance(svm.kernel, SupportVectorMachineClassifier.Kernel.Linear)
        linear_kernel = svm.kernel._get_sklearn_kernel()
        assert linear_kernel == "linear"

    @pytest.mark.parametrize("degree", [-1, 0], ids=["minus_one", "zero"])
    def test_should_raise_if_degree_less_than_1(self, degree: int) -> None:
        with pytest.raises(OutOfBoundsError, match=rf"degree \(={degree}\) is not inside \[1, \u221e\)\."):
            SupportVectorMachineClassifier.Kernel.Polynomial(degree=degree)

    def test_should_get_sklearn_kernel_polynomial(self) -> None:
        svm = SupportVectorMachineClassifier(c=2, kernel=SupportVectorMachineClassifier.Kernel.Polynomial(degree=2))
        assert isinstance(svm.kernel, SupportVectorMachineClassifier.Kernel.Polynomial)
        poly_kernel = svm.kernel._get_sklearn_kernel()
        assert poly_kernel == "poly"

    def test_should_get_sklearn_kernel_sigmoid(self) -> None:
        svm = SupportVectorMachineClassifier(c=2, kernel=SupportVectorMachineClassifier.Kernel.Sigmoid())
        assert isinstance(svm.kernel, SupportVectorMachineClassifier.Kernel.Sigmoid)
        sigmoid_kernel = svm.kernel._get_sklearn_kernel()
        assert sigmoid_kernel == "sigmoid"

    def test_should_get_sklearn_kernel_rbf(self) -> None:
        svm = SupportVectorMachineClassifier(c=2, kernel=SupportVectorMachineClassifier.Kernel.RadialBasisFunction())
        assert isinstance(svm.kernel, SupportVectorMachineClassifier.Kernel.RadialBasisFunction)
        rbf_kernel = svm.kernel._get_sklearn_kernel()
        assert rbf_kernel == "rbf"

    def test_should_get_kernel_name(self) -> None:
        svm = SupportVectorMachineClassifier(c=2, kernel=SupportVectorMachineClassifier.Kernel.Linear())
        assert svm._get_kernel_name() == "linear"

        svm = SupportVectorMachineClassifier(c=2, kernel=SupportVectorMachineClassifier.Kernel.Polynomial(degree=2))
        assert svm._get_kernel_name() == "poly"

        svm = SupportVectorMachineClassifier(c=2, kernel=SupportVectorMachineClassifier.Kernel.Sigmoid())
        assert svm._get_kernel_name() == "sigmoid"

        svm = SupportVectorMachineClassifier(c=2, kernel=SupportVectorMachineClassifier.Kernel.RadialBasisFunction())
        assert svm._get_kernel_name() == "rbf"

    def test_should_get_kernel_name_invalid_kernel_type(self) -> None:
        svm = SupportVectorMachineClassifier(c=2)
        with pytest.raises(TypeError, match="Invalid kernel type."):
            svm._get_kernel_name()
