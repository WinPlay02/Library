from __future__ import annotations

from typing import TYPE_CHECKING

from sklearn.ensemble import GradientBoostingRegressor as sk_GradientBoostingRegressor

from safeds.ml.classical._util_sklearn import fit, predict

from ._regressor import Regressor

if TYPE_CHECKING:
    from safeds.data.tabular.containers import Table, TaggedTable


class GradientBoosting(Regressor):
    """Gradient boosting regression.

    Parameters
    ----------
    learning_rate : float
        The larger the value, the more the model is influenced by each additional tree. If the learning rate is too
        low, the model might underfit. If the learning rate is too high, the model might overfit.

    Raises
    ------
    ValueError
        If `learning_rate` is non-positive.
    """

    def __init__(self, learning_rate: float = 0.1) -> None:
        # Validation
        if learning_rate <= 0:
            raise ValueError("The learning rate has to be greater than 0.")

        # Hyperparameters
        self._learning_rate = learning_rate

        # Internal state
        self._wrapped_regressor: sk_GradientBoostingRegressor | None = None
        self._feature_names: list[str] | None = None
        self._target_name: str | None = None

    def fit(self, training_set: TaggedTable) -> GradientBoosting:
        """
        Create a copy of this regressor and fit it with the given training data.

        This regressor is not modified.

        Parameters
        ----------
        training_set : TaggedTable
            The training data containing the feature and target vectors.

        Returns
        -------
        fitted_regressor : GradientBoosting
            The fitted regressor.

        Raises
        ------
        LearningError
            If the training data contains invalid values or if the training failed.
        """
        wrapped_regressor = sk_GradientBoostingRegressor(learning_rate=self._learning_rate)
        fit(wrapped_regressor, training_set)

        result = GradientBoosting(learning_rate=self._learning_rate)
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