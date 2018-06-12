import os
import logging
import time
from collections import defaultdict

import torch
from torch import nn, optim
from tensorboardX import SummaryWriter

from . import utils, config


class TrainingStats:
    TIMER_KEY = "__timer__"

    def __init__(self):
        self._samples = defaultdict(list)
        self._start = None

    def add(self, name, value):
        self._samples[name].append(value)

    def get(self, name):
        values = self._samples[name]
        if values:
            avg = sum(values) / len(values)
        else:
            avg = 0.0
        self._samples.pop(name)
        return avg

    def __iter__(self):
        names = list(self._samples.keys())
        for name in names:
            yield name, self.get(name)

    def start_timer(self):
        self._start = time.time()

    def stop_timer(self):
        if self._start is None:
            return
        elapsed = time.time() - self._start
        self._samples[self.TIMER_KEY].append(elapsed)

    def get_timer(self):
        sec_per_step = self.get(self.TIMER_KEY)
        return 1 / sec_per_step


class Model:
    def __init__(self, network, model_dir):
        logging.info(network)
        self.network = network
        if torch.cuda.is_available():
            self.network = self.network.cuda()

        self.optimizer = optim.Adam(
                filter(lambda p: p.requires_grad, self.network.parameters()),
                lr=config.learning_rate)

        self.step = 0
        self.model_dir = model_dir

    def save(self):
        states = {
            "step": self.step,
            "network": self.network.state_dict(),
            "optimizer": self.optimizer.state_dict(),
        }
        utils.save_checkpoint(self.model_dir, self.step, states, config.keep_checkpoint_max)

    def restore(self):
        states = utils.load_checkpoint(self.model_dir)
        if states:
            logging.info("Restoring the saved states...")
            self.step = states["step"] + 1
            self.network.load_state_dict(states["network"])
            self.optimizer.load_state_dict(states["optimizer"])

    def train(self, train_dataset, eval_dataset=None):
        stats = TrainingStats()
        writer = SummaryWriter(log_dir=self.model_dir)
        for batch in train_dataset:
            stats.start_timer()

            # Forward
            self.network.train()
            _, loss = self.network(**batch)

            # Backpropagation
            self.optimizer.zero_grad()
            loss.backward()
            if config.clip_gradients:
                grad_norm = nn.utils.clip_grad_norm_(self.network.parameters(), config.clip_gradients)
            self.optimizer.step()

            stats.stop_timer()

            # Log summary
            stats.add("loss", loss.item())
            if self.step % config.summary_interval == 0:
                avg_loss = stats.get("loss")
                step_per_sec = stats.get_timer()
                writer.add_scalar("loss", avg_loss, self.step)
                writer.add_scalar("train/step_per_sec", step_per_sec, self.step)
                if config.clip_gradients:
                    writer.add_scalar("train/grad_norm", grad_norm, self.step)
                logging.info("step={} loss={:.3f} step/sec={:.3f}".format(self.step, avg_loss, step_per_sec))

            # Evaluate
            if eval_dataset and config.evaluation_interval \
                    and self.step % config.evaluation_interval == 0:
                self.evaluate(eval_dataset)

            # Save a checkpoint
            if config.checkpoint_interval and self.step % config.checkpoint_interval == 0:
                self.save()

            self.step += 1

    def evaluate(self, dataset):
        stats = TrainingStats()
        writer = SummaryWriter(log_dir=os.path.join(self.model_dir, "eval"))

        for step, batch in zip(utils.range_step(1, config.eval_steps), dataset):
            with torch.no_grad():
                self.network.eval()
                predictions, loss = self.network(**batch)

            # This values will be averaged the end of evaluation.
            stats.add("loss", loss.item())
            metrics = self.evaluate_hook(step, predictions, **batch)
            if metrics:
                for name, value in metrics.items():
                    stats.add(name, value)

            logging.info("Evaluation step [{}/{}]".format(step, config.eval_steps))

        # Write loss and metrics to tensorboard and log.
        avg_loss = stats.get("loss")
        writer.add_scalar("loss", avg_loss, self.step)
        metrics_msg = ""
        for name, value in stats:
            writer.add_scalar("metrics/" + name, value, self.step)
            metrics_msg += " {}={:.3f}".format(name, value)

        logging.info("Evaluation result: loss={:.3f}{}".format(avg_loss, metrics_msg))

    def evaluate_hook(self, step, predictions, **kwargs):
        pass

    def predict(self):
        raise NotImplemented
