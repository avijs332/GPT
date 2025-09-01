import tensorflow as tf
from keras.saving import register_keras_serializable
from keras.layers import Layer

@register_keras_serializable()
class ApplyMask(Layer):
    def call(self, inputs):
        logits, mask_input = inputs
        return tf.where(mask_input > 0, logits, -1e9)