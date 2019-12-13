"""
Workflow of mutual information between two continuous variables
===============================================================

This example illustrates how to compute the mutual information between two
continuous variables and also perform statistics. Usually, the first variable
is an electrophysiological data (M/EEG, intracranial) and a regressor. This
kind of mutual information is equivalent to a traditional correlation. Note
that the regressor variable can either be univariate (single column) or
multivariate (multiple columns). For further details, see
Ince et al., 2017 :cite:`ince2017statistical`
"""
import numpy as np

from frites.simulations import sim_multi_suj_ephy, sim_mi_cc
from frites.dataset import DatasetEphy
from frites.workflow import WfMi

import matplotlib.pyplot as plt
plt.style.use('seaborn-white')


###############################################################################
# Simulate electrophysiological data
# ----------------------------------
#
# Let's start by simulating MEG / EEG electrophysiological data coming from
# multiple subjects using the function
# :func:`frites.simulations.sim_multi_suj_ephy`. As a result, the `x` output
# is a list of length `n_subjects` of arrays, each one with a shape of
# n_epochs, n_sites, n_times

modality = 'meeg'
n_subjects = 5
n_epochs = 400
n_times = 100
x, roi, time = sim_multi_suj_ephy(n_subjects=n_subjects, n_epochs=n_epochs,
                                  n_times=n_times, modality=modality,
                                  random_state=0)

###############################################################################
# Extract the regressor variable
# ------------------------------
#
# Once we have the electrophysiological, we need to extract the second variable
# that is going to serves for computing the "correlation" at each time point
# and at each site / channel / sensor. To do this, we can simply take the mean
# over time points and region of interest in a time window

sl = slice(40, 60)
y = [x[k][..., sl].mean(axis=(1, 2)) for k in range(len(x))]

###############################################################################
# .. note::
#     Taking the mean across time points and space is exactly the behavior of
#     the function :func:`frites.simulations.sim_mi_cc`

###############################################################################
# Define the electrophysiological dataset
# ---------------------------------------
#
# Now we define an instance of :class:`frites.dataset.DatasetEphy`

dt = DatasetEphy(x, y, roi)


###############################################################################
# Compute the mutual information
# ------------------------------
#
# Once we have the dataset instance, we can then define an instance of workflow
# :class:`frites.workflow.WfMi`. This instance is used to compute the mutual
# information

# mutual information type ('cc' = continuous / continuous)
mi_type = 'cc'

# define the workflow
wf = WfMi(mi_type)
# compute the mutual information
mi, _ = wf.fit(dt, level=None)

# plot the information shared between the data and the regressor y
plt.plot(time, mi)
plt.xlabel("Time (s)"), plt.ylabel("MI (bits)")
plt.title('I(C; C)')
plt.show()

###############################################################################
# Multivariate regressor
# ----------------------
#
# Example above uses a univariate regressor (i.e a single column vector). But
# multivariate regressors are also supported. Here is an example
# of multivariate regressor

# take the mean over time points [10, 30]
sl = slice(10, 30)
_y_1 = [x[k][..., sl].mean(axis=(1, 2)) for k in range(len(x))]
# take the mean over time points [70, 90]
sl = slice(70, 90)
_y_2 = [x[k][..., sl].mean(axis=(1, 2)) for k in range(len(x))]
# concatenate the two vectors
y_mv = [np.c_[_y_1[k], _y_2[k]] for k in range(len(_y_1))]
print([k.shape for k in y_mv])


# compute the mutual information
dt = DatasetEphy(x, y_mv, roi)
mi, _ = WfMi('cc').fit(dt, level=None)
# plot the result
plt.plot(time, mi)
plt.xlabel("Time (s)"), plt.ylabel("MI (bits)")
plt.title("Multivariate regressor")
plt.show()

###############################################################################
# Evaluate the statistics
# -----------------------
#
# In the section above, the input parameter `stat_method=None` specifies that
# no statistics are going to be computed. Here, we show how to compute either
# within (ffx) or between subject (rfx) statistics.

mi_type = 'cc'
n_perm = 200
y, _ = sim_mi_cc(x, snr=.1)

# within subject statistics (ffx=fixed-effect)
ffx_stat = 'ffx_cluster_tfce'
dt_ffx = DatasetEphy(x, y, roi)
wf_ffx = WfMi(mi_type, 'ffx')
mi_ffx, pv_ffx = wf_ffx.fit(dt_ffx, level='cluster', cluster_th='tfce',
                            n_perm=n_perm)

# between-subject statistics (rfx=random-effect)
dt_rfx = DatasetEphy(x, y, roi)
wf_rfx = WfMi(mi_type, 'rfx')
mi_rfx, pv_rfx = wf_rfx.fit(dt_rfx, level='cluster', cluster_th='tfce',
                            n_perm=n_perm)

# plot the comparison
fig = plt.figure(figsize=(10, 8))
fig.suptitle("Fixed-effect vs. Random-effect")

plt.subplot(221)
plt.plot(time, mi_ffx)
plt.xlabel("Time (s)"), plt.ylabel("MI (bits)")
plt.title(f"Mutual information (FFX / cluster / TFCE)")
plt.subplot(223)
plt.plot(time, pv_ffx)
plt.xlabel("Time (s)"), plt.ylabel("P-value")
plt.subplot(222)
plt.plot(time, mi_rfx)
plt.xlabel("Time (s)"), plt.ylabel("MI (bits)")
plt.title(f"Mutual information (RFX / cluster / TFCE)")
plt.subplot(224)
plt.plot(time, pv_rfx)
plt.xlabel("Time (s)"), plt.ylabel("P-value")
plt.show()
