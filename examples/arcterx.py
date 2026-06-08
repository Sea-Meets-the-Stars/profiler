""" Figures for the ARCTERX Leg 2 """


# imports
from importlib import reload
import os
import sys
import glob

import numpy as np


from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator
import matplotlib.gridspec as gridspec

import seaborn as sns

from ocpy.utils import plotting

from profiler import gliderdata
from profiler import floatdata
from profiler import vmpdata
from profiler import triaxusdata
from profiler import profilepairs
from profiler import binning
from profiler.specific import em_apex
from profiler.specific import altos
from cugn import io as cugn_io
from cugn import plotting as cugn_plotting

from IPython import embed

Sn_lbls = cugn_plotting.Sn_lbls
dataset = 'ARCTERX-Leg2'
apath = os.getenv('ARCTERX')

def load_vmp():
    datafile = '/home/xavier/Projects/Oceanography/data/ARCTERX/VMP/combo.nc'
    vmp = vmpdata.VMPData.from_binned_file(datafile, 'cusack', 
                                       dataset, in_field=True,
                                       missid=20000)
    return [vmp]

def load_slocumb():
    datafile = '/home/xavier/Projects/Oceanography/data/ARCTERX/gliders/slocumb/osu685.l3.nc'
    pData = gliderdata.SlocumbData.from_binned_file(
        datafile, 'slocumb', dataset, missid=60000, in_field=True)
    return [pData]

def load_sprays():
    datafiles = glob.glob(os.path.join(apath, 'gliders/spray/*.mat'))
    sprays = []
    for datafile in datafiles:
        s = gliderdata.SprayData.from_binned_file(
            datafile, 'idg', dataset, in_field=True,
            extra_dict={'adcp_on': False})
        sprays.append(s)
    return sprays

def load_solos():
    solos = []
    datafiles = glob.glob('/home/xavier/Projects/Oceanography/data/ARCTERX/Floats/Solo/*.mat')
    for datafile in datafiles:
        solo = floatdata.SoloData.from_binned_file(
            datafile, 'idg', dataset, in_field=True)
        solos.append(solo)
    # 
    return solos

def load_flips():
    flips = []
    datafiles = glob.glob('/home/xavier/Projects/Oceanography/data/ARCTERX/Floats/Flip/*.mat')
    for datafile in datafiles:
        flip = floatdata.FlipData.from_binned_file(
            datafile, 'idg', dataset, in_field=True)
        flips.append(flip)
    # 
    return flips

def load_apexes():
    emapexs = []
    dfiles = glob.glob('/home/xavier/Projects/Oceanography/data/ARCTERX/Floats/EM_Apex/EMApex_data_*.mat')
    for dfile in dfiles:
        pData = em_apex.load_emapex_infield(dfile, dataset, binme=True, add_vel=False)
        #  
        emapexs += pData
    return emapexs

def load_altos():
    dfile = '/home/xavier/Projects/Oceanography/data/ARCTERX/Floats/Alto/tn441_alto_gridded.mat'
    my_altos = altos.load_infield(dfile, dataset, missid_offset=100000)
    return my_altos

def load_triaxes():
    tris = []
    datafiles = glob.glob('/home/xavier/Projects/Oceanography/data/ARCTERX/Triaxus/CTD*.mat')
    for datafile in datafiles:
        missid = int(datafile.split('/')[-1].split('_')[1].split('.')[0]) + 50000
        #embed(header='load_triaxes: 79')
        triaxus = triaxusdata.TriaxusData.from_binned_file(datafile, 'triaxus', 
                                       dataset, in_field=True,
                                       missid=missid)
        tris.append(triaxus)
    # 
    return tris

all_assets = ['Alto', 'Flip', 'Slocumb', 'Spray', 'Solo', 
              'EMApex', 'VMP', 'Triaxus']

def load_by_asset(assets:list):
    # Generate pairs
    profilers = []
    for asset in assets:
        if asset == 'Spray':
            profilers += load_sprays()
        elif asset == 'Solo':
            profilers += load_solos()
        elif asset == 'Flip':
            profilers += load_flips()
        elif asset == 'Alto':
            profilers += load_altos()
        elif asset == 'EMApex':
            profilers += load_apexes()
        elif asset == 'VMP':
            profilers += load_vmp()
        elif asset == 'Triaxus':
            profilers += load_triaxes()
        elif asset == 'Slocumb':
            profilers += load_slocumb()
        else:
            raise IOError(f"Bad asset! {asset}")
    # Return
    return profilers

