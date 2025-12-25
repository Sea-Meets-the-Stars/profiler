# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Profiler is a Python package for loading, processing, and analyzing oceanographic profiler data from various instruments including Spray gliders, Solo/Flip floats, EM-APEX floats, VMPs (Vertical Microstructure Profilers), and Triaxus towed vehicles.

## Environment Setup

**Environment variables (optional, for test data):**
- `ARCTERX`: Path to ARCTERX campaign data

**Installation:**
```bash
pip install -e .
```

## Running Tests

```bash
pytest profiler/tests/
pytest profiler/tests/test_spray.py  # single test file
pytest profiler/tests/test_spray.py::test_binned_spray  # single test
```

Note: Tests require actual instrument data files and appropriate environment variables.

## Key Architecture

### Class Hierarchy

The package uses an inheritance hierarchy for profiler data:

```
ProfilerData (ABC)          # Base class in profilerdata.py
├── ADCPData                 # Adds ADCP velocity fields (udop, vdop)
│   └── SprayData           # Spray gliders (gliderdata.py)
├── SoloData                # Solo floats (floatdata.py)
├── FlipData                # Flip floats (floatdata.py)
├── SlocumData              # Slocum gliders (gliderdata.py)
├── VMPData                 # Vertical Microstructure Profilers (vmpdata.py)
└── TriaxusData             # Triaxus towed vehicles (triaxusdata.py)
```

### Core Modules

- **profilerdata.py**: Abstract base class `ProfilerData` defining the interface for all profilers. Key attributes: `time`, `lat`, `lon`, `depth`, `s` (salinity), `t` (temperature), `theta` (potential temp), `sigma` (density)
- **gliderdata.py**: `SprayData` and `SlocumData` classes for underwater gliders
- **floatdata.py**: `SoloData`, `FlipData` for profiling floats
- **profilerpairs.py**: `ProfilerPairs` class for structure function analysis - pairs profiles by time/distance constraints and computes velocity/tracer differences
- **binning.py**: `bin_profilerdata()` for depth-binning raw profiles
- **io.py**: JSON serialization utilities (`jsonify`, `loadjson`, `savejson`)

### Data Loading Patterns

Three main loading patterns:
1. **from_binned_file()**: Load pre-binned .mat files (IDG format)
2. **from_rawfile()**: Load raw instrument files using instrument-specific loaders
3. **from_dict()**: Create from dictionary of arrays

### Array Conventions

ProfilerData objects track arrays in categories:
- `profile_arrays`: 1D arrays indexed by profile (time, lat, lon)
- `depth_arrays`: 1D arrays indexed by depth level
- `profile_depth_arrays`: 2D arrays [profile, depth] (t, s, theta, sigma)
- `scalar_keys`: Single values (missid, platform)

### ProfilerPairs for Structure Functions

`ProfilerPairs` enables turbulence analysis by:
1. Finding profile pairs within time/distance constraints
2. Computing separations in E-N coordinates relative to survey center
3. Calculating velocity differences (duL=longitudinal, duT=transverse)
4. Computing structure functions S1, S2, S3 vs separation distance

Key methods:
- `calc_delta(iz, variables)`: Compute differences at depth index `iz`
- `calc_Sn(variables)`: Compute structure functions for variable combination
- `calc_Sn_vs_r(rbins)`: Bin structure functions by separation distance

### Subpackages

- **loading/**: Data loaders (`binned.py` for IDG format, `pymatreader/` for .mat files)
- **processing/**: GSW seawater calculations
- **specific/**: Instrument-specific code (altos, em_apex, idg formats)
- **utils/**: Geographic utilities (`offsets.py` for distance calculations)

## Downstream Dependencies

This package is used by the `cugn` repository for California Underwater Glider Network analysis.
