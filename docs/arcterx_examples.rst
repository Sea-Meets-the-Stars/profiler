ARCTERX Analysis Examples
======================

This guide provides examples of analyzing oceanographic data from the ARCTERX dataset using the Profiler package.

Loading Different Asset Types
---------------------------

The ARCTERX dataset includes multiple types of oceanographic instruments. Here's how to load each type:

Loading Spray Gliders
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    def load_sprays():
        datafiles = glob.glob(os.path.join(apath, 'gliders/spray/*.mat'))
        sprays = []
        for datafile in datafiles:
            s = gliderdata.SprayData.from_binned_file(
                datafile, 
                'ARCTERX-Leg2', 
                in_field=True,
                extra_dict={'adcp_on': False}
            )
            sprays.append(s)
        return sprays

Loading EM-APEX Floats
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    def load_apexes():
        emapexs = []
        dfiles = glob.glob('EMApex_data_*.mat')
        for dfile in dfiles:
            pData = em_apex.load_emapex_infield(
                dfile, 
                'ARCTERX-Leg2', 
                binme=True, 
                add_vel=False
            )
            emapexs += pData
        return emapexs

Loading VMP Data
~~~~~~~~~~~~~~

.. code-block:: python

    def load_vmp():
        vmp = vmpdata.VMPData.from_binned_file(
            'combo.nc',
            'cusack', 
            'ARCTERX-Leg2',
            in_field=True,
            missid=20000
        )
        return [vmp]

Analyzing Profile Separations
---------------------------

Creating Profile Pairs
~~~~~~~~~~~~~~~~~~~~

Example of creating and analyzing profile pairs:

.. code-block:: python

    def analyze_separations(dataset='ARCTERX-Leg2', max_time=10.):
        # Load different types of profilers
        profilers = load_by_asset(['Spray', 'EMApex', 'VMP'])
        
        # Generate pairs
        mixPairs = profilepairs.ProfilerPairs(
            profilers, 
            max_time=max_time,
            debug=False,
            randomize=False
        )
        
        return mixPairs

Calculating Structure Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Example of calculating and analyzing structure functions:

.. code-block:: python

    def analyze_structure(dataset='ARCTERX-Leg2', 
                         variables='dTdTdT',
                         iz=5):
        # Load profilers
        profilers = load_by_asset(['Spray', 'Solo', 'EMApex'])
        
        # Setup binning
        nbins = 20
        rbins = 10**np.linspace(0., np.log10(400), nbins)  # km
        
        # Create pairs
        gPairs = profilepairs.ProfilerPairs(
            profilers, 
            max_time=10., 
            avoid_same_glider=True
        )
        
        # Calculate structure functions
        gPairs.calc_delta(iz, variables)
        gPairs.calc_Sn(variables)
        
        # Calculate statistics
        Sn_dict = gPairs.calc_Sn_vs_r(rbins, nboot=100)
        gPairs.calc_corr_Sn(Sn_dict)
        
        return Sn_dict

Visualization Examples
-------------------

Plotting Separations
~~~~~~~~~~~~~~~~~~

Example of visualizing profile separations:

.. code-block:: python

    def plot_separations(mixPairs):
        # Create figure
        fig = plt.figure(figsize=(12,6))
        
        # Plot lat/lon positions
        ax_ll = plt.subplot(121)
        for mid in np.unique(mixPairs.data('missida',2).astype(int)):
            idx = mixPairs.data('missida',2) == mid
            ax_ll.scatter(
                mixPairs.data('lon', 2)[idx],
                mixPairs.data('lat', 2)[idx],
                s=2, 
                label=f'MID={mid}'
            )
            
        # Plot separation histogram
        ax_r = plt.subplot(122)
        sns.histplot(mixPairs.r, bins=50, log_scale=True, ax=ax_r)
        
        return fig

Plotting Structure Functions
~~~~~~~~~~~~~~~~~~~~~~~~~

Example of visualizing structure functions:

.. code-block:: python

    def plot_structure(Sn_dict, variables='dTdTdT'):
        fig = plt.figure(figsize=(19,6))
        
        # Generate keys based on variables
        if variables == 'dTdTdT':
            Skeys = ['S1_dT', 'S2_dT**2', 'S3_'+variables]
        
        # Plot each structure function
        for n, clr in enumerate('krb'):
            ax = plt.subplot(1, 3, n+1)
            Skey = Skeys[n]
            
            # Plot with error bars
            ax.errorbar(
                Sn_dict['r'], 
                Sn_dict[Skey],
                yerr=Sn_dict['err_'+Skey],
                color=clr,
                fmt='o', 
                capsize=5
            )
            
            ax.set_xscale('log')
            ax.set_xlabel('Separation (km)')
            ax.set_ylabel(Sn_lbls[Skey])
            
        return fig

Complete Analysis Example
----------------------

Here's a complete example that loads data, calculates structure functions, and creates visualizations:

.. code-block:: python

    def run_analysis(dataset='ARCTERX-Leg2', max_time=10.):
        # Load profilers
        profilers = load_by_asset(['Spray', 'EMApex', 'VMP'])
        
        # Create pairs and calculate separations
        pairs = analyze_separations(dataset, max_time)
        
        # Calculate structure functions
        Sn_dict = analyze_structure(dataset)
        
        # Create visualizations
        sep_fig = plot_separations(pairs)
        struct_fig = plot_structure(Sn_dict)
        
        return pairs, Sn_dict, sep_fig, struct_fig