def fig_separations(dataset:str, outroot='fig_sep', 
                    max_time:float=10.,
                    assets:list=all_assets):
    outfile = f'{outroot}_{dataset}.png'

    profilers = load_by_asset(assets)
    
    # Generate pairs
    #embed(header='119 of figs')
    reload(profilepairs)
    print("TURN OF RANDOMIZE=FALSE!!")
    mixPairs = profilepairs.ProfilerPairs(profilers, 
                                          max_time=max_time,
                                          debug=False,
                                          randomize=False)

    # Start the figure
    fig = plt.figure(figsize=(12,6))
    plt.clf()
    gs = gridspec.GridSpec(1,2)

    # Lat/lon
    ax_ll = plt.subplot(gs[0])

    for mid in np.unique(mixPairs.data('missida',2).astype(int)):
        fill = True
        if mid < 100:
            marker = '+'
        elif mid < 10000:
            marker = '*'
        elif mid < 20000:
            marker = 'x'
        else:
            marker = '^'
        idx = mixPairs.data('missida',2) == mid
        ax_ll.scatter(mixPairs.data('lon', 2)[idx], 
            mixPairs.data('lat', 2)[idx], s=2, label=f'MID={mid}',
            marker=marker)

    ax_ll.set_xlabel('Longitude [deg]')
    ax_ll.set_ylabel('Latitude [deg]')
    ax_ll.legend(fontsize=4, ncol=2,
                 loc='upper left')

    ax_ll.grid()
    ax_ll.xaxis.set_major_locator(MultipleLocator(1.0))  # Major ticks every 2 units


    # Separations
    ax_r = plt.subplot(gs[1])
    _ = sns.histplot(mixPairs.r, bins=50, log_scale=True, ax=ax_r)
    # Label
    ax_r.set_xlabel('Separation [km]')
    ax_r.set_ylabel('Count')
    ax_r.set_yscale('log')

    # Add dataset
    lsz = 16.
    ax_r.text(0.1, 0.9, dataset, transform=ax_r.transAxes, fontsize=lsz)
    # Label time separation
    ax_r.text(0.1, 0.8, f't < {max_time} hours', transform=ax_r.transAxes, fontsize=15)

    for ax in [ax_ll, ax_r]:
        plotting.set_fontsize(ax, 15) 
        
    plt.tight_layout()#pad=0.0, h_pad=0.0, w_pad=0.3)
    plt.savefig(outfile, dpi=300)
    print(f"Saved: {outfile}")

