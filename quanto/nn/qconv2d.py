from typing import Optional

import torch

from ..tensor import Optimizer, QTensor, qtype
from .qmodule import QModuleMixin, register_qmodule


__all__ = ["QConv2d"]


@register_qmodule(torch.nn.Conv2d)
class QConv2d(QModuleMixin, torch.nn.Conv2d):
    @classmethod
    def qcreate(
        cls,
        module,
        weights: qtype,
        activations: Optional[qtype] = None,
        optimizer: Optional[Optimizer] = None,
        input_optimizer: Optional[Optimizer] = None,
        output_optimizer: Optional[Optimizer] = None,
    ):
        return cls(
            in_channels=module.in_channels,
            out_channels=module.out_channels,
            kernel_size=module.kernel_size,
            stride=module.stride,
            padding=module.padding,
            dilation=module.dilation,
            groups=module.groups,
            bias=module.bias is not None,
            padding_mode=module.padding_mode,
            dtype=module.weight.dtype,
            device=module.weight.device,
            weights=weights,
            activations=activations,
            optimizer=optimizer,
            input_optimizer=input_optimizer,
            output_optimizer=output_optimizer,
        )

    def qforward(self, input: torch.Tensor) -> torch.Tensor:
        if self.activation_qtype is not None and not isinstance(input, QTensor):
            # Quantize tensor to be able to take advantage of accelerated conv2d
            input = QTensor.quantize(
                input,
                qtype=self.activation_qtype,
                axis=None,
                group_size=None,
                scale=self.input_scale,
                optimizer=self.input_optimizer,
            )
        # We always use quantized weights
        return self._conv_forward(input, self.qweight, self.bias)
