# TART: Radio-telescope low-level interface

This module is used for low-level interfacing to the open-source Transient Array Radio Telescope (TART).

For more information see the [TART github repository](https://github.com/tart-telescope/sbc_code)

## Authors

* Tim Molteno (tim@elec.ac.nz)
* Max Scheel (max@max.ac.nz)
* Pat Suggate (ihavenolimbs@gmail.com)

## Development work

If you are developing this package, this should be installed using

    python setyp.py develop

in which case changes to the source-code will be immediately available to projects using it.

## Testing

To run tests, install with test dependencies and run:
```bash
    sudo apt update && sudo apt install -y build-essential clang
```

```bash
    uv venv
    source .venv/bin/activate
    uv pip install -e ".[test]"
    python -m unittest discover unittests/
```

## NEWS

* Version 0.1.6. Python3 support
* Version 0.1.7. Further python3 support
* Version 0.1.8. Remove unused routines, no implicit import paths
* Version 0.2.0. Save RAW data as .hdf5 files
* Version 0.2.0b3. Add dummy and fake SPI modules when SPI isn't readable. This displays a clock :)
* Version 0.2.0b7. Remove general matplotlib dependency. Only required/imported for validation tests.
