import abc
from typing import *

from .base import *

__all__ = ('GeneratorPrimitiveBase',)


class GeneratorPrimitiveBase(PrimitiveBase[None, Output, Params]):
    """
    A base class for primitives which have to be fitted before they can start
    producing (useful) outputs, but they are fitted only on output data.
    Moreover, they do not accept any inputs to generate outputs, which is
    represented as a list of ``None`` values to signal how many outputs is
    requested.

    A base class for primitives which are not fitted at all and can
    simply produce (useful) outputs from inputs directly. As such they
    also do not have any state (params).

    This class is parametrized using only by two type variables, ``Output`` and ``Params``.
    """

    @abc.abstractmethod
    def produce(self, *, inputs: Sequence[None]) -> Sequence[Output]:
        pass

    @abc.abstractmethod
    def set_training_data(self, *, inputs: None = None, outputs: Sequence[Output]) -> None:
        pass
