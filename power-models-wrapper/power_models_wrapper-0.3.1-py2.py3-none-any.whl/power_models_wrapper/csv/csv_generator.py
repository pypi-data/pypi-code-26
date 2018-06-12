import io
import csv
import numpy as np
from calendar import month_name
from power_models_wrapper.data_transformation.all_pass_filter import AllPassFilter

class CsvGenerator:

    TIME_STEPS = 24
    DAY_TYPE = ["week", "peak", "weekend"]
    NUMBER_OF_MONTHS = 12
    VARIABLE_TITLES = {"dg_output_dercam_ui": "Generator Active Power Output",
                       "pv_output_dercam_ui": "PV Active Power Output",
                       "bat_output_dercam_ui": "Battery Active Power Output",
                       "p_g": "Generator Active Power Output",
                       "p_pv": "PV Active Power Output",
                       "p_w": "Wind Active Power Output",
                       "p_b": "Battery Active Power Output",
                       "sc_b": "Battery State of Charge"}

    def __init__(self, filter = None):
        if filter == None:
            self.filter = AllPassFilter()
        else:
            self.filter = filter

    def generate(self, data_dictionary, variable_names, number_of_months_in_data = 12, number_of_day_type_in_data = 3):

        data_dictionary = self.__apply_filter(data_dictionary)

        output = io.StringIO()
        writer = csv.writer(output, quoting = csv.QUOTE_NONNUMERIC)

        for key, value in variable_names.items():

            writer.writerow(["*** " + self.VARIABLE_TITLES[key]])

            for node_index, node_array in enumerate(data_dictionary[key]):

                node_number = node_index + 1

                if value == "timeseries":
                    divided_data = self.divide_for_timeseries(node_array)
                    #print("divided_data: %s" % (divided_data))

                    for index, data_row in enumerate(divided_data):
                        if index % number_of_months_in_data == 0:
                            #writer.writerow(["node" + str(node_number), self.DAY_TYPE[(index * number_of_months_in_data) % len(self.DAY_TYPE)]])
                            writer.writerow(["node" + str(node_number), self.DAY_TYPE[self.get_index_for_day_type(index, number_of_months_in_data)]])
                        writer.writerow(data_row)
                        #if index != 0 and index % (number_of_months_in_data * len(self.DAY_TYPE) - 1) == 0:
                        #    node_number +=1

        return output.getvalue()

    def divide_for_timeseries(self, data):
        #print("In divide_for_timeseries: data: %s" % (data))
        #print("In divide_for_timeseries: type(data): %s" % (type(data)))
        #print("In divide_for_timeseries: len(data): %s" % (len(data)))

        reshaped_data = np.reshape(data, (len(data) // self.TIME_STEPS, self.TIME_STEPS)).tolist()
        result_data_with_original_order = self.__add_month_name(reshaped_data)
        result_data = self.__rearrange_rows(result_data_with_original_order)

        return result_data
        #return {"week": result_data[0], "peak": result_data[1], "weekend": result_data[2]}

    def __add_month_name(self, reshaped_data):
        return [[month_name[index//len(self.DAY_TYPE) + 1]] + row_list for index, row_list in enumerate(reshaped_data)]

    def __rearrange_rows(self, data):
        result = []
        for index, day_type in enumerate(self.DAY_TYPE):
            result = result + data[index:len(data):len(self.DAY_TYPE)]
        #print("__rearrange_rows method: result: %s" % (result))
        return result;

    # Note: Made it public in order to access from unit test.
    def get_index_for_day_type(self, index, number_of_months_in_data):
        return index // number_of_months_in_data

    def __apply_filter(self, data_dictionary):
       return self.filter.filter(data_dictionary)
