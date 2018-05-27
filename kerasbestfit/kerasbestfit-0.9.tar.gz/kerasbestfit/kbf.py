from keras.callbacks import EarlyStopping, Callback
import datetime

class _FBFCheckpoint(Callback):
    def __init__(self, metric='val_acc', save_best=False, save_path=None, best_metric_val_so_far=0.0, snifftest_max_epoch=0, snifftest_metric_val=-1.0,
                 show_progress=True, format_metric_val='{:1.10f}', finish_by=0.0, logmsg_callback=None, progress_callback=None):
        super().__init__()
        self.finish_by = finish_by
        self.save_best = save_best
        self.save_path = save_path
        self.previous_best_metric_val_so_far = best_metric_val_so_far
        self.best_metric_val_so_far = best_metric_val_so_far
        self.current_epoch = 0

        if metric=='val_acc':
            self.current_epoch_metric_val = 0
            self.current_epoch_max_metric_val = 0
            self.best_metric_val = 0
            self.saved_at_metric_val = 0
        elif metric=='val_loss':
            self.current_epoch_metric_val = 100
            self.current_epoch_max_metric_val = 100
            self.best_metric_val = 100
            self.saved_at_metric_val = 100

        self.is_best = False
        self.best_epoch = 0
        self.full_log = []
        self.saved = False
        self.saved_at_epoch = 0
        self.snifftest_max_epoch = snifftest_max_epoch
        self.snifftest_metric_val = snifftest_metric_val
        self.snifftest_failed = False
        self.show_progress = show_progress
        self.format_metric_val = format_metric_val
        self.metric = metric
        self.expired = False
        self.logmsg_callback=logmsg_callback
        self.progress_callback=progress_callback

    def save_model(self):
        # save model structure as .json and weights as .hdf5 only if snifftest has passed
        self.saved = True
        self.saved_at_epoch = self.best_epoch
        self.saved_at_metric_val = self.best_metric_val
        model_json = self.model.to_json()
        with open(self.save_path + 'model.json', "w") as json_file:
            json_file.write(model_json)
        self.model.save_weights(self.save_path + 'model.hdf5')

    def on_epoch_end(self, epoch, logs=()):
        if not self.expired:
            logs = logs or {}
            logs['epoch'] = epoch
            self.full_log.append(logs)
            self.saved_at_epoch = False
            self.is_best = False
            self.saved = False
            self.current_epoch = epoch

            if self.metric=='val_acc':
                self.current_epoch_metric_val = logs.get(self.metric)
                self.snifftest_failed = (self.current_epoch >= self.snifftest_max_epoch) and (
                    self.snifftest_metric_val >= self.current_epoch_metric_val)
                self.model.stop_training = self.snifftest_failed
                if self.snifftest_failed == False:
                    if self.current_epoch_metric_val > self.best_metric_val:
                        self.best_metric_val = self.current_epoch_metric_val
                        self.best_epoch = epoch
                        self.is_best = True
                        if self.best_metric_val > self.best_metric_val_so_far:
                            self.previous_best_metric_val = self.best_metric_val_so_far
                            self.best_metric_val_so_far = self.best_metric_val
                            #save model structure as .json and weights as .hdf5 only if snifftest has passed
                            if (self.current_epoch >= self.snifftest_max_epoch) and self.save_best:
                                self.save_model()
            elif self.metric=='val_loss':
                self.current_epoch_metric_val = logs.get(self.metric)
                self.snifftest_failed = (self.current_epoch >= self.snifftest_max_epoch) and (
                    self.snifftest_metric_val <= self.current_epoch_metric_val)
                self.model.stop_training = self.snifftest_failed
                if self.snifftest_failed == False:
                    if self.current_epoch_metric_val < self.best_metric_val:
                        self.best_metric_val = self.current_epoch_metric_val
                        self.best_epoch = epoch
                        self.is_best = True
                        if self.best_metric_val < self.best_metric_val_so_far:
                            self.previous_best_metric_val = self.best_metric_val_so_far
                            self.best_metric_val_so_far = self.best_metric_val
                            #save model structure as .json and weights as .hdf5 only if snifftest has passed
                            if (self.current_epoch >= self.snifftest_max_epoch) and self.save_best:
                                self.save_model()

            if self.show_progress:
                cva = self.format_metric_val.format(self.current_epoch_metric_val)
                bsf = self.format_metric_val.format(self.best_metric_val_so_far)
                if self.metric=='val_acc':
                    is_best_so_far = self.is_best and (self.best_metric_val_so_far > self.previous_best_metric_val_so_far)
                elif self.metric=='val_loss':
                    is_best_so_far = self.is_best and (self.best_metric_val_so_far < self.previous_best_metric_val_so_far)
                flags = '  '
                msg = ''
                if self.is_best:
                    flags = '* '
                if is_best_so_far:
                    flags = '*!'
                if self.saved:
                    msg = ' Saved '
                if self.snifftest_failed:
                    msg = ' Snifftest failed '
                if self.logmsg_callback is not None:
                    self.logmsg_callback(f'  e{self.current_epoch}: {self.metric}={cva} {flags} bsf={bsf} {msg}')

            if (self.finish_by != 0) and (datetime.datetime.today() >= self.finish_by):
                fmt = "%a %b %d %H:%M:%S %Y"
                self.logmsg_callback(f'  Finish_by time has been reached.  Fit terminated at {self.finish_by.strftime(fmt)}')
                self.model.stop_training = True
                self.expired = True

            if self.progress_callback is not None:
                self.progress_callback(self.current_epoch, logs.get('acc'), logs.get('loss'), logs.get('val_acc'), logs.get('val_loss'))

