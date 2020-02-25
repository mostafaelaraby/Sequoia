from abc import ABC, abstractmethod
from typing import Any, Tuple, List, Generic, TypeVar

import torch
from torch import Tensor, nn, optim
from torch.nn import functional as F
from dataclasses import dataclass


class AuxiliaryTask(nn.Module, ABC):
    """ Represents an additional loss to apply to a `Classifier`.

    The main logic should be implemented in the `get_loss` method.

    In general, it should apply some deterministic transformation to its input,
    and treat that same transformation as a label to predict.
    That loss should be backpropagatable through the feature extractor (the
    `encoder` attribute). 
    """

    @dataclass
    class Options:
        """Settings for this Auxiliary Task. """
        # Coefficient used to scale the task loss before adding it to the total.
        coefficient: float = 0.

    def __init__(self, encoder: nn.Module, classifier: nn.Module, options: Options=None):
        """Creates a new Auxiliary Task to further train the encoder.
        
        Should use the `encoder` and `classifier` components of the parent
        `Classifier` instance.
        
        NOTE: Since this object will be stored inside the `tasks` list in the
        model, we can't pass a reference to the parent here, otherwise the
        parent would hold a reference to itself inside its `.modules()`. 
        
        Parameters
        ----------
        - encoder : nn.Module
        
            The encoder (or feature extractor) of the parent `Classifier`.
        - classifier : nn.Module
        
            The classifier (logits) layer of the parent `Classifier`.
        - options : TaskOptions, optional, by default None
        
            The `TaskOptions` related to this task, containing the loss 
            coefficient used to scale this task, as well as any other additional
            hyperparameters specific to this `AuxiliaryTask`.
        """
        super().__init__()
        self.encoder = encoder
        self.classifier = classifier
        self.options: AuxiliaryTask.Options = options or AuxiliaryTask.Options()

    @abstractmethod
    def get_loss(self, x: Tensor, h_x: Tensor=None, y_pred: Tensor=None, y: Tensor=None) -> Tensor:
        """Calculates the Auxiliary loss for the input `x`.ABC
        
        The parameters `h_x`, `y_pred` are given for convenience, so we don't
        re-calculate the forward pass multiple times on the same input.
        
        Parameters
        ----------
        - x : Tensor
        
            The input samples.ABC
        - h_x : Tensor, optional, by default None
        
            The hidden vector, or hidden features, which corresponds to the
            output of the feature extractor (should be equivalent to 
            `self.encoder(x)`). Given for convenience, when available.ABC
        - y_pred : Tensor, optional, by default None
        
            The predicted (raw/unscaled) scores for each class, which 
            corresponds to the output of the classifier layer of the parent
            Model. (should be equivalent to `self.classifier(self.encoder(x))`). 
        - y : Tensor, optional, by default None
        
            The true labels for each sample. Will generally be None, as we don't
            generally use the label for Auxiliary Tasks.
            TODO: Is there any case where we might use the labels here?
        
        Returns
        -------
        Tensor
            The loss, not scaled.
        """
        pass
    
    @property
    def coefficient(self) -> float:
        return self.options.coefficient