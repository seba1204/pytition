"""Mixin defining a subscription interface."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any


class HasSubscribe:
    """
    Abstract mixin that defines a subscription interface.

    Classes inheriting from this mixin must implement the `subscribe` method.

    Notes
    -----
    This mixin is abstract and should not be instantiated directly.
    """

    @abstractmethod
    def subscribe(self, user: Any, **kwargs: Any) -> None:
        """
        Abstract method to handle user subscription.

        This method must be implemented by any subclass to define how
        a user subscribes to the specific model instance.

        Parameters
        ----------
        user : Any
            The user object (or any entity) subscribing to the instance.
        **kwargs : Any
            Additional keyword arguments for the subscription process.

        Raises
        ------
        NotImplementedError
            If the subclass does not implement this method.
        """
        raise NotImplementedError("Subclasses must implement the 'subscribe' method.")