def fig_structure(dataset:str, outroot='fig_structure',
                  variables = 'duLduLduL',
                  assets:list=['Spray', 'Solo', 'EMApex'],
                  iz: int|float=5, tcut:tuple=None,
                  calculate:bool=True,
                  minN:int=10, avoid_same_glider:bool=True,
                  debug:bool=False,
                  show_correct:bool=False):

    profilers = load_by_asset(assets)

    # Skip velocities?
    skip_vel = False
    if dataset in ['ARCTERX-Leg2']:
        skip_vel = True

    # Outfile
    if iz >= 0:
        outfile = f'{outroot}_z{(iz+1)*10}_{dataset}_{variables}.png'
    else:
        outfile = f'{outroot}_iso{np.abs(iz)}_{dataset}_{variables}.png'

    # Load
    if iz >= 0:
        gpair_file = cugn_io.gpair_filename(
            dataset, iz, not avoid_same_glider)
        gpair_file = os.path.join('..', 'Analysis', 'Outputs', gpair_file)

    if variables not in ['duLduLduL', 'dTdTdT']:
        raise NotImplementedError('Not ready for these variablaes')
    # Cut on valid velocity data 
    nbins = 20
    rbins = 10**np.linspace(0., np.log10(400), nbins) # km

    gPairs = profilepairs.ProfilerPairs(
        profilers, max_time=10., 
        avoid_same_glider=avoid_same_glider,
        #remove_nans=True,
        debug=debug)
    # Isopycnals?
    if iz < 0:
        gPairs.prep_isopycnals('t')
    gPairs.calc_delta(iz, variables, skip_velocity=skip_vel)
    gPairs.calc_Sn(variables)

    Sn_dict = gPairs.calc_Sn_vs_r(rbins, nboot=100)
    gPairs.calc_corr_Sn(Sn_dict) 
    gPairs.add_meta(Sn_dict)

    #embed(header='fig_structure: 215')

    # Start the figure
    fig = plt.figure(figsize=(19,6))
    plt.clf()
    gs = gridspec.GridSpec(1,3)

    goodN = np.array(Sn_dict['config']['N']) > minN
    

    # Generate the keys
    if variables == 'duLduLduL':
        Skeys = ['S1_duL', 'S2_duL**2', 'S3_'+variables]
    elif variables == 'duTduTduT':
        Skeys = ['S1_duT', 'S2_duT**2', 'S3_'+variables]
    elif variables == 'duLTduLTduLT':
        Skeys = ['S1_duLT', 'S2_duLT**2', 'S3_'+variables]
    elif variables == 'duLdSdS':
        Skeys = ['S1_duL', 'S2_dS**2', 'S3_'+variables]
    elif variables == 'duLdTdT':
        Skeys = ['S1_duL', 'S2_dT**2', 'S3_'+variables]
    elif variables == 'duLduTduT':
        Skeys = ['S1_duL', 'S2_duT**2', 'S3_'+variables]
    elif variables == 'dTdTdT':
        Skeys = ['S1_dT', 'S2_dT**2', 'S3_'+variables]
    else:
        raise IOError("Bad variables")


    for n, clr in enumerate('krb'):
        ax = plt.subplot(gs[n])
        Skey = Skeys[n] 
        ax.errorbar(Sn_dict['r'][goodN], 
                    Sn_dict[Skey][goodN], 
                    yerr=Sn_dict['err_'+Skey][goodN],
                    color=clr,
                    fmt='o', capsize=5)  # fmt defines marker style, capsize sets error bar cap length

        # Corrected
        if n > 0 and show_correct:
            corr_key = Skey[0:2]+'corr'+Skey[2:]
            ax.plot(Sn_dict['r'][goodN], 
                    Sn_dict[corr_key][goodN],  
                    'x',
                    color=clr)
        elif 'med_S1' in Sn_dict.keys():
            ax.plot(Sn_dict['r'][goodN], Sn_dict['med_S1'][goodN],  
                    'x', color=clr)


        ax.set_xscale('log')
    #
        ax.set_xlabel('Separation (km)')
        ax.set_ylabel(Sn_lbls[Skey])

        # Label time separation
        if n == 2:
            same_glider = 'True' if avoid_same_glider else 'False'
            if iz >=0:
                lbl = f'{dataset}\n depth = {(iz+1)*10} m, t<{int(Sn_dict['config']['max_time'])} hr\nAvoid same glider? {same_glider}\n {variables}' 
            else:
                lbl = f'{dataset}\n density = {1000+np.abs(iz)} kg/m^3, t<{int(Sn_dict['config']['max_time'])} hr\nAvoid same glider? {same_glider}\n {variables}'
            ax.text(0.1, 0.8, lbl,
                transform=ax.transAxes, fontsize=16, ha='left')
        # 0 line
        ax.axhline(0., color='red', linestyle='--')

        plotting.set_fontsize(ax, 19) 
        ax.grid()
        
    plt.tight_layout()#pad=0.0, h_pad=0.0, w_pad=0.3)
    plt.savefig(outfile, dpi=300)
    print(f"Saved: {outfile}")


