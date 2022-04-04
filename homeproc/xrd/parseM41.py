def readm41(path):
    """Parses JANA M41 files to get UC parameters."""

    with open(path) as file:
        lines = file.readlines()

    # Find blocks
    blk1, blk2, blk3 = 0, 0, 0
    for n, line in enumerate(lines):
        if "*******" in line:
            blk1 = n
        elif "------" in line:
            if blk2 == 0:
                blk2 = n
            else:
                blk3 = n

    data = {}

    data['shifts'] = {
        key: val
        for (key, val) in zip(
            ["zero", "sycos", "sysin"],
            map(float, lines[blk1 + 2].strip().split()[:-1]),
        )
    }
    # bkg = list(map(float, lines[blk1 + 4].strip().split()[:-1]))

    phase = None
    phases = []
    for n, line in enumerate(lines[blk1:blk2]):
        if "phase" in line:
            phases.append(n + blk1)
            phase = True
    if len(phases) == 0:
        phases.append(blk1 + 5)

    for pn, ll in enumerate(phases):
        if phase is None or phase == "base":
            phase = "base"
        else:
            phase = lines[ll].split()[-1]

        data[phase] = {}

        line1 = phases[pn]
        line2 = phases[pn + 1] if pn + 1 != len(phases) else blk2

        for n, line in enumerate(lines[line1:line2]):
            if "Cell" in line:
                data[phase]["cell"] = {
                    key: val
                    for (key, val) in zip(
                        ["a", "b", "c", "alpha", "beta", "gamma"],
                        map(float, lines[line1 + n + 1].strip().split()[:-1]),
                    )
                }
            elif "Gaussian" in line:
                data[phase]["profile_gaussian"] = {
                    key: val
                    for (key, val) in zip(
                        ["U", "V", "W", "P"],
                        map(float, lines[line1 + n + 1].strip().split()[:-1]),
                    )
                }
            elif "Lorentzian" in line:
                data[phase]["profile_lorentzian"] = {
                    key: val
                    for (key, val) in zip(
                        ["LX", "LXe", "LY", "LYe"],
                        map(float, lines[line1 + n + 1].strip().split()[:-1]),
                    )
                }

    phases = [a - blk1 + blk2 for a in phases]

    for pn, ll in enumerate(phases):
        if phase is None or phase == "base":
            phase = "base"
        else:
            phase = lines[ll].split()[-1]

        data[phase]['su'] = {}

        line1 = phases[pn]
        line2 = phases[pn + 1] if pn + 1 != len(phases) else blk3

        for n, line in enumerate(lines[line1:line2]):
            if "Cell" in line:
                data[phase]['su']["cell"] = {
                    key: val
                    for (key, val) in zip(
                        ["a", "b", "c", "alpha", "beta", "gamma"],
                        map(float, lines[line1 + n + 1].strip().split()),
                    )
                }
            elif "Gaussian" in line:
                data[phase]['su']["profile_gaussian"] = {
                    key: val
                    for (key, val) in zip(
                        ["U", "V", "W", "P"],
                        map(float, lines[line1 + n + 1].strip().split()),
                    )
                }
            elif "Lorentzian" in line:
                data[phase]['su']["profile_lorentzian"] = {
                    key: val
                    for (key, val) in zip(
                        ["LX", "LXe", "LY", "LYe"],
                        map(float, lines[line1 + n + 1].strip().split()),
                    )
                }

    return data
