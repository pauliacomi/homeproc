import numpy


def plot_pxrd(
    files,
    ax,
    offset=1,
    scale="lin",
    normalize=False,
    limits=None,
):
    """Plot a sequence of PXRD patterns for comparison."""
    limits = limits if limits else (5, 60)
    for ind, pxrd in enumerate(files):
        xy = numpy.array([pxrd['x'], pxrd['data']])
        xy = xy[:, (xy[0, :] > limits[0]) & (xy[0, :] < limits[1])]
        x = xy[0]
        y = xy[1]
        if normalize:
            y = y / numpy.max(y)
        if scale == "log":
            y = numpy.log(y)
        elif scale == "sqrt":
            y = numpy.sqrt(y)

        y = y - ind * offset

        try:
            label = pxrd['name']
        except:
            label = 'simulated'

        ax.plot(x, y, label=label)

    ax.set_xlim(limits)
    ax.set_xlabel("Angle $2\\theta$ [°]", fontsize=15)

    if scale == "log":
        ax.set_ylabel("Intensity, log [a.u.]", fontsize=15)
    elif scale == "sqrt":
        ax.set_ylabel("Intensity, sqrt [a.u.]", fontsize=15)
    else:
        ax.set_ylabel("Intensity [a.u.]", fontsize=15)

    ax.set_yticks([])
    ax.tick_params(axis='both', labelsize=13)