#from subprocess import run, PIPE
from power_models_wrapper.formulation_type import FormulationType
from power_models_wrapper.csv.csv_generator import CsvGenerator
from power_models_wrapper.julia_preparation import JuliaPreparation

class RemoteOffGrid:

    VARIABLE_TYPES = {"dg_output_dercam_ui": "timeseries",
                      "pv_output_dercam_ui": "timeseries",
                      "bat_output_dercam_ui": "timeseries"}
    #VARIABLE_TYPES = {"p_g": "timeseries",
    #                  "p_pv": "timeseries",
    #                  "p_w": "timeseries",
    #                  "p_b": "timeseries",
    #                  "sc_b": "timeseries"}

    def __init__(self):
        #pass
        #self.__julia_object = julia.Julia()
        #self.__julia_object.using("RemoteOffGridMicrogrids")
        julia_preparation = JuliaPreparation()
        self.__julia_object = julia_preparation.get_julia_object()

    def run(self, input_data_file_path):

        julia_code = "run_model(\"" + input_data_file_path + "\")"

        #print("julia_code: %s" % (julia_code))

        data_from_julia_code = self.__julia_object.eval(julia_code)

        #print("data_from_julia_code: %s" % (data_from_julia_code))
        #print("type(data_from_julia_code): %s" % (type(data_from_julia_code)))
        #print("len(data_from_julia_code): %s" % (len(data_from_julia_code)))
        #data_portion = data_from_julia_code["p_g"]
        #print("len(data_from_julia_code[\"p_g\"]): %s" % (len(data_from_julia_code["p_g"])))
        #print("data_portion[0]: %s" % (data_portion[0]))

        csv_generator = CsvGenerator()

        result = csv_generator.generate(data_from_julia_code, self.VARIABLE_TYPES)

        return result