def fig_dT2_vs_depth(dataset:str='ARCTERX-Leg2', 
                     outfile='fig_dT2_vs_depth.png',
                  variables = 'dTdTdT',
                  iz:int=5, tcut:tuple=None,
                  calculate:bool=True,
                  minN:int=10, avoid_same_glider:bool=True,
                  show_correct:bool=True):

    # Skip velocities?
    skip_vel = False
    if dataset in ['ARCTERX-Leg2']:
        skip_vel = True

    # Load
    gpair_file = cugn_io.gpair_filename(
        dataset, iz, not avoid_same_glider)
    gpair_file = os.path.join('..', 'Analysis', 'Outputs', gpair_file)

    # Cut on valid velocity data 
    nbins = 20
    rbins = 10**np.linspace(0., np.log10(400), nbins) # km
    # Load dataset
    gData = gliderdata.load_dataset(dataset)
    if not skip_vel:
        gData = gData.cut_on_good_velocity()
    if tcut is not None:
        gData = gData.cut_on_reltime(tcut)

    # Generate pairs
    gPairs = profilepairs.ProfilerPairs(
        gData, max_time=10., 
        avoid_same_glider=avoid_same_glider)

    # Calculate as a function of depth
    Sndicts = []
    for iz in range(50):
        gPairs.calc_delta(iz, variables, skip_velocity=skip_vel)
        gPairs.calc_Sn(variables)

        Sn_dict = gPairs.calc_Sn_vs_r(rbins, nboot=10000)
        gPairs.calc_corr_Sn(Sn_dict) 
        gPairs.add_meta(Sn_dict)

        # Grab
        Sndicts.append(Sn_dict.copy())

    embed(header='fig_structure: 342')

    # Start the figure
    fig = plt.figure(figsize=(10,8))
    plt.clf()
    gs = gridspec.GridSpec(1,1)
    ax = plt.subplot(gs[0])

    Skeys = ['S1_dT', 'S2_dT**2', 'S3_'+variables]
    Skey = Skeys[1] 

    for iz in [0, 5, 10, 15, 20]:

        Sn_dict = Sndicts[iz]
        goodN = np.array(Sn_dict['config']['N']) > minN
        ax.plot(Sn_dict['r'][goodN], 
                    Sn_dict[Skey][goodN], '-o',
                    label=f'{(iz+1)*10} m')

    ax.set_xscale('log')
    ax.set_xlabel('Separation (km)')
    ax.set_ylabel(Sn_lbls[Skey])

    # Label time separation
    same_glider = 'True' if avoid_same_glider else 'False'
    ax.text(0.1, 0.8, 
            f'{dataset}\n t<{int(Sn_dict['config']['max_time'])} hr\nAvoid same glider? {same_glider}\n {variables}', 
        transform=ax.transAxes, fontsize=16, ha='left')
    # 0 line
    #ax.axhline(0., color='black', linestyle='--')

    plotting.set_fontsize(ax, 19) 
    ax.grid()
    ax.legend(fontsize=17.)
        
    plt.tight_layout()#pad=0.0, h_pad=0.0, w_pad=0.3)
    plt.savefig(outfile, dpi=300)
    print(f"Saved: {outfile}")

def fig_Sn_depth(dataset:str, outroot='fig_Sn_depth',
    variables = 'duLduLduL', minN:int=10,
    nz:int=50):

    outfile = f'{outroot}_{dataset}_{variables}'
    varlbl = variables
    
    
    # Load and parse
    all_N = []
    all_S1 = []
    all_S2 = []
    all_S3 = []
    for iz in range(nz):
        # Load
        gpair_file = cugn_io.gpair_filename(dataset, iz, variables)
        gpair_file = os.path.join('..', 'Analysis', 'Outputs', gpair_file)

        Sn_dict = gliderpairs.load_Sndict(gpair_file)
        # Grab em
        all_N.append(Sn_dict['N'])
        all_S1.append(Sn_dict['S1'])
        all_S2.append(Sn_dict['S2corr'])
        all_S3.append(Sn_dict['S3corr'])
        # r
        if iz == 0:
            r = Sn_dict['r']

    all_N = np.array(all_N)
    all_S1 = np.array(all_S1)
    all_S2 = np.array(all_S2)
    all_S3 = np.array(all_S3)

    goodN = all_N[0] > minN

    # Median
    med_S1 = np.median(all_S1, axis=0)
    med_S2 = np.median(all_S2, axis=0)
    med_S3 = np.median(all_S3, axis=0)

    std_S1 = np.std(all_S1, axis=0)
    std_S2 = np.std(all_S2, axis=0)
    std_S3 = np.std(all_S3, axis=0)

    #embed(header='297 of figs')

    # Start the figure
    fig = plt.figure(figsize=(19,6))
    plt.clf()
    gs = gridspec.GridSpec(1,3)

    for n, clr in enumerate(['g','r','b']):
        ax = plt.subplot(gs[n])
        Skey = f'S{n+1}'
        if n == 0:
            Sn = all_S1
            medSn = med_S1
        elif n == 1:
            Sn = all_S2
            medSn = med_S2
        else:
            Sn = all_S3
            medSn = med_S3

        for iz in range(nz):
            #a = 0.9 - 0.8*iz/nz
            a = 0.1 + 0.8*iz/nz
            ax.plot(r[goodN], Sn[iz][goodN], color=clr, alpha=a)

        # Median
        ax.plot(r[goodN], medSn[goodN], color='k')

        ax.set_xscale('log')
        ax.set_xlabel('Separation (km)')
        ax.set_ylabel(r'$S_'+str(n+1)+r'$ Corrected')
        # 0 line
        ax.axhline(0., color='k', linestyle='--')

        plotting.set_fontsize(ax, 19) 
        ax.grid()

        ax.set_xlim(1., 100.)
        ax.minorticks_on()

        # Label time separation
        if n == 2:
            ax.text(0.9, 0.1, f'{dataset}\n  {varlbl}', 
                transform=ax.transAxes, fontsize=18, ha='right')
        

    plt.tight_layout()#pad=0.0, h_pad=0.0, w_pad=0.3)
    plt.savefig(outfile, dpi=300)
    print(f"Saved: {outfile}")
    