# -----------------------------------------------------------------------------------------------------------------------
def find_best_fit(
        model=None,
        metric='val_acc',
        xtrain=None,
        ytrain=None,
        xval=None,
        yval=None,
        shuffle=False,
        validation_split=0,
        batch_size=1000,
        epochs=2,
        patience=5,
        snifftest_max_epoch=0,
        snifftest_metric_val=0,
        show_progress=True,
        format_metric_val='{:1.10f}',
        save_best=False,
        save_path=None,
        best_metric_val_so_far=0,
        finish_by=0,
        logmsg_callback=None,
        progress_callback=None
        ):
    # model - a compiled Keras model
    # metric - (string) - use 'val_acc' or 'val_loss'.  It will search for the best value for this metric.
    # xtrain - (numpy array) - This is passed to the Keras .fit function.  See Keras documentation for more info.
    # ytrain - (numpy array) - This is passed to the Keras .fit function.  See Keras documentation for more info.
    # xval - (numpy array) - This is passed to the Keras .fit function.  See Keras documentation for more info.
    # yval - (numpy array) - This is passed to the Keras .fit function.  See Keras documentation for more info.
    # validation_split  - (float) - set to non-zero value to split the xtrain and ytrain into additional validation
    #   datasets. If non-zero, the xval and yval params are ignored.
    #   This is passed to the Keras .fit function.  See Keras documentation for more info.
    # shuffle - (boolean) - use this to randomly select the validation split.  Only works if validation_split is not zero.
    #   This is passed to the Keras .fit function.  See Keras documentation for more info.
    # batch_size - (integer) - this is passed to the Keras .fit function.  See Keras documentation for more info.
    # epochs - (integer) - this is passed to the Keras .fit function.  See Keras documentation for more info.
    # patience - (integer) - this is passed to the Keras early stopping callback.  See Keras documentation for more info.
# snifftest_max_epoch - (integer) - set this to the epoch in which the snifftest_metric_val must be reached or else
    #   the training will be aborted.  Great for hyperparameter searchs where some parameters give recognizably horrible results.
    #   set to zero to disable the snifftest
    # snifftest_metric_val - (float) - set this to the metric value that must be reached by snifftest_max_epoch epochs.
    #   set to zero to disable the snifftest
    # show_progress - (boolean) - set to True to see training log messages.
    # format_metric_val - string) - this is the formatting used for formatting floats for training logging.
    # save_best - (boolean) - set this to True to cause the model to be saved when a new best metric val is found
    # save_path = (string) - the folder that the saved model will be saved to.  The model files will always be named
    #  'model' and give files model.json and model.hdf5
    #   EXAMPLE
    #   ".//models//
    # best_metric_val_so_far - (float) - use this to keep track which is the best metric val found so far.  This is
    #   use in the output messages to denote the ! symbol.
    # started_at - (datetime) set this to the time you are starting a training session.
    # finish_by - (float) in minutes(ex: 120.0 for 2.0 hours, 2.0 for 2 minutes, 0.25 for 25 seconds.  Training will expire started_by + finish_by.
    #   is tested after epoch completion, so if you have a time limit, plan it for time limit minus the time to complete a single epoch, so leave
    #   yourself some extra time for finishing.  Example, I have a hard total training limit of 6 hours, so I'll set the finish_by to 6*60-10 where
    #   the 10 minutes is just be be sure that the last epoch completes before the time is up.
    # logmsg_callback - (function) - a function that will be used for displaying status messages.  Requires a string parameter.
    #   EXAMPLE
    #   def log(msg=''):
    #       print(msg)
    #       return
    # progress_callback - (function) - a function that is called at the end of each epoch and contains training log data
    #   EXAMPLE
    #   def on_progress(epoch, acc, loss, val_acc, val_loss):
    #       print(epoch, acc, loss, val_acc, val_loss)
    #       return

    cbstopper = EarlyStopping(monitor=metric, patience=patience, verbose=0)
    cbcheckpoint = _FBFCheckpoint(save_best=save_best,
                                 save_path=save_path,
                                 metric=metric,
                                 best_metric_val_so_far=best_metric_val_so_far,
                                 snifftest_max_epoch=snifftest_max_epoch,
                                 snifftest_metric_val=snifftest_metric_val,
                                 show_progress=show_progress,
                                 format_metric_val=format_metric_val,
                                 finish_by=finish_by,
                                 logmsg_callback=logmsg_callback,
                                 progress_callback=progress_callback)

    # call the native fit function
    if validation_split == 0:
        history = model.fit(xtrain, ytrain,
                            batch_size=batch_size,
                            epochs=epochs,
                            verbose=0,
                            callbacks=[cbcheckpoint, cbstopper],
                            shuffle=shuffle,
                            validation_data=[xval, yval])

    else:
        history = model.fit(xtrain, ytrain,
                            batch_size=batch_size,
                            epochs=epochs,
                            verbose=0,
                            callbacks=[cbcheckpoint, cbstopper],
                            shuffle=shuffle,
                            validation_split=validation_split)

    results = {}
    results['expired'] = cbcheckpoint.expired
    results['snifftest_failed'] = cbcheckpoint.snifftest_failed
    results['is_best'] = cbcheckpoint.is_best
    results['saved'] = cbcheckpoint.saved
    results['saved_at_epoch'] = cbcheckpoint.saved_at_epoch
    results['saved_at_metric_val'] = cbcheckpoint.saved_at_metric_val
    results['best_metric_val_so_far'] = cbcheckpoint.best_metric_val_so_far
    results['best_metric_val'] = cbcheckpoint.best_metric_val
    results['best_epoch'] = cbcheckpoint.best_epoch
    results['final_epoch'] = cbcheckpoint.current_epoch
    results['history'] = history.history

    return results, cbcheckpoint.full_log