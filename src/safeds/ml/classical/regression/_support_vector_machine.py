from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from sklearn.svm import SVR as sk_SVR  # noqa: N811

from safeds.exceptions import ClosedBound, OpenBound, OutOfBoundsError
from safeds.ml.classical._util_sklearn import fit, predict
from safeds.ml.classical.regression import Regressor

if TYPE_CHECKING:
    from sklearn.base import RegressorMixin

    from safeds.data.tabular.containers import Table, TaggedTable


class SupportVectorMachineKernel(ABC):
    """The abstract base class of the different subclasses supported by the `Kernel`."""

    @abstractmethod
    def _get_sklearn_kernel(self) -> object:
        """
        Get the kernel of the given SupportVectorMachine.

        Returns
        -------
        object
        The kernel of the SupportVectorMachine.
        """


class SupportVectorMachineRegressor(Regressor):
    """
    Support vector machine.

    Parameters
    ----------
    c: float
        The strength of regularization. Must be strictly positive.
    kernel: SupportVectorMachineKernel | None
        The type of kernel to be used. Defaults to None.

    Raises
    ------
    OutOfBoundsError
        If `c` is less than or equal to 0.
    """

    def __init__(self, *, c: float = 1.0, kernel: SupportVectorMachineKernel | None = None) -> None:
        # Internal state
        self._wrapped_regressor: sk_SVR | None = None
        self._feature_names: list[str] | None = None
        self._target_name: str | None = None

        # Hyperparameters
        if c <= 0:
            raise OutOfBoundsError(c, name="c", lower_bound=OpenBound(0))
        self._c = c
        self._kernel = kernel

    @property
    def c(self) -> float:
        """
        Get the regularization strength.

        Returns
        -------
        result: float
            The regularization strength.
        """
        return self._c

    @property
    def kernel(self) -> SupportVectorMachineKernel | None:
        """
        Get the type of kernel used.

        Returns
        -------
        result: SupportVectorMachineKernel | None
            The type of kernel used.
        """
        return self._kernel

    class Kernel:
        class Linear(SupportVectorMachineKernel):
            def _get_sklearn_kernel(self) -> str:
                """
                Get the name of the linear kernel.

                Returns
                -------
                result: str
                    The name of the linear kernel.
                """
                return "linear"

        class Polynomial(SupportVectorMachineKernel):
            def __init__(self, degree: int):
                if degree < 1:
                    raise OutOfBoundsError(degree, name="degree", lower_bound=ClosedBound(1))
                self._degree = degree

            def _get_sklearn_kernel(self) -> str:
                """
                Get the name of the polynomial kernel.

                Returns
                -------
                result: str
                    The name of the polynomial kernel.
                """
                return "poly"

        class Sigmoid(SupportVectorMachineKernel):
            def _get_sklearn_kernel(self) -> str:
                """
                Get the name of the sigmoid kernel.

                Returns
                -------
                result: str
                    The name of the sigmoid kernel.
                """
                return "sigmoid"

        class RadialBasisFunction(SupportVectorMachineKernel):
            def _get_sklearn_kernel(self) -> str:
                """
                Get the name of the radial basis function (RBF) kernel.

                Returns
                -------
                result: str
                    The name of the RBF kernel.
                """
                return "rbf"

    def _get_kernel_name(self) -> str:
        """
        Get the name of the kernel.

        Returns
        -------
        result: str
            The name of the kernel.

        Raises
        ------
        TypeError
            If the kernel type is invalid.
        """
        if isinstance(self.kernel, SupportVectorMachineRegressor.Kernel.Linear):
            return "linear"
        elif isinstance(self.kernel, SupportVectorMachineRegressor.Kernel.Polynomial):
            return "poly"
        elif isinstance(self.kernel, SupportVectorMachineRegressor.Kernel.Sigmoid):
            return "sigmoid"
        elif isinstance(self.kernel, SupportVectorMachineRegressor.Kernel.RadialBasisFunction):
            return "rbf"
        else:
            raise TypeError("Invalid kernel type.")

    def fit(self, training_set: TaggedTable) -> SupportVectorMachineRegressor:
        """
        Create a copy of this regressor and fit it with the given training data.

        This regressor is not modified.

        Parameters
        ----------
        training_set : TaggedTable
            The training data containing the feature and target vectors.

        Returns
        -------
        fitted_regressor : SupportVectorMachineRegressor
            The fitted regressor.

        Raises
        ------
        LearningError
            If the training data contains invalid values or if the training failed.
        UntaggedTableError
            If the table is untagged.
        NonNumericColumnError
            If the training data contains non-numerical values.
        MissingValuesColumnError
            If the training data contains missing values.
        DatasetMissesDataError
            If the training data contains no rows.
        """
        wrapped_regressor = self._get_sklearn_regressor()
        fit(wrapped_regressor, training_set)

        result = SupportVectorMachineRegressor(c=self._c, kernel=self._kernel)
        result._wrapped_regressor = wrapped_regressor
        result._feature_names = training_set.features.column_names
        result._target_name = training_set.target.name

        return result

    def predict(self, dataset: Table) -> TaggedTable:
        """
        Predict a target vector using a dataset containing feature vectors. The model has to be trained first.

        Parameters
        ----------
        dataset : Table
            The dataset containing the feature vectors.

        Returns
        -------
        table : TaggedTable
            A dataset containing the given feature vectors and the predicted target vector.

        Raises
        ------
        ModelNotFittedError
            If the model has not been fitted yet.
        DatasetContainsTargetError
            If the dataset contains the target column already.
        DatasetMissesFeaturesError
            If the dataset misses feature columns.
        PredictionError
            If predicting with the given dataset failed.
        NonNumericColumnError
            If the dataset contains non-numerical values.
        MissingValuesColumnError
            If the dataset contains missing values.
        DatasetMissesDataError
            If the dataset contains no rows.
        """
        return predict(self._wrapped_regressor, dataset, self._feature_names, self._target_name)

    def is_fitted(self) -> bool:
        """
        Check if the regressor is fitted.

        Returns
        -------
        is_fitted : bool
            Whether the regressor is fitted.
        """
        return self._wrapped_regressor is not None

    def _get_sklearn_regressor(self) -> RegressorMixin:
        """
        Return a new wrapped Regressor from sklearn.

        Returns
        -------
        wrapped_regressor: RegressorMixin
            The sklearn Regressor.
        """
        return sk_SVR(C=self._c)
