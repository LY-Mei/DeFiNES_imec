from plot_helper_funcs import *


def simple_data_collect(result_saving_path):
    import glob
    import re
    import pickle

    class DataToPlot:
        def __init__(self):
            self.en_collect = {}
            self.la_collect = {}

            self.en_per_layer_collect = {}
            self.la_per_layer_collect = {}

    data_to_plot = DataToPlot()
    paths = glob.glob(f'{result_saving_path}/*.pkl')
    for idx, path in enumerate(paths):
        print(f'Reading in result -- {path}')
        ky = re.split('[/ .]', path)[-2]
        with open(path, 'rb') as f:
            data = pickle.load(f)
        f.close()

        data_to_plot.en_collect[ky], data_to_plot.la_collect[ky] = get_total_en_la(data)
        data_to_plot.en_per_layer_collect[ky], data_to_plot.la_per_layer_collect[ky] = get_per_layer_en_la(data)

    return data_to_plot


if __name__ == '__main__':
    from main_lbl import result_saving_path
    import pickle
    data_collect = simple_data_collect(result_saving_path)
    a=1