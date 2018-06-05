import tensorflow as tf



class CharEntityExtractor:

    def __init__(self, entity_name, model_dir):
        self.entity_name = entity_name
        self.model_dir = model_dir
        self.max_chars = 320
        self.batch_size = 32
        self.initial_step = 1e-3
        self.num_units = 32
        self.session = tf.Session()

    def create_network(self):
        with tf.name_scope(self.entity_name):
            self.x = tf.placeholder(tf.int8, [self.batch_size, self.max_chars, 1], name="x")
            self.y = tf.placeholder(tf.float16, [self.batch_size, self.max_chars, 1], name="y")

            with tf.name_scope("encoder_fwd"):
                self.cell_fwd = tf.nn.rnn_cell.GRUCell(
                    num_units=self.num_units,
                    activation=tf.nn.relu,
                )

            with tf.name_scope("encoder_bwd"):
                self.cell_bwd = tf.nn.rnn_cell.GRUCell(
                    num_units=self.num_units,
                    activation=tf.nn.relu,
                )

            with tf.name_scope("encoder"):
                self.encoder_out, self.encoder_state = tf.nn.bidirectional_dynamic_rnn(
                    cell_fw=self.cell_fwd,
                    cell_bw=self.cell_bwd,
                    inputs=self.x,
                    dtype=tf.float16,
                )

            self.y_ = None
