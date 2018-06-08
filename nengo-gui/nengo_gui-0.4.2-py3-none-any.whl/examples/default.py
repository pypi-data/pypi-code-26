import nengo
import nengo_spa as spa



model = spa.Network()
with model:

    stim = spa.Transcode('X', output_vocab=32)
