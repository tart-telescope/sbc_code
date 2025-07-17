import hashlib
import logging
import os

import numpy as np
from tart.operation import observation, settings
from tart.util import utc

"""
Helper functions
"""


def get_psd_ext(d, fs, nfft):
    logging.warning("DEPRECATED: Use get_psd_np instead.")
    from matplotlib import mlab

    power, freq = mlab.psd(d, Fs=fs, NFFT=nfft)
    num_bins = 128
    window_width = len(power) // num_bins
    power_ret = []
    freq_ret = []
    for i in range(num_bins):
        start = int(i * window_width)
        stop = start + window_width
        power_ret.append(power[start:stop].max())
        freq_ret.append(freq[start:stop].mean())
    return np.asarray(power_ret), np.asarray(freq_ret)


def get_psd_np(d, fs, nfft):
    """
    Drop-in replacement for matplotlib.mlab.psd() using pure numpy.

    This function provides equivalent functionality to matplotlib.mlab.psd()
    without requiring matplotlib as a dependency. It computes the power
    spectral density using FFT with Hanning windowing and proper scaling
    to match the original behavior exactly.

    Args:
        d: Input signal data
        fs: Sampling frequency
        nfft: FFT size

    Returns:
        tuple: (power, freq) arrays after binning into 128 frequency bins
    """
    # Validate nfft is large enough for 128 frequency bins
    expected_freq_bins = nfft // 2 + 1
    assert expected_freq_bins >= 128, (
        f"nfft={nfft} produces only {expected_freq_bins} frequency bins, need at least 128"
    )
    # Handle different signal lengths like matplotlib.mlab.psd
    if len(d) < nfft:
        # Zero-pad if signal is shorter than nfft
        d = np.concatenate([d, np.zeros(nfft - len(d))])

    # For signals longer than nfft, use Welch's method with non-overlapping segments
    if len(d) > nfft:
        # Calculate number of non-overlapping segments
        num_segments = len(d) // nfft

        # Initialize power accumulator
        power_sum = np.zeros(nfft // 2 + 1)

        # Process each segment
        for i in range(num_segments):
            start = i * nfft
            segment = d[start : start + nfft]

            # Apply window and compute FFT
            window = np.hanning(nfft)
            segment_windowed = segment * window
            X = np.fft.fft(segment_windowed, nfft)
            window_norm = np.sum(window**2)
            segment_power = (X * np.conj(X)).real / (fs * window_norm)
            segment_power = segment_power[: nfft // 2 + 1]

            # Apply scaling for positive frequencies
            if nfft % 2 == 0:  # Even nfft
                segment_power[1:-1] *= 2
            else:  # Odd nfft
                segment_power[1:] *= 2

            power_sum += segment_power

        # Average across segments
        power = power_sum / num_segments
    else:
        # Signal length equals nfft or was zero-padded
        window = np.hanning(nfft)
        d_windowed = d * window
        X = np.fft.fft(d_windowed, nfft)
        window_norm = np.sum(window**2)
        power = (X * np.conj(X)).real / (fs * window_norm)
        power = power[: nfft // 2 + 1]
        if nfft % 2 == 0:  # Even nfft
            power[1:-1] *= 2
        else:  # Odd nfft
            power[1:] *= 2

    # Generate frequency array to match matplotlib.mlab.psd behavior
    freq = np.fft.fftfreq(nfft, 1 / fs)[: nfft // 2 + 1]
    # Fix negative Nyquist frequency for even nfft
    if nfft % 2 == 0:
        freq[-1] = abs(freq[-1])

    num_bins = 128
    window_width = len(power) // num_bins
    power_ret = []
    freq_ret = []

    # Handle case where power array is smaller than num_bins
    if window_width == 0:
        # If power array is too small, pad with zeros and repeat last frequency
        power_ret = power.tolist() + [0.0] * (num_bins - len(power))
        freq_ret = freq.tolist() + [freq[-1]] * (num_bins - len(freq))
    else:
        for i in range(num_bins):
            start = int(i * window_width)
            stop = start + window_width
            if start < len(power):
                power_ret.append(power[start:stop].max())
                freq_ret.append(freq[start:stop].mean())
            else:
                # If we've run out of data, pad with zeros
                power_ret.append(0.0)
                freq_ret.append(freq[-1] if len(freq) > 0 else 0.0)

    return np.asarray(power_ret), np.asarray(freq_ret)


def get_psd(d, fs, nfft):
    # Validate nfft is large enough for 128 frequency bins
    expected_freq_bins = nfft // 2 + 1
    assert expected_freq_bins >= 128, (
        f"nfft={nfft} produces only {expected_freq_bins} frequency bins, need at least 128"
    )
    return get_psd_np(d, fs, nfft)


def sha256_checksum(filename, block_size=65536):
    sha256 = hashlib.sha256()
    with open(filename, "rb") as f:
        for block in iter(lambda: f.read(block_size), b""):
            sha256.update(block)
    return sha256.hexdigest()


def ph_stats(vals, stable_threshold, N_samples):
    expval = np.exp(1j * np.asarray(vals) * np.pi / 6.0)
    m = np.angle(np.mean(expval))
    s = np.abs(expval.sum()) / (1.0 * len(vals))
    if m < 0:
        m += 2 * np.pi
    mean_rounded = int(np.round(m / (2 * np.pi) * 12))
    return [mean_rounded, s, stable_threshold, N_samples, int(s > stable_threshold)]


def mean_stats(vals, mean_threshold):
    m = np.mean(vals)
    return [m, mean_threshold, int(abs(m - 0.5) < mean_threshold)]


def mkdir_p(path):
    os.makedirs(path, exist_ok=True)


def create_timestamp_and_path(base_path):
    ts = utc.now()  # Timestamp information for directory structure
    # Create a meaningful directory structure to organize recorded data
    p = os.path.join(base_path, str(ts.year), str(ts.month), str(ts.day))
    mkdir_p(p)
    # Call timestamp again (the directory name will not have changed, but the timestamp will be more accurate)
    ts = utc.now()
    return ts, p


def get_status(tart_instance):
    vals = tart_instance.read_status(False)
    d = tart_instance.extract(vals)
    d["timestamp"] = utc.now()
    return d


def run_diagnostic(tart, runtime_config):
    # pp = tart.load_permute()
    logging.info("Enabling DEBUG mode")
    tart.debug(
        on=not runtime_config["acquire"],
        shift=runtime_config["shifter"],
        count=runtime_config["counter"],
        noisy=runtime_config["verbose"],
    )
    logging.info("Setting capture registers")

    num_ant = runtime_config["diagnostic"]["num_ant"]
    N_samples = runtime_config["diagnostic"]["N_samples"]  # Number of samples for each antenna
    stable_threshold = runtime_config["diagnostic"]["stable_threshold"]  # 95% in same direction

    phases = []

    for src in range(num_ant):
        tart.reset()
        tart.capture(on=True, source=src, noisy=runtime_config["verbose"])
        tart.centre(runtime_config["centre"], noisy=runtime_config["verbose"])
        tart.start(runtime_config["diagnostic"]["N_samples_exp"], True)
        k = 0
        measured_phases = []
        while k < N_samples:
            k += 1
            d = get_status(tart)
            measured_phases.append(d["TC_STATUS"]["phase"])

        phases.append(
            dict(
                list(
                    zip(
                        ["measured", "stability", "threshold", "N_samples", "ok"],
                        ph_stats(measured_phases, stable_threshold, N_samples),
                    )
                )
            )
        )

    mean_phases = []
    for i in range(num_ant):
        mean_phases.append(phases[i]["measured"])

    logging.info("Median phase: %s", np.median(mean_phases))
    delay_to_be_set = (np.median(mean_phases) + 6) % 12
    logging.info("Set delay to: %s", delay_to_be_set)

    runtime_config["sample_delay"] = delay_to_be_set

    logging.info("Starting small test acquisition")
    tart.reset()
    tart.debug(on=False, noisy=runtime_config["verbose"])
    tart.set_sample_delay(delay_to_be_set)
    tart.capture(on=True, source=0, noisy=runtime_config["verbose"])
    tart.centre(runtime_config["centre"], noisy=runtime_config["verbose"])
    tart.start_acquisition(1.1, True)

    d = get_status(tart)

    while not tart.data_ready():
        tart.pause(duration=0.005, noisy=True)
    logging.info("Acquisition complete, beginning read-back")
    # tart.capture(on=False, noisy=runtime_config['verbose'])
    logging.debug("N_samples_exp: %s", runtime_config["diagnostic"]["spectre"]["N_samples_exp"])
    data = tart.read_data(num_words=2 ** runtime_config["diagnostic"]["spectre"]["N_samples_exp"])
    data = np.asarray(data, dtype=np.uint8)
    ant_data = np.flipud(np.unpackbits(data).reshape(-1, 24).T)
    logging.debug("Antenna data shape: %s, first 10 samples: %s", ant_data.shape, ant_data[:, :10])
    radio_means = []
    mean_threshold = 0.2
    for i in range(num_ant):
        radio_means.append(
            dict(
                list(
                    zip(
                        ["mean", "threshold", "ok"],
                        mean_stats(ant_data[i], mean_threshold),
                    )
                )
            )
        )

    ant_data = np.asarray(ant_data, dtype=np.float16) * 2 - 1.0

    channels = []

    for i in range(num_ant):
        channel = {}
        channel["id"] = i
        channel["phase"] = phases[i]
        channel["radio_mean"] = radio_means[i]
        power, freq = get_psd(
            ant_data[i] - ant_data[i].mean(),
            16e6,
            runtime_config["diagnostic"]["spectre"]["NFFT"],
        )
        power_db = 10.0 * np.log10(power + 1e-32)  # Avoid divide by zero
        power_db = np.nan_to_num(power_db)
        channel["power"] = (np.asarray(power_db * 1000, dtype=int) / 1000.0).tolist()
        channel["freq"] = (freq / 1e6).tolist()
        channels.append(channel)

    runtime_config["channels"] = channels
    runtime_config["channels_timestamp"] = utc.now()
    runtime_config["status"] = d
    logging.info("Diagnostic complete")


"""
RUN TART in raw data acquisition mode
"""


def run_acquire_raw(tart, runtime_config):
    runtime_config["acquire"] = 1
    tart.reset()
    tart.debug(
        on=not runtime_config["acquire"],
        shift=runtime_config["shifter"],
        count=runtime_config["counter"],
        noisy=runtime_config["verbose"],
    )
    tart.capture(on=True, source=0, noisy=runtime_config["verbose"])
    tart.set_sample_delay(runtime_config["sample_delay"])
    tart.centre(runtime_config["centre"], noisy=runtime_config["verbose"])
    t_stmp, path = create_timestamp_and_path(runtime_config["raw"]["base_path"])
    tart.start_acquisition(1.1, True)

    while not tart.data_ready():
        tart.pause(duration=0.005, noisy=True)
    logging.info("Acquisition complete, beginning read-back")
    # tart.capture(on=False, noisy=runtime_config['verbose'])

    data = tart.read_data(num_words=np.power(2, runtime_config["raw"]["N_samples_exp"]))

    d = get_status(tart)
    runtime_config["status"] = d
    tart.reset()

    logging.info("Reshaping antenna data")
    data = np.asarray(data, dtype=np.uint8)
    ant_data = np.flipud(np.unpackbits(data).reshape(-1, 24).T)
    if runtime_config["raw"]["save"]:
        config = settings.from_file(runtime_config["telescope_config_path"])

        fname = "data_{}.hdf".format(t_stmp.strftime("%Y-%m-%d_%H_%M_%S.%f"))

        filename = os.path.join(path, fname)

        obs = observation.Observation(t_stmp, config, savedata=ant_data)
        obs.to_hdf5(filename)
        logging.info("Saved raw data to: %s", filename)
        return {"filename": filename, "sha256": sha256_checksum(filename)}
    return {}
