"""
Unit test to verify get_psd_ext and get_psd_np produce identical outputs
"""

import unittest

import numpy as np

from tart_hardware_interface.highlevel_modes_api import get_psd_ext, get_psd_np


class TestPSDFunctionsEquivalence(unittest.TestCase):
    """Test that get_psd_ext and get_psd_np produce identical results"""

    def setUp(self):
        """Set up test parameters"""
        self.fs = 16000000  # 16 MHz
        self.nfft_values = [256, 512, 1024]

    def test_psd_functions_equivalence(self):
        """Test that both functions produce identical results for different nfft values"""

        for nfft in self.nfft_values:
            with self.subTest(nfft=nfft):
                # Test signals
                test_signals = [
                    # Sine wave
                    np.sin(2 * np.pi * 50000 * np.linspace(0, 1, nfft, endpoint=False)),
                    # Random noise
                    np.random.RandomState(42).randn(nfft),
                    # Multi-frequency
                    (
                        np.sin(2 * np.pi * 100000 * np.linspace(0, 1, nfft, endpoint=False))
                        + 0.5 * np.sin(2 * np.pi * 200000 * np.linspace(0, 1, nfft, endpoint=False))
                    ),
                ]

                for i, signal in enumerate(test_signals):
                    with self.subTest(nfft=nfft, signal=i + 1):
                        # Get results from both functions
                        power_np, freq_np = get_psd_np(signal, self.fs, nfft)
                        power_ext, freq_ext = get_psd_ext(signal, self.fs, nfft)

                        # Compare results
                        np.testing.assert_allclose(
                            power_np,
                            power_ext,
                            rtol=1e-10,
                            err_msg=f"Power arrays differ for nfft={nfft}, signal={i + 1}",
                        )
                        np.testing.assert_allclose(
                            freq_np,
                            freq_ext,
                            rtol=1e-10,
                            err_msg=f"Frequency arrays differ for nfft={nfft}, signal={i + 1}",
                        )

    def test_output_properties(self):
        """Test basic output properties"""
        fs = 1000
        nfft = 256
        signal = np.random.randn(nfft)

        power, freq = get_psd_np(signal, fs, nfft)

        self.assertEqual(len(power), 128, "Expected 128 power bins")
        self.assertEqual(len(freq), 128, "Expected 128 frequency bins")
        self.assertTrue(np.all(power >= 0), "Power should be non-negative")
        self.assertTrue(np.all(freq >= 0), "Frequency should be non-negative")
        self.assertEqual(freq[0], 0, "First frequency should be 0")
        self.assertTrue(np.all(np.diff(freq) > 0), "Frequency should be monotonic")
        self.assertIsInstance(power, np.ndarray, "Power should be numpy array")
        self.assertIsInstance(freq, np.ndarray, "Frequency should be numpy array")

    def test_different_signal_lengths(self):
        """Test with signals of different lengths"""
        fs = 8000
        nfft = 256

        # Signal shorter than nfft (should be zero-padded)
        short_signal = np.random.RandomState(123).randn(128)

        # Signal longer than nfft (should be truncated)
        long_signal = np.random.RandomState(456).randn(512)

        for signal, name in [(short_signal, "short"), (long_signal, "long")]:
            with self.subTest(signal_type=name):
                power_np, freq_np = get_psd_np(signal, fs, nfft)
                power_ext, freq_ext = get_psd_ext(signal, fs, nfft)

                np.testing.assert_allclose(
                    power_np,
                    power_ext,
                    rtol=1e-10,
                    err_msg=f"Power arrays differ for {name} signal",
                )
                np.testing.assert_allclose(
                    freq_np,
                    freq_ext,
                    rtol=1e-10,
                    err_msg=f"Frequency arrays differ for {name} signal",
                )

    def test_edge_cases(self):
        """Test edge cases with special signal types"""
        fs = 8000
        nfft = 256  # Use larger nfft to ensure at least 128 frequency bins

        edge_cases = [
            ("DC signal", np.ones(nfft)),
            ("Zero signal", np.zeros(nfft)),
            ("Impulse", np.concatenate([np.array([1.0]), np.zeros(nfft - 1)])),
            ("Step function", np.concatenate([np.zeros(nfft // 2), np.ones(nfft // 2)])),
            ("Ramp", np.linspace(0, 1, nfft)),
            ("Alternating", np.array([1, -1] * (nfft // 2))),
        ]

        for name, signal in edge_cases:
            with self.subTest(signal_type=name):
                power_np, freq_np = get_psd_np(signal, fs, nfft)
                power_ext, freq_ext = get_psd_ext(signal, fs, nfft)

                np.testing.assert_allclose(
                    power_np, power_ext, rtol=1e-10, err_msg=f"Power arrays differ for {name}"
                )
                np.testing.assert_allclose(
                    freq_np, freq_ext, rtol=1e-10, err_msg=f"Frequency arrays differ for {name}"
                )

    def test_different_sampling_rates(self):
        """Test with different sampling rates"""
        nfft = 256
        sampling_rates = [1000, 8000, 16000, 44100, 48000]

        for fs in sampling_rates:
            with self.subTest(fs=fs):
                # Create test signal with known frequency content
                t = np.linspace(0, 1, nfft, endpoint=False)
                signal = np.sin(2 * np.pi * fs / 8 * t)  # 1/8 of sampling rate

                power_np, freq_np = get_psd_np(signal, fs, nfft)
                power_ext, freq_ext = get_psd_ext(signal, fs, nfft)

                np.testing.assert_allclose(
                    power_np, power_ext, rtol=1e-10, err_msg=f"Power arrays differ for fs={fs}"
                )
                np.testing.assert_allclose(
                    freq_np, freq_ext, rtol=1e-10, err_msg=f"Frequency arrays differ for fs={fs}"
                )

    def test_multiple_random_seeds(self):
        """Test with multiple random seeds to ensure robustness"""
        fs = 16000
        nfft = 512
        seeds = [1, 42, 123, 456, 789]

        for seed in seeds:
            with self.subTest(seed=seed):
                np.random.seed(seed)
                signal = np.random.randn(nfft)

                power_np, freq_np = get_psd_np(signal, fs, nfft)
                power_ext, freq_ext = get_psd_ext(signal, fs, nfft)

                np.testing.assert_allclose(
                    power_np, power_ext, rtol=1e-10, err_msg=f"Power arrays differ for seed={seed}"
                )
                np.testing.assert_allclose(
                    freq_np,
                    freq_ext,
                    rtol=1e-10,
                    err_msg=f"Frequency arrays differ for seed={seed}",
                )

    def test_boundary_signal_lengths(self):
        """Test signals with lengths that are exact multiples of nfft"""
        fs = 8000
        nfft = 256  # Use larger nfft to ensure at least 128 frequency bins

        # Test exact multiples
        for multiplier in [1, 2, 3, 4, 5]:
            signal_length = nfft * multiplier
            with self.subTest(length=signal_length):
                signal = np.random.RandomState(42).randn(signal_length)

                power_np, freq_np = get_psd_np(signal, fs, nfft)
                power_ext, freq_ext = get_psd_ext(signal, fs, nfft)

                np.testing.assert_allclose(
                    power_np,
                    power_ext,
                    rtol=1e-10,
                    err_msg=f"Power arrays differ for length={signal_length}",
                )
                np.testing.assert_allclose(
                    freq_np,
                    freq_ext,
                    rtol=1e-10,
                    err_msg=f"Frequency arrays differ for length={signal_length}",
                )

    def test_very_short_signals(self):
        """Test very short signals"""
        fs = 1000
        nfft = 256  # Use larger nfft to ensure at least 128 frequency bins

        short_lengths = [1, 2, 3, 5, 10, 16, 32, 64, 128]

        for length in short_lengths:
            with self.subTest(length=length):
                signal = np.random.RandomState(length).randn(length)

                power_np, freq_np = get_psd_np(signal, fs, nfft)
                power_ext, freq_ext = get_psd_ext(signal, fs, nfft)

                np.testing.assert_allclose(
                    power_np,
                    power_ext,
                    rtol=1e-10,
                    err_msg=f"Power arrays differ for length={length}",
                )
                np.testing.assert_allclose(
                    freq_np,
                    freq_ext,
                    rtol=1e-10,
                    err_msg=f"Frequency arrays differ for length={length}",
                )

    def test_known_frequency_content(self):
        """Test signals with known frequency content"""
        fs = 8000
        nfft = 256

        # Test pure tones at different frequencies
        frequencies = [100, 500, 1000, 2000, 3000]

        for freq in frequencies:
            with self.subTest(freq=freq):
                t = np.linspace(0, 1, nfft, endpoint=False)
                signal = np.sin(2 * np.pi * freq * t)

                power_np, freq_np = get_psd_np(signal, fs, nfft)
                power_ext, freq_ext = get_psd_ext(signal, fs, nfft)

                np.testing.assert_allclose(
                    power_np,
                    power_ext,
                    rtol=1e-10,
                    err_msg=f"Power arrays differ for freq={freq}Hz",
                )
                np.testing.assert_allclose(
                    freq_np,
                    freq_ext,
                    rtol=1e-10,
                    err_msg=f"Frequency arrays differ for freq={freq}Hz",
                )

    def test_additional_nfft_values(self):
        """Test with additional nfft values"""
        fs = 16000
        nfft_values = [256, 512, 1024, 2048]  # Only use nfft values that produce at least 128 bins

        for nfft in nfft_values:
            with self.subTest(nfft=nfft):
                # Create signal with length equal to nfft
                signal = np.random.RandomState(nfft).randn(nfft)

                power_np, freq_np = get_psd_np(signal, fs, nfft)
                power_ext, freq_ext = get_psd_ext(signal, fs, nfft)

                np.testing.assert_allclose(
                    power_np, power_ext, rtol=1e-10, err_msg=f"Power arrays differ for nfft={nfft}"
                )
                np.testing.assert_allclose(
                    freq_np,
                    freq_ext,
                    rtol=1e-10,
                    err_msg=f"Frequency arrays differ for nfft={nfft}",
                )

    def test_signals_with_different_variances(self):
        """Test signals with different statistical properties"""
        fs = 8000
        nfft = 256
        variances = [0.1, 0.5, 1.0, 2.0, 10.0]

        for var in variances:
            with self.subTest(variance=var):
                signal = np.random.RandomState(42).randn(nfft) * np.sqrt(var)

                power_np, freq_np = get_psd_np(signal, fs, nfft)
                power_ext, freq_ext = get_psd_ext(signal, fs, nfft)

                np.testing.assert_allclose(
                    power_np,
                    power_ext,
                    rtol=1e-10,
                    err_msg=f"Power arrays differ for variance={var}",
                )
                np.testing.assert_allclose(
                    freq_np,
                    freq_ext,
                    rtol=1e-10,
                    err_msg=f"Frequency arrays differ for variance={var}",
                )

    def test_combined_signals(self):
        """Test complex combined signals"""
        fs = 16000
        nfft = 512

        # Create combined signal: multiple tones + noise
        t = np.linspace(0, 1, nfft, endpoint=False)
        signal = (
            np.sin(2 * np.pi * 440 * t)  # A4 note
            + 0.5 * np.sin(2 * np.pi * 880 * t)  # A5 note
            + 0.3 * np.sin(2 * np.pi * 1760 * t)  # A6 note
            + 0.1 * np.random.RandomState(42).randn(nfft)  # noise
        )

        power_np, freq_np = get_psd_np(signal, fs, nfft)
        power_ext, freq_ext = get_psd_ext(signal, fs, nfft)

        np.testing.assert_allclose(
            power_np, power_ext, rtol=1e-10, err_msg="Power arrays differ for combined signal"
        )
        np.testing.assert_allclose(
            freq_np, freq_ext, rtol=1e-10, err_msg="Frequency arrays differ for combined signal"
        )


if __name__ == "__main__":
    unittest.main()
