from keras.models import Sequential
import re

def _get_relevant_params(dict_obj, scope_object=None):
    relevant_params = ['batch_size',
                        'epochs',
                        'initial_epoch',
                        'loss',
                        'loss_weights',
                        'metrics',
                        'metrics_names',
                        'optimizer',
                        'shuffle',
                        'steps_per_epoch',
                        'use_multiprocessing',
                        'stop_training',
                        'supports_masking',
                        'validation_split',
                        'validation_steps',
                        'weighted_metrics']
    result = {}

    #Extact the relevant link
    for rp in relevant_params:
        try:
            if scope_object:
                # check value is number or string
                try:
                    value = float(dict_obj[rp])
                    result[rp] = value
                except (ValueError, TypeError):
                    value = dict_obj[rp]
                    result[rp] = value

                    #Replace if the value is in scope object
                    value = scope_object[value]
                    result[rp] = value
            else:
                result[rp] = dict_obj[rp]
        except (KeyError, TypeError):
            pass

    return result

def _get_layer_info(layers):
    result = []
    for layer in layers:
        layer_name = "%s (%s)" %  (layer.name, layer.__class__.__name__)
        output_shape = str(layer.output_shape)
        params = layer.count_params()
        tag =   layer.tag if layer.tag else ''

        result.append([layer_name, output_shape, params, tag])

    return result


def get_compile_params(text):
    compile_regex = re.compile('.*compile(.*)')
    compile_match = compile_regex.search(text)
    if compile_match:
        return __parse_param_string(compile_match.group(1))

    return None

def get_fit_params(text):
    fit_regex = re.compile('.*fit(.*)')
    fit_match = fit_regex.search(text)
    if fit_match:
        return __parse_param_string(fit_match.group(1))

    return None


def __parse_param_string(text):
    result = {}
    open_sqbracket_flag = False
    el = ''
    text_array = []

    # Seperate the parameters into a list
    for c in text:
        if c == '[':
            open_sqbracket_flag = True
        elif  c == ']':
            open_sqbracket_flag = False

        if c in (',', ')') and not open_sqbracket_flag:
            text_array.append(el)
            el = ''

        if c.isalnum() or c in ('=','_','.') or ( c == ',' and open_sqbracket_flag):
            el += c

    # Convert it to dict
    for text in text_array:
        param_split = text.split('=')
        try:
            result[param_split[0]] = param_split[1]
        except IndexError:
            pass

    return result
