"""DrifterData — adapts Lagrangian drifter trajectory data to the ProfilerData interface.

Each drifter becomes a separate DrifterData instance.  Time steps map to
"profiles", and the single surface layer provides udop/vdop velocity arrays
compatible with ProfilerPairs.calc_delta().
"""

import numpy as np

from profiler import profilerdata


# Meter-to-degree conversion (equatorial approximation, cos(0)=1)
_M_PER_DEG = 111_000.0


class DrifterData(profilerdata.ProfilerData):
    """ProfilerData subclass for a single Lagrangian drifter trajectory."""

    platform = 'Drifter'
    has_adcp = True  # We supply udop/vdop
    scalar_keys: list = []

    # ------------------------------------------------------------------ #
    #  Constructors
    # ------------------------------------------------------------------ #

    def __init__(self, datafile: str, dataset: str):
        super().__init__(datafile, dataset)

    @classmethod
    def from_QG_trajectory(cls, traj_df, meta, drifter_id):
        """Build a DrifterData instance for one drifter.
        This is from the QG model output.

        Parameters
        ----------
        traj_df : pd.DataFrame
            Full trajectory table (all drifters).  Must contain columns
            ID, x_m, y_m, t.
        meta : dict
            Metadata dict (must contain 'dx', 'nx').
        drifter_id : float
            The drifter ID to extract.

        Returns
        -------
        DrifterData
        """
        # Extract this drifter's rows, sorted by time
        sub = traj_df[traj_df.ID == drifter_id].sort_values('t')
        x_m = sub.x_m.values
        y_m = sub.y_m.values
        times = sub.t.values.astype(float)
        nt = len(times)

        # --- Velocities via centered finite differences (no periodic wrap) ---
        u = np.empty(nt)
        v = np.empty(nt)
        for k in range(nt):
            if k == 0:
                # Forward difference
                dt = times[1] - times[0]
                dx = x_m[1] - x_m[0]
                dy = y_m[1] - y_m[0]
            elif k == nt - 1:
                # Backward difference
                dt = times[-1] - times[-2]
                dx = x_m[-1] - x_m[-2]
                dy = y_m[-1] - y_m[-2]
            else:
                # Centered difference
                dt = times[k + 1] - times[k - 1]
                dx = x_m[k + 1] - x_m[k - 1]
                dy = y_m[k + 1] - y_m[k - 1]
            u[k] = dx / dt
            v[k] = dy / dt

        # --- Build the DrifterData object ---
        obj = cls.__new__(cls)
        obj.datafile = None
        obj.dataset = f'QG_drifter_{int(drifter_id)}'
        obj.in_field = False

        # Array layout declarations (used by ProfilerData helpers)
        obj.profile_arrays = ['lat', 'lon', 'time']
        obj.depth_arrays = ['depth']
        obj.profile_depth_arrays = ['udop', 'vdop']
        obj.scalar_keys = []
        obj.meta_keys = ['missid', 'platform', 'dataset']

        # Profile arrays — one element per time step
        # Add a tiny per-drifter offset so ProfilerPairs dt>0 filter works
        obj.time = times + drifter_id * 1e-3
        obj.lat = y_m / _M_PER_DEG
        obj.lon = x_m / _M_PER_DEG

        # Depth array — single surface level
        obj.depth = np.array([0.0])

        # Velocity arrays — shape (Ntime, 1) for the single depth level
        obj.udop = u[:, np.newaxis]
        obj.vdop = v[:, np.newaxis]

        # Mission ID — integer drifter ID (used for avoid_same_glider)
        obj.missid = int(drifter_id)

        return obj

    @classmethod
    def all_from_QG_trajectory(cls, traj_df, meta):
        """Build a list of DrifterData objects, one per drifter ID.
        This is from QG model output.

        Parameters
        ----------
        traj_df : pd.DataFrame
            Full trajectory table.
        meta : dict
            Metadata dict.

        Returns
        -------
        list of DrifterData
        """
        ids = sorted(traj_df.ID.unique())
        return [cls.from_trajectory(traj_df, meta, did) for did in ids]