def fig_neg_mean_spatial(max_time=10., avoid_same_glider=True, nbins=20, 
                 iz = 5, dataset = 'ARCTERX', minN:int=10,
                 variables = 'duLduLduL', connect_dots:bool=False,
                 show_zero:bool=False,
                 outfile='fig_ARCTERX_negmean_spatial.png'):

    # ARCTERX
    rbins = 10**np.linspace(0., np.log10(400), nbins) # km

    
    # Load dataset
    gData = gliderdata.load_dataset(dataset)

    # Cut on valid velocity data 
    gData = gData.cut_on_good_velocity()

    # Generate pairs
    gPairs = gliderpairs.GliderPairs(
        gData, max_time=max_time, 
        avoid_same_glider=avoid_same_glider)
    gPairs.calc_delta(iz, variables)
    gPairs.calc_Sn(variables)

    #embed(header='fig_neg_mean_spatial: 366')    

    #Sn_dict = gPairs.calc_Sn_vs_r(rbins, nboot=10000)
    #gPairs.calc_corr_Sn(Sn_dict) 
    

    #goodN = Sn_dict['config']['N'] > minN

    # Grab them
    neg_idx = np.arange(11,15)

    # Maybe loop over these?




    fig = plt.figure(figsize=(7,6))
    plt.clf()
    ax_ll = plt.gca()

    # 
    for ridx in [1]:#,1,2]:
        ss = neg_idx[ridx]
        if show_zero:
            ss = neg_idx[0]-1
            if ridx > 0:
                break
        #print(f"rbin: {rbins[ss],rbins[ss+1]}, Stat: {Sn_dict['S1_duL'][ss]}")

        in_r = (gPairs.r > rbins[ss]) & (gPairs.r <= rbins[ss+1])
        for tt in [0,1]:
            m = 'o' if tt == 0 else 's'
            ec = None #'k' if tt == 0 else None
            scatter = ax_ll.scatter(gPairs.data('lon', tt)[in_r],  
                    gPairs.data('lat', tt)[in_r], 
                    c=gPairs.S1[in_r],
                                    marker=m,
                    edgecolor=ec,
                    cmap='seismic',
                    vmin=-1., vmax=1.,
                    s=5)#, label=f'MID={mid}')

        # Connect with a line
        if connect_dots:
            for tt in np.where(in_r)[0]:
                ax_ll.plot(
                    [gPairs.data('lon', 0)[tt], gPairs.data('lon', 1)[tt]],  
                    [gPairs.data('lat', 0)[tt], gPairs.data('lat', 1)[tt]],
                    color='gray', ls=':', zorder=10, lw=0.3)  
        # Add text
        ax_ll.text(0.1, 0.2, f'{dataset}\n depth = {(iz+1)*10} m \n r={int(np.round(rbins[ss])),int(np.round(rbins[ss+1]))} km',
                transform=ax_ll.transAxes, fontsize=16, ha='left')

    # Color
    cb = plt.colorbar(scatter, pad=0., fraction=0.030)
    cb.set_label(r'$\delta u_L$ (m/s)', fontsize=14)


    ax_ll.set_xlabel('Longitude [deg]')
    ax_ll.set_ylabel('Latitude [deg]')
    
    plt.tight_layout()#pad=0.0, h_pad=0.0, w_pad=0.3)
    plt.savefig(outfile, dpi=300)
    print(f"Saved: {outfile}")


