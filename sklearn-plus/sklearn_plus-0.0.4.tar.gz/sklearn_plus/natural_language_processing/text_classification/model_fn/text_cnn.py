
import tensorflow as tf

from sklearn_plus.utils import const


def model_fn(features, labels, mode, params):

    filter_sizes = params.filter_sizes
    embed_dim = params.embed_dim
    num_filters = params.num_filters
    num_filters_total = num_filters * len(filter_sizes)
    dropout_keep_prob = params.dropout_keep_prob
    l2_lambda = params.l2_lambda
    decay_steps = params.decay_steps
    decay_rate = params.decay_rate

    global_step = tf.Variable(0, trainable=False, name="Global_Step")

    max_document_length = features[const.word_ids].shape[1]

    initializer = tf.random_normal_initializer(stddev=0.1)

    word_vectors = tf.contrib.layers.embed_sequence(
        features[const.word_ids],
        vocab_size=params.vocab_size,
        embed_dim=embed_dim)

    word_vectors_expanded = tf.expand_dims(word_vectors, -1)

    pooled_outputs = []
    for i, filter_size in enumerate(filter_sizes):
        with tf.name_scope("convolution-pooling-%s" % filter_size):
            filter = tf.get_variable(
                "filter-%s" % filter_size,
                [filter_size, embed_dim, 1, num_filters],
                initializer=initializer)

            conv = tf.nn.conv2d(
                word_vectors_expanded,
                filter,
                strides=[1, 1, 1, 1],
                padding="VALID",
                name="conv"
                )

            b = tf.get_variable("b-%s" % filter_size, [num_filters])
            h = tf.nn.relu(tf.nn.bias_add(conv, b), "relu")
            pooled = tf.nn.max_pool(
                h,
                ksize=[1, max_document_length-filter_size+1, 1, 1],
                strides=[1, 1, 1, 1],
                padding='VALID',
                name="pool")
            pooled_outputs.append(pooled)

    h_pool = tf.concat(pooled_outputs, 3)
    h_pool_flat = tf.reshape(h_pool, [-1, num_filters_total])

    h_drop = tf.nn.dropout(h_pool_flat, keep_prob=dropout_keep_prob)

    W_projection = tf.get_variable(
        "W_projection",
        shape=[num_filters_total, params.class_num],
        initializer=initializer)
    b_projection = tf.get_variable("b_projection", shape=[params.class_num])
    logits = tf.matmul(h_drop, W_projection) + b_projection

    predicted_classes = tf.argmax(logits, 1)

    if mode == tf.estimator.ModeKeys.PREDICT:
        return tf.estimator.EstimatorSpec(
            mode=mode,
            predictions={
                'class': predicted_classes,
                'prob': tf.nn.softmax(logits)
            })
    loss = tf.losses.sparse_softmax_cross_entropy(labels=labels, logits=logits)
    loss = tf.reduce_mean(loss)
    l2_losses = tf.add_n(
        [tf.nn.l2_loss(v) for v in tf.trainable_variables()
            if 'bias' not in v.name]) * l2_lambda
    loss = loss+l2_losses

    if mode == tf.estimator.ModeKeys.TRAIN:
        learning_rate = tf.train.exponential_decay(
            params.learning_rate,
            global_step,
            decay_steps,
            decay_rate,
            staircase=True)

        optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
        train_op = optimizer.minimize(
            loss, global_step=tf.train.get_global_step())
        return tf.estimator.EstimatorSpec(mode, loss=loss, train_op=train_op)

    eval_metric_ops = {
        'accuracy': tf.metrics.accuracy(
            labels=labels, predictions=predicted_classes)
    }
    return tf.estimator.EstimatorSpec(
        mode=mode,
        loss=loss,
        eval_metric_ops=eval_metric_ops)
