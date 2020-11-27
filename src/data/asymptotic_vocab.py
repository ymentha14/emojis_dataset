"""
Functions and methods to assess the asymptotic vocabulary size wrt to the number of users.
This allows us to choose the number of users to run the survey for in a data-driven way.
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from IPython.core.debugger import set_trace
from scipy.spatial import distance


def get_voc_size(serie):
    """
    return the vocabulary size of the words present in serie
    """
    return len(set([word for words_user in serie for word in words_user ]))

def get_distrib(em_serie,ex_distrib=None):
    """
    Return the distribution of words for em_serie.
    Complete the existing distribution support for comparison compatibility
    by filling it with 0 for non present words.
    
    Args:
        em_serie (pd.Serie): serie of words
        
    """
    distrib = em_serie.explode().value_counts()
    distrib /= distrib.sum()
    distrib = distrib.to_dict()

    if ex_distrib is not None:        
        assert(np.isclose(sum(ex_distrib.values()),1))
        dis_set = set(distrib.keys())
        ex_set = set(ex_distrib.keys())
        totkeys = dis_set.union(ex_set)
        distrib = {key:distrib.get(key,0) for key in totkeys}
        # inplace change for ex_distrib
        for key in dis_set - ex_set:
            ex_distrib[key] = 0
        assert(np.isclose(sum(ex_distrib.values()),1))
        assert(set(distrib.keys()) == set(ex_distrib.keys()))
    assert(np.isclose(sum(distrib.values()),1))
    return distrib

def compute_distance_distribs(distrib1,distrib2=None):
    """
    Return the distance between the 2 distributions
    """
    if distrib2 is None:
        return 1
    keys = distrib1.keys()
    distrib1 = [distrib1[key] for key in keys]
    distrib2 = [distrib2[key] for key in keys]
    return distance.jensenshannon(distrib1,distrib2,2)

def build_trajectory(em_serie):
    """
    Return a random vocabulary size trajectory
    
    Args:
        em_serie (pd.Serie): serie of list of words for one emoji (independant users on each row assumed)
    
    Return:
        [dict]: dictionary mapping the size of voc to the number of users used to build this voc
    """
    
    em_serie = em_serie.sample(frac=1)

    # returned dictionary
    ret_dic = {}
    ex_distrib = None
    for n_user in range(1,em_serie.shape[0]+1):
        sub_serie = em_serie[:n_user]
        # voc_size = get_voc_size(sub_serie)
        # ret_dic[n_user] = voc_size
        distrib = get_distrib(sub_serie,ex_distrib)
        distance = compute_distance_distribs(distrib,ex_distrib)
        ret_dic[n_user] = distance
        ex_distrib = distrib
    return ret_dic

def generate_diff_strings(N_common=0):
    """
    Generate a different string at each call
    """
    i = 0
    j = 0
    while True:
        yield "w" + str(i)
        j +=1
        if j > N_common:
            i += 1

def compute_random_trajectory(N_users):
    """
    Compute the trajectory of a series of N_users with 3 words each
    which doesn't have any 2 same words
    """
    words = []
    gen = generate_diff_strings()
    for n in range(N_users):
        user_words = [word for _, word in zip(range(3),gen)]
        words.append(user_words)
    rand_words = pd.Series(words)
    traj = build_trajectory(rand_words)
    return traj

def plot_trajectories(em_serie,ax=None,N_TRAJ = 20,rand_norm_traj = False):
    """
    Generate and plot the random vocabulary size trajectories as described in build_trajectory

    Args:
        em_serie (pd.Serie): serie of list of words for one emoji (independant users on each row assumed)
        N_TRAJ (int): the number of trajectories to compute
        rand_norm_traj (Bool): random trajectory to normalize on
    """
    if ax is None:
        fig,ax = plt.subplots(1)

    trajectories = [pd.Series(build_trajectory(em_serie)) for i in range(N_TRAJ)]

    N = em_serie.shape[0]
    random_traj = pd.Series(compute_random_trajectory(N))
    if rand_norm_traj:
        trajectories = [(random_traj - traj) / random_traj for traj in trajectories]
    else:
        random_traj.plot(ax=ax,color='blueviolet',label='random_ref')

    trajectories = pd.concat(trajectories,axis = 1)

    mean_traj = trajectories.mean(axis=1)
    median_traj = trajectories.median(axis=1)

    for col in trajectories.columns:
        trajectories[col].plot(ax=ax,color='red',alpha=0.2,label='')
    mean_traj.plot(ax=ax,color='green',label='mean')
    median_traj.plot(ax=ax,color='#1261A0',label='median')



    # labels
    ax.set_xlabel('# of users')
    ax.set_ylabel('JS divergence btwn N and N+1')
    ax.legend()

def plot_multi_trajectories(form_df,rand_norm_traj=False,log_scale=False):
    """
    Plot the random trajectories as in plot_trajectories for the 9 first emojis of form_df
    """
    fig,axes = plt.subplots(3,3,figsize=(15,15))
    axes = axes.reshape(-1)
    for ax,col in zip(axes,form_df.columns):
        print(col,end="")
        plot_trajectories(form_df[col],ax,rand_norm_traj=rand_norm_traj)
    
    y_lim = max([ax.get_ylim()[1] for ax in axes])
    if log_scale:
        for ax in axes:
            #ax.set_ylim((0,y_lim))
            ax.set_yscale('log')