def fig_Sn_distribution(dataset:str, outfile:str,
    variables:str, Sn:str, rval:float,
    iz:int=5, tcut=None,
    avoid_same_glider=True):

    #outfile = f'{outroot}_{dataset}_{variables}'
    #varlbl = variables
    
    # Cut on valid velocity data 
    nbins = 20
    rbins = 10**np.linspace(0., np.log10(400), nbins) # km

    # Pick out the radial bin
    rbool = (rval> rbins) & (rval < np.roll(rbins,-1))
    ir = np.where(rbool)[0][0]

    # Load dataset
    gData = gliderdata.load_dataset(dataset)
    gData = gData.cut_on_good_velocity()
    if tcut is not None:
        gData = gData.cut_on_reltime(tcut)

    # Generate pairs
    gPairs = gliderpairs.GliderPairs(
        gData, max_time=10., 
        avoid_same_glider=avoid_same_glider)
    gPairs.calc_delta(iz, variables)
    gPairs.calc_Sn(variables)

    Sn_dict = gPairs.calc_Sn_vs_r(rbins, nboot=10000)
    gPairs.calc_corr_Sn(Sn_dict) 
    gPairs.add_meta(Sn_dict)

    all_vals = getattr(gPairs, Sn)
    in_r = (gPairs.r > rbins[ir]) & (gPairs.r <= rbins[ir+1])
    vals = all_vals[in_r]

    # Normalize by the error
    err_key = 'err_'+Sn+f'_{variables}'
    vals = vals/(Sn_dict[err_key][ir]*np.sqrt(np.sum(in_r)))
    #embed(header='fig_Sn_distribution: 493')
    
    # Start the figure
    fig = plt.figure(figsize=(12,6))
    plt.clf()
    gs = gridspec.GridSpec(1,1)

    ax = plt.subplot(gs[0])

    hist, bins = np.histogram(vals, bins=100)#, density=True)
    # Plot
    ax.hist(vals, bins=bins, color='green')
    #sns.histplot(vals, bins=100, ax=ax, color='green')
                 #log_scale=(False,True))

    ax.set_xlabel(Sn+r'/$\sigma('+f'{Sn}'+r')$')
    #ax.set_ylabel(r'$S_'+str(n+1)+r'$ Corrected')
    # 0 line
    #ax.axhline(0., color='k', linestyle='--')

    # Overlay a Gaussian
    area = np.sum(hist)*(bins[1]-bins[0])

    #embed(header='fig_Sn_distribution: 513')

    x = np.linspace(-5., 5., 100)
    y = np.exp(-0.5*x**2)/np.sqrt(2*np.pi)
    a_y = np.sum(y)*(x[1]-x[0])
    ax.plot(x, y*area/a_y, color='red', linestyle='--')

    plotting.set_fontsize(ax, 19) 
    ax.grid()

    ax.text(0.1, 0.8, f'{dataset}\n depth = {(iz+1)*10} m, \nr={int(np.round(rbins[ir])),int(np.round(rbins[ir+1]))} km',
                transform=ax.transAxes, fontsize=16, ha='left')

    #ax.set_xlim(1., 100.)
    ax.minorticks_on()

    plt.tight_layout()#pad=0.0, h_pad=0.0, w_pad=0.3)
    plt.savefig(outfile, dpi=300)
    print(f"Saved: {outfile}")
    

def main(flg):
    if flg== 'all':
        flg= np.sum(np.array([2 ** ii for ii in range(25)]))
    else:
        flg= int(flg)

    # Separations
    if flg == 1:
        fig_separations('ARCTERX-Leg2')
        fig_separations('ARCTERX-Leg2', outroot='fig_sep_adcp_',
                        assets=['Spray', 'EMApex', 'Triaxus'], 
                        max_time=10.)
        #fig_separations('ARCTERX-Leg2', outroot='fig_sep_test',
        #                assets=['Solo', 'Slocumb'],
        #                max_time=10.)

    # dTdTdT
    if flg == 2:
        skip_assets = ['Alto', 'Flip', 'Solo']#, 'Slocumb', 'Spray', 'Solo', 'EMApex', 'VMP', 'Triaxus']
        sub_assests = all_assets.copy()
        for skip in skip_assets:
            sub_assests.remove(skip)

        fig_structure('ARCTERX-Leg2', variables='dTdTdT',
           assets=sub_assests)
        #fig_structure('ARCTERX-Leg2', variables='dTdTdT',
        #              assets=['Alto'],  # No good
                      #assets=['EMApex'], 
                      #assets=['Triaxus'], 
                      #assets=['Flip'],  # No good
                      #assets=['Solo'],  # No good
        #              outroot='fig_struct_test',
        #              debug=True)
        #fig_structure('ARCTERX-Leg2', variables='dTdTdT',
        #              assets=['Spray'], iz=-23.5,
        #              outroot='fig_struct_Spray')

    # dT**2 vs. z
    if flg == 3:
        fig_dT2_vs_depth()

# Command line execution
if __name__ == '__main__':
    import sys

    if len(sys.argv) == 1:
        flg = 0

        #flg = 1
        
    else:
        flg = sys.argv[1]

    main(flg)