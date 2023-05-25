import typing
import os
from warnings import warn
import math

import numpy as np
from librosa import load as librosa_load
from scipy import signal as scipy_signal

EPS = np.finfo(float).eps


class AudioSignal:
    def __init__(
        self,
        samples: np.ndarray,
        fs: int,
        file_path: typing.Union[str, os.PathLike] = None,
        verbose: bool = True,
    ):
        """Create an audiosignal instance.

        Args:
            samples: Takes in a numpy array and, if necessary,
                converts it to a float with range -1 to 1. Samples has
                n_channels*n_samples dimensions. If value provided is a one
                dimensional array, it is converted to a single row 2
                dimensional array.
            fs: Sampling frequency
            file_path: Defaults to None. Path to original
                audio file in case init is called from a classmethod that
                reads a file.

        """
        self.fs = fs
        """Sampling frequency in Hz."""

        self.samples = samples
        if verbose:
            # Warn when clipping is detected
            if np.amax(np.abs(samples)) > 1.0:
                warn(
                    "Clipping detected in input. You may want to rescale.",
                    RuntimeWarning,
                )

        self.file_path = file_path
        """File path to audio signal's original location (optional)."""

    @property
    def samples(self) -> np.ndarray:
        """The n_channels*n_samples numpy array containing all audio samples."""
        return self._samples

    @samples.setter
    def samples(self, value: np.ndarray):
        """Set samples.

        Takes in a numpy array and, if necessary, converts it to a float
        with range -1 to 1. Samples has n_channels*n_samples dimensions. If
        value provided is a one dimensional array, it is converted to a single
        row 2 dimensional array.

        Args:
            value: a numpy array of integer or float type. For 1
                channel audio, it accepts an array with shape n_samples*1,
                1*n_samples, and n_samples. For all other audio, array needs
                to be of shape n_channels*n_samples.

        """
        # check if provided samples is not empty
        if value.size == 0:
            raise ValueError("It is not possible for an AudioSignal to have no samples")

        # if only 1 dimensional vector of samples for one channel is provided,
        # convert to 1*n_samples array
        if value.ndim == 1:
            value = np.expand_dims(value, axis=0)

        # if 2 dimensional vector has shape n_samples*1, transform
        if value.ndim == 2 and value.shape[1] == 1:
            value = value.T

        # if int type audio, convert to float with -1 to 1 range, leave float
        # untouched, reject other input
        if np.issubdtype(value[0, 0], np.signedinteger):
            int_min = np.abs(np.iinfo(value.dtype).min)
            value = value.astype(dtype=np.float32)
            value = np.divide(value, int_min)
        elif np.issubdtype(value[0, 0], np.floating):  # if float type audio
            pass
        else:
            raise ValueError(
                "Input type not recognized."
                + "Samples has to be a numpy array of integer or float type."
            )

        # Return an array (ndim >= 1) laid out in Fortran order in memory, for librosa
        value = np.asfortranarray(value)

        self._samples = value

    @property
    def n_samples(self) -> int:
        """Number of samples per channel."""
        return self.samples.shape[1]

    @property
    def n_channels(self) -> int:
        """Number of samples per channel."""
        return self.samples.shape[0]

    @property
    def is_mono(self) -> bool:
        """True if the signal has one channel."""
        return self.n_channels == 1

    @property
    def file_name(self) -> typing.Union[str, os.PathLike]:
        """File name of audio signal (optional)."""
        return self.get_file_name_from_path(self.file_path)

    @property
    def file_name_without_extension(self) -> str:
        """File name of audio signal without extension (optional)."""
        return self.get_file_name_from_path(self.file_path, remove_ext=True)

    @classmethod
    def load_from_audiofile(
        cls,
        file_path_in: typing.Union[str, bytes, os.PathLike],
        offset=0.0,
        duration=None,
        mono=False,
        verbose=True,
    ) -> "AudioSignal":
        r"""Turn an audiofile (.wav etc.) into AudioSignal.

        Loads an audiofile (like .wav files) and turns it into an AudioSignal
        instance. All audiofiles supported by the package audioread should work.

        Args:
            file_path_in: relative or absolute path to the file
            NB! In Windowns, if you want to use backslash in the file path name, use two backslashes
                to prevent a unicode error. I.e. 'C:\\Users\\blabla\\etc.wav'
            offset: Defaults to 0.0. Start reading after this time (in seconds)
            duration: Defaults to None for complete clip. Only load up to this much audio (in seconds)

        Returns:
            instance of audiosigal or one of its children

        """
        # pylint: disable=not-callable
        samples, fs = librosa_load(
            file_path_in, sr=None, mono=mono, offset=offset, duration=duration
        )
        return cls(samples, fs, file_path=file_path_in)

    @staticmethod
    def get_file_name_from_path(
        file_path_in: typing.Union[str, os.PathLike, None], remove_ext=False
    ):
        """Obtain file name from full path to file."""
        try:
            file_name = os.path.basename(file_path_in)
        except Exception:
            return None

        if remove_ext:
            assert len(file_name.split(".")) == 2
            return file_name.split(".")[0]

        return file_name

    def apply_butterworth_filter(
        self,
        order: int,
        Wn: typing.Union[list, np.ndarray],
        filter_type: str = None,
        analog: bool = False,
    ):
        """Apply a Butterworth filter"""
        Wn = np.asarray(Wn)
        if filter_type is None:
            if np.isscalar(Wn):
                filter_type = "low"
            else:
                filter_type = "bandpass"
        sos = scipy_signal.butter(
            order,
            Wn,
            btype=filter_type,
            analog=analog,
            output="sos",
        )
        samples_copy = self.samples.copy()
        self.samples = np.squeeze(
            scipy_signal.sosfilt(sos, samples_copy, axis=1, zi=None)
        )

    def harmonic_ratio(
        self,
        win_length,
        hop_length,
        window="hamming",
    ):
        """Estimate the harmonic ratio as standardized in MPEG-7"""
        assert self.is_mono  # TODO implement for multichannel signals?

        # Get a windowed signal
        window_coef = scipy_signal.get_window(window, win_length, fftbins=False)
        n_windows = int((self.n_samples - win_length) / hop_length)
        windowed_signal = np.zeros(shape=(n_windows, win_length))
        samples_copy = self.samples.copy()
        for i in range(n_windows):
            windowed_signal[i] = (
                samples_copy[0, i * hop_length : i * hop_length + win_length]
                * window_coef
            )

        # Determine high edge of the lag domain. 40 ms is recommended by MPEG-7.
        high_edge = int(np.min(np.asarray([np.floor(self.fs * 0.04), win_length - 1])))

        # Autocorrelation (Convert to the lag domain)
        m2 = 2 ** (math.ceil(math.log2(2 * win_length - 1)))
        c1 = np.real(np.fft.ifft(np.power(np.abs(np.fft.fft(windowed_signal, m2)), 2)))
        R = c1[:, 1:high_edge]

        # Isolate the total power calculated during autocorrelation.
        total_power = c1[:, 0]

        # Expand the summation of the partial power calculation.
        partial_power = np.flip(np.cumsum(np.power(windowed_signal, 2), axis=1), axis=1)
        partial_power = partial_power[:, 1:high_edge]

        # Determine the lower edge of the range.
        low_edge = np.zeros((n_windows), dtype=int)
        for i in range(n_windows):
            nonzero_differences = np.argwhere(np.diff(np.sign(R[i, :]), axis=0))
            if nonzero_differences.size == 0:
                low_edge[i] = high_edge
            else:
                low_edge[i] = nonzero_differences[0]

        # Normalize the autocorrelation.
        gamma = np.divide(
            np.transpose(R),
            np.sqrt(np.transpose(total_power) * np.transpose(partial_power)) + EPS,
        )
        # Set gamma outside the range to 0.
        for i in range(n_windows):
            gamma[0 : low_edge[i], i] = 0

        # Estimate first guess of HR as the max of Gamma.
        hr_estimate = np.max(gamma, axis=0)

        # TODO improve with interpolation for higher accuracy?

        return hr_estimate
