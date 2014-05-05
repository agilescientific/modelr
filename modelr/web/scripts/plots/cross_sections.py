import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib import gridspec
import numpy as np
import h5py
f_ = 10
theta_ = 25
trace_ = 38
t_idx_= 115
cmap = 'seismic'

class arg():
  f = f_
  theta = theta_
  trace = trace_
  t_idx = t_idx_
  
args = arg

datafile = h5py.File('testfile.hdf5')
seismic_data = datafile["seismic"]

#max/min amplitude for plot and colorbar scaling
extr1 = 1

fig = plt.figure(figsize=[15,10], facecolor = 'white')
width_ratios = [3,1,1]
gs = gridspec.GridSpec(2, 3, width_ratios = width_ratios, height_ratios = [2,1])


ax11 = plt.subplot(gs[0])
ax12 = plt.subplot(gs[1])
ax13 = plt.subplot(gs[2])
ax21 = plt.subplot(gs[3])
ax22 = plt.subplot(gs[4])
ax23 = plt.subplot(gs[5])

axarr = [[ax11, ax12, ax13],[ax21, ax22, ax23]]

# spatial

im = axarr[0][0].imshow(seismic_data[:,:, args.theta, args.f], 
                    aspect='auto', cmap=cmap, 
                    extent = [0, seismic_data.shape[1], seismic_data.shape[0], 0],
                    vmin = -extr1, vmax = extr1
                    )
axarr[0][0].axvline(x=args.trace, lw=3, color='k', alpha=0.25)
axarr[0][0].axhline(y=args.t_idx, lw=3, color='g')
axarr[0][0].set_title('spatial cross-section')
axarr[0][0].set_ylabel('time')
axarr[0][0].set_xticklabels(' ')
axarr[0][0].grid()

# Put wiggle trace on seismic cross-section

trace1 = seismic_data[:,args.trace, args.theta, args.f]
x = np.arange(seismic_data.shape[0])
gain1 = 5.0

axarr[0][0].plot(args.trace + gain1 * trace1, x, 'k', alpha = 0.9)
axarr[0][0].fill_betweenx(x, args.trace+gain1 * trace1,  args.trace, 
                  gain1 * trace1 > 0,
                  color = 'k', alpha = 0.5)


# Put colorbar legend
colorbar_ax = fig.add_axes([0.55,0.775,0.010,0.08])
fig.colorbar(im, cax=colorbar_ax)
colorbar_ax.text( 0.5, -0.1, '%3.2f' % -extr1, transform=colorbar_ax.transAxes, horizontalalignment='center',verticalalignment='top')
colorbar_ax.text(0.5, 1.1, '%3.2f' % extr1, transform=colorbar_ax.transAxes, horizontalalignment='center')
colorbar_ax.set_axis_off()

axarr[1][0].plot(seismic_data[args.t_idx,:, args.theta, args.f], 'g', lw = 3)
axarr[1][0].set_ylim(-extr1,extr1)
axarr[1][0].set_xlim(0,seismic_data.shape[1])
axarr[1][0].set_ylabel('amplitude')
axarr[1][0].set_xlabel('trace')
axarr[1][0].grid()

# angle column
axarr[0][1].imshow(seismic_data[:, args.trace, :, args.f], 
                    aspect='auto', cmap=cmap, 
                    extent = [0, seismic_data.shape[1], 
                    seismic_data.shape[0], 0],
                    vmin = -extr1, vmax = extr1
                    )
axarr[0][1].axvline(x=args.theta, lw=3, color='r', alpha = 0.25)
axarr[0][1].axhline(y=args.t_idx, lw=3, color='g')
axarr[0][1].set_title('angle gather')
axarr[0][1].set_yticklabels(' ')
axarr[0][1].set_xticklabels(' ')
axarr[0][1].grid()

# Put wiggle trace on AVO cross-section

trace2 = seismic_data[:,args.trace, args.theta, args.f]
x = np.arange(seismic_data.shape[0])
gain2 = gain1*float(width_ratios[0])/width_ratios[1]

axarr[0][1].plot(args.theta + gain2 * trace2, x, 'k', alpha = 0.9)
axarr[0][1].fill_betweenx(x, args.theta + gain2 * trace2,  args.theta, 
                  gain2 * trace2 > 0,
                  color = 'k', alpha = 0.5)
# line plot
data2 = seismic_data[args.t_idx, args.trace, :, args.f]
axarr[1][1].plot(data2, 'g', lw = 3)
axarr[1][1].set_ylim(-extr1,extr1)
axarr[1][1].set_xlim(0,seismic_data.shape[2])
axarr[1][1].set_xlabel(r'$\theta$'+' '+r'$^{\circ}$')
axarr[1][1].set_yticklabels(' ')
axarr[1][1].set_xticks([10,20,30,40])
axarr[1][1].grid()


# wavelet
axarr[0][2].imshow(seismic_data[:, args.trace, args.theta, :],
                    aspect='auto', cmap=cmap, 
                    extent = [0, seismic_data.shape[1], seismic_data.shape[0], 0],
                    vmin = -extr1, vmax = extr1
                    )
axarr[0][2].axvline(x=args.f, lw=3, color='m', alpha = 0.25)
axarr[0][2].axhline(y=args.t_idx, lw=3, color='g')
axarr[0][2].set_title('wavelet gather')
axarr[0][2].set_yticklabels(' ')
axarr[0][2].set_xticklabels(' ')
axarr[0][2].grid()

# Put wiggle trace on wavelet cross-sectoion

trace3 = seismic_data[:,args.trace, args.theta, args.f]
x = np.arange(seismic_data.shape[0])
gain3 = gain1*float(width_ratios[0])/float(width_ratios[2])

axarr[0][2].plot(args.f + gain3 * trace3, x, 'k', alpha = 0.9)
axarr[0][2].fill_betweenx(x, args.f + gain3 * trace3,  args.f, 
                  gain3 * trace3 > 0,
                  color = 'k', alpha = 0.5)
#line plot
data3 = seismic_data[args.t_idx, args.trace, args.theta, :]
axarr[1][2].plot(data3, 'g', lw = 3)
axarr[1][2].set_ylim(-extr1,extr1)
axarr[1][2].set_xlabel('center frequency ' + r'$Hz$')
axarr[1][2].set_xlim(0,seismic_data.shape[3])
axarr[1][2].set_yticklabels(' ')
axarr[1][2].grid()

# remove some whitespace between the axes
gs.update(hspace=0.05,wspace=0.05)

fig.show()