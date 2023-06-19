from plotly.graph_objects import Figure, Scatter
from mne.io import read_raw_edf
from numpy import mean
from easygui import fileopenbox
from yaml import safe_load
from os.path import join
from philistine.mne import savgol_iaf


def load_config():
    try:
        with open(join("config.yaml")) as yaml_file:
            doc = safe_load(yaml_file)
        return doc
    except:
        raise Exception("Can't load config file")


def browse_file(config):
    file_name = fileopenbox(msg="wybierz plik do weryfikacji",
                            title="IAF checker",
                            default=config["browse_directory"])
    if file_name is None:
        exit(0)
    return file_name


def calculate_iaf(file_name, config):
    data = read_raw_edf(file_name, verbose=False)
    freq = data.info["sfreq"]
    data = data.crop(30, len(data) / freq - 30)
    iaf = savgol_iaf(data, picks=None, fmin=config["iaf_range"][0], fmax=config["iaf_range"][1])
    spectrum = data.compute_psd(method="welch", fmin=1, fmax=48)
    data, _ = spectrum.get_data(return_freqs=True)
    psds = mean(data, axis=0)
    return iaf[0], psds, spectrum.freqs


def draw_plot(iaf, psds, freqs, participant_data):
    fig = Figure()
    fig.add_trace(Scatter(x=list(freqs), y=list(psds)))
    fig.update_layout(title_text=f"Analizowany plik:   {participant_data}                       IAF proponowany przez algorytm: {iaf}")
    # Add range slider
    fig.update_layout(xaxis=dict(rangeslider=dict(visible=True)))
    fig.show()


def main():
    config = load_config()
    file_name = browse_file(config=config)
    participant_data = file_name.split('\\')[-1]
    iaf, psds, freqs = calculate_iaf(file_name, config)
    draw_plot(iaf, psds, freqs, participant_data)


if __name__ == "__main__":
    main()
