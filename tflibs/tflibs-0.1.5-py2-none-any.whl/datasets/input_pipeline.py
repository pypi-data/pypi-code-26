"""
    Input pipeline
"""

import tensorflow as tf


def build_input_fn(batch_size, map_fn=None, global_step=None, num_elements=None, shuffle_and_repeat=True):
    dataset = dataset.apply(tf.contrib.data.map_and_batch(
        map_func=map_fn, batch_size=batch_size))

    def input_fn(dataset):

        if shuffle_and_repeat:
            dataset = dataset.apply(tf.contrib.data.shuffle_and_repeat(batch_size * 50))

        if global_step:
            dataset = dataset.skip((global_step - 1) * batch_size)

        dataset = dataset.apply(tf.contrib.data.batch_and_drop_remainder(batch_size))
        dataset = dataset.prefetch(buffer_size=batch_size * 20)

        iterator = dataset.make_one_shot_iterator()

        return iterator.get_next()
