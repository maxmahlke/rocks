#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Author: Benoit Carry
    Date: 06 June 2020

    Plot utilities

    Part of the rocks CLI suite
'''

import numpy as np
import matplotlib.pyplot as plt

# Define colors/markers for all methods in ssodnet
s={'avg':{'color':'black'},
   'std':{'color':'darkgrey'},
  #-Space mission
   'SPACE':{'color':'gold', 'marker':'X'}, 
  #-3d shape modeling
   'ADAM':{'color':'navy', 'marker':'v'}, 
   'SAGE':{'color':'mediumblue', 'marker':'^'}, 
   'KOALA':{'color':'slateblue', 'marker':'<'}, 
   'Radar':{'color':'cornflowerblue', 'marker':'>'}, 
  #-LC with scaling
   'LC+OCC':{'color':'lightgreen', 'marker':'v'}, 
   'LC+AO':{'color':'forestgreen', 'marker':'^'},  #deprecated =LC+IM
   'LC+IM':{'color':'forestgreen', 'marker':'^'}, 
   'LC+TPM':{'color':'darkgreen', 'marker':'<'}, 
   'LC-TPM':{'color':'green', 'marker':'>'}, 
  #-Thermal models
   'STM':{'color':'grey', 'marker':'D'}, 
   'NEATM':{'color':'grey', 'marker':'o'}, 
   'TPM':{'color':'darkgrey', 'marker':'s'}, 
  #-triaxial ellipsoid
   'TE-IM':{'color':'blue', 'marker':'o'},
  #-2d on sky
   'OCC':{'color':'brown', 'marker':'P'}, 
   'IM':{'color':'oranged', 'marker':'p'}, 
   'IM-PSF':{'color':'tomato', 'marker':'H'}, 
  #-Mass from binary
   'Bin-IM':{'color':'navy', 'marker':'v'}, 
   'Bin-Genoid':{'color':'mediumblue', 'marker':'^'}, 
   'Bin-PheMu':{'color':'slateblue', 'marker':'<'}, 
   'Bin-Radar':{'color':'cornflowerblue', 'marker':'>'}, 
  #-Mass from deflection
   'DEFLECT':{'color':'brown', 'marker':'D'}, 
   'EPHEM':{'color':'red', 'marker':'o'}, 
  #-Taxonomy
   'Phot':{'color':'red', 'marker':'s'}, 
   'Spec':{'color':'red', 'marker':'s'}, 
   }

ylabels={'diameter':'Diameter (km)',
         'mass': 'Mass (kg)', 
         'albedo': 'Albedo'}




def show_scatter_hist(info, par, figname):

    # translate input
    n=len(info[1])
    x=np.linspace(1,n,n)

    val=info[1].get(par).values
    unc=info[1].get('err_'+par).values
    avg=info[0][0]
    std=info[0][1]

    # TBD: Sort values by year? or let it as in ssodnet?
    # TBD: offer it as option?



    # Define figure layout
    fig = plt.figure(figsize=(12, 8))
    gs = fig.add_gridspec(1, 2, width_ratios=(7, 2), wspace=0.05, 
                          left=0.07, right=0.97, bottom=0.05, top=0.87)
    ax = fig.add_subplot(gs[0])
    ax_histy = fig.add_subplot(gs[1], sharey=ax)


    # the scatter plot:
    # mean and std
    lavg = ax.axhline(avg, label='Average',
               color=s['avg']['color'])
    lstd = ax.axhline(avg+std, label='1$\sigma$ deviation',
               color=s['std']['color'], linestyle='dashed')
    lstd = ax.axhline(avg-std, 
               color=s['std']['color'], linestyle='dashed')

    # TBD: fill the 1sigma range?
    #lstd = ax.fill_between(x, avg-std, avg+std,
    #                label='1$\sigma$ deviation',
    #                color=s['std']['color'])
 
    # all methods
    for i in np.unique(info[1].method):
        p=np.where(info[1].method==i)
        if True in info[1].selected.values[p]:
            fcol=s[i]['color']
        else:
            fcol='none'
        ax.scatter(x[p], val[p], marker=s[i]['marker'], s=80, label=i, 
                   facecolors=fcol, edgecolors=s[i]['color'] )
        ax.errorbar(x[p],val[p], yerr=unc[p], c=s[i]['color'], linestyle='')

    # axes
    #ax.set_ylabel('Diameter (km)')
    ax.set_ylabel(ylabels[par])
    ax.set_xticks(x)

    # TBD: one legend for avg/std, one for methods?
    ax.legend(loc='best',ncol=2)


    # place shortbib on top for quick identification 
    axtop = ax.twiny()
    axtop.set_xticks(x)
    axtop.set_xticklabels(info[1].shortbib, rotation=25, ha='left') 

 
    # Histogram
    range=ax.get_ylim()
    nbins=10
    ax_histy.tick_params(axis="y", labelleft=False)
    sel=np.where(info[1].selected==True)

    na, ba, pa = ax_histy.hist(val, bins=nbins, range=range,
            orientation='horizontal', color='grey', label='All')
    ns, bs, ps = ax_histy.hist(val[sel], bins=nbins, range=range,
            orientation='horizontal', color='gold', label='Selected')

    ax_histy.legend(loc='lower right')

    plt.savefig(figname)
    plt.close()



