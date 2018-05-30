import tensorflow as tf
import sonnet as snt

__all__ = ['LayerNormalization']


class LayerNormalization(snt.AbstractModule):
    def __init__(self,
                 eps=1e-5,
                 initializers=None,
                 partitioners=None,
                 regularizers=None,
                 name="layer_normalization"):
        super(LayerNormalization, self).__init__(name=name)
        with self._enter_variable_scope():
            self._layer_norm = snt.LayerNorm(eps=eps,
                                             initializers=initializers,
                                             partitioners=partitioners,
                                             regularizers=regularizers,
                                             name=f'{name}_core')

    def _build(self, inputs):
        """Connects the LayerNorm module into the graph.

        Args:
            inputs: a Tensor of shape `[batch_size, ..., layer_dim]`.

        Returns:
            normalized: layer normalized outputs with same shape as inputs.
        """

        inputs_shape = inputs.get_shape().as_list()
        hidden_size = inputs_shape[-1]
        reshaped_inputs = tf.reshape(inputs, shape=[-1, hidden_size])
        reshaped_normalized = self._layer_norm(reshaped_inputs)
        normalized = tf.reshape(reshaped_normalized, shape=[-1] + inputs_shape[1:])
        return normalized
