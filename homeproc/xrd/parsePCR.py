def readpcr(path):
    """
    Only for multipattern formats.
    """

    with open(path) as file:
        lines = file.readlines()

    # Strip comments
    lines = [line for line in lines if not line.startswith("!")]

    pcr = {}  # main dictionary
    line = 0  # line reference

    ##### start read
    # pcr name
    pcr['name'] = lines[line].strip()
    line = line + 1

    # patterns
    pcr['patterns'] = {}
    patt_1 = lines[line].split()
    npatt = int(patt_1[1])

    pcr['patterns']["npatt"] = npatt

    for n in range(npatt):
        pcr['patterns'][n] = {"is_refined": bool(patt_1[n + 2])}

    line = line + 1

    # pattern weights
    weights = list(map(float, lines[line].split()[1:]))
    for n in range(npatt):
        pcr['patterns'][n]['weight'] = weights[n]

    line = line + 1

    # global flags
    flags = list(map(int, lines[line].split()))
    pcr["phases"] = {"nphases": flags[0]}
    pcr["fl_divergence"] = flags[1]
    pcr["fl_refl_reorder"] = flags[2]
    pcr["fl_single_crystal_job"] = flags[3]
    pcr["fl_optimisations"] = flags[4]
    pcr["fl_automatic_refine"] = flags[5]

    line = line + 1

    # pattern flags
    for n in range(npatt):
        pattflags = {}
        flags = list(map(int, lines[line].split()[0:14]))

        pattflags["jobtype"] = flags[0]
        pattflags["profile_type"] = flags[1]
        pattflags["background_type"] = flags[2]
        pattflags["excluded_regions"] = flags[3]
        pattflags["scatterfactor_userdef"] = flags[4]
        pattflags["preferred_orientation_type"] = flags[5]
        pattflags["refine_weighting_type"] = flags[6]
        pattflags["lorentz_polar_corr"] = flags[7]
        pattflags["resolution_function_type"] = flags[8]
        pattflags["reduction_factor"] = flags[9]
        pattflags["scattering_unit"] = flags[10]
        pattflags["intensity_corr"] = flags[11]
        pattflags["anm"] = flags[12]
        pattflags["int"] = flags[13]

        pcr['patterns'][n] = {"flags": pattflags}

        line = line + 1

    # pattern names
    for n in range(npatt):
        pcr['patterns'][n]["filename"] = lines[line].strip()
        line = line + 1

    # output flags
    flags = list(map(int, lines[line].split()))

    pcr["out_correlation_matrix"] = flags[0]
    pcr["out_update_pcr"] = flags[1]
    pcr["out_nli"] = flags[2]
    pcr["out_sym_file"] = flags[3]
    pcr["out_rpa"] = flags[4]
    pcr["out_reduced_verbose"] = flags[5]

    line = line + 1

    # output pattern flags
    for n in range(npatt):
        pattflags = {}
        flags = list(map(int, lines[line].split()[0:11]))

        pattflags["out_integrated"] = flags[0]
        pattflags["out_ppl"] = flags[1]
        pattflags["out_ioc"] = flags[2]
        pattflags["out_ls1"] = flags[3]
        pattflags["out_ls2"] = flags[4]
        pattflags["out_ls3"] = flags[5]
        pattflags["out_prf"] = flags[6]
        pattflags["out_ins"] = flags[7]
        pattflags["out_hkl"] = flags[8]
        pattflags["out_fou"] = flags[9]
        pattflags["out_ana"] = flags[10]

        pcr['patterns'][n]['output'] = pattflags

        line = line + 1

    # experiment pattern flags
    for n in range(npatt):
        expatt = {}
        flags = list(map(float, lines[line].split()))
        expatt["lmd_1"] = flags[0]
        expatt["lmd_2"] = flags[1]
        expatt["lmd_ratio"] = flags[2]
        expatt["background_start"] = flags[3]
        expatt["prf_cutoff"] = flags[4]
        expatt["monocrh_polarization_corr"] = flags[5]
        expatt["absorp_corr"] = flags[6]
        expatt["asymetry_corr_lim"] = flags[7]
        expatt["polarization_factor"] = flags[8]
        expatt["2nd-muR"] = flags[9]

        pcr['patterns'][n]["flags"].update(expatt)

        line = line + 1

    # refinement flags
    flags = lines[line].split()

    pcr["ref_cycles"] = int(flags[0])
    pcr["ref_convergence"] = float(flags[1])
    pcr["ref_r_atomic"] = float(flags[2])
    pcr["ref_r_anisotropic"] = float(flags[3])
    pcr["ref_r_profile"] = float(flags[4])
    pcr["ref_r_global"] = float(flags[5])

    line = line + 1

    # refinement pattern
    for n in range(npatt):
        refpatt = {}
        flags = list(map(float, lines[line].split()))
        refpatt["theta_min"] = flags[0]
        refpatt["steo"] = flags[1]
        refpatt["theta_max"] = flags[2]
        refpatt["incident_angle"] = flags[3]
        refpatt["max_beam_angle"] = flags[4]

        pcr['patterns'][n]["flags"].update(refpatt)

        line = line + 1

    # excluded regions
    for n in range(npatt):
        excluded = pcr['patterns'][n]["flags"]['excluded_regions']
        if excluded != 0:
            ranges = []
            for _ in range(excluded):
                ranges.append(tuple(map(float, lines[line].split())))
                line = line + 1

            pcr['patterns'][n]["excluded"] = ranges
        else:
            line = line + 1

    # refined parameters
    nrefined = int(lines[line].split()[0])
    line = line + 1

    # data setup per pattern type
    for n in range(npatt):

        # powder data setup
        scattering_unit = pcr['patterns'][n]["flags"]['scattering_unit']
        if scattering_unit == 0:
            flags = list(map(float, lines[line].split()))
            expatt["zero_point"] = flags[0]
            expatt["zero_point_code"] = flags[1]
            expatt["systematic_shift_cos"] = flags[2]
            expatt["systematic_shift_cos_code"] = flags[3]
            expatt["systematic_shift_sin"] = flags[4]
            expatt["systematic_shift_sin_code"] = flags[5]
            expatt["wavelength"] = flags[6]
            expatt["wavelength_code"] = flags[7]

            more = bool(flags[8])
            if more:
                # microadsorption (not implemented)
                line = line + 1

            pcr['patterns'][n]["flags"].update(expatt)

        elif scattering_unit == 1:
            raise NotImplementedError

        elif scattering_unit == 2:
            raise NotImplementedError

        line = line + 1

        # background coefficients
        background_type = pcr['patterns'][n]["flags"]['background_type']
        if background_type == 0:
            pcr['patterns'][n]['background_poly'] = list(map(float, lines[line].split()))
            line = line + 1
            pcr['patterns'][n]['background_code'] = list(map(float, lines[line].split()))
        else:
            raise NotImplementedError

        line = line + 1

    # start phase reading
    nphases = pcr["phases"]["nphases"]

    for ph in range(nphases):
        phase = {}
        # read name
        phase["name"] = lines[line].strip()
        line = line + 1

        # read codes
        phcodes = lines[line].split()
        phase["natoms"] = int(phcodes[0])
        phase["n_constraints_distance"] = int(phcodes[1])
        phase["n_constraints_angle"] = int(phcodes[2])  # TODO can be n_constraints_magmoment
        phase["job_type"] = int(phcodes[3])
        phase["symmetry_reading_mode"] = int(phcodes[4])
        phase["size_strain_mode"] = int(phcodes[5])
        phase["n_usedef_parameters"] = int(phcodes[6])
        phase["weight_coeff"] = float(phcodes[7])
        phase["n_propagation_vectors"] = int(phcodes[8])
        line = line + 1

        more = int(phcodes[9])
        if more:
            raise NotImplementedError

        # read contribution
        contributes = list(map(bool, lines[line].split()))
        phase["pattern"] = {}
        for n in range(npatt):
            phase["pattern"][n] = {'contributes': contributes[n]}
        line = line + 1

        # specific pattern parameters
        if any(contributes):
            for n in range(npatt):
                params_1 = list(map(int, lines[line].split()))
                line = line + 1
                params_2 = list(map(float, lines[line].split()))
                line = line + 1

                phase["pattern"][n]["reflexions"] = params_1[0]
                phase["pattern"][n]["profile_type"] = params_1[1]
                phase["pattern"][n]["job_type"] = params_1[2]
                phase["pattern"][n]["Nsp_Ref"] = params_1[3]
                phase["pattern"][n]["Ph_Shift"] = params_1[4]

                phase["pattern"][n]["preferred_orientation_d1"] = params_2[0]
                phase["pattern"][n]["preferred_orientation_d2"] = params_2[1]
                phase["pattern"][n]["preferred_orientation_d3"] = params_2[2]
                phase["pattern"][n]["brindley_coeff"] = params_2[3]
                phase["pattern"][n]["reflx_int_data_weight"] = params_2[4]
                phase["pattern"][n]["reflx_int_exclusion"] = params_2[5]
                phase["pattern"][n]["reflx_chi2_weight"] = params_2[6]

        else:
            line = line + 1

        # spacegroup
        phase["spacegroup"] = lines[line][0:21].strip()
        line = line + 1

        # atoms
        natoms = phase["natoms"]
        atoms = {}
        for n in range(natoms):
            atom_flags = lines[line].split()
            line = line + 1
            atom_codes = lines[line].split()
            line = line + 1

            atoms[n] = {}
            atoms[n]["label"] = atom_flags[0]
            atoms[n]["type"] = atom_flags[1]
            atoms[n]["x"] = float(atom_flags[2])
            atoms[n]["y"] = float(atom_flags[3])
            atoms[n]["z"] = float(atom_flags[4])
            atoms[n]["biso"] = float(atom_flags[5])
            atoms[n]["occ"] = float(atom_flags[6])
            atoms[n]["symmetry_subs_in"] = int(atom_flags[7])
            atoms[n]["symmetry_subs_fin"] = int(atom_flags[8])
            atoms[n]["isotropic_type"] = int(atom_flags[9])
            atoms[n]["specie"] = int(atom_flags[10])

            atoms[n]["x_code"] = atom_codes[0]
            atoms[n]["y_code"] = atom_codes[1]
            atoms[n]["z_code"] = atom_codes[2]
            atoms[n]["biso_code"] = atom_codes[3]
            atoms[n]["occ_code"] = atom_codes[4]

        phase["atoms"] = atoms

        # profile parameters
        for n in range(npatt):
            profile_1 = lines[line].split()
            line = line + 1
            profile_1_codes = list(map(float, lines[line].split()))
            line = line + 1
            profile_2 = list(map(float, lines[line].split()))
            line = line + 1
            profile_2_codes = list(map(float, lines[line].split()))
            line = line + 1

            phase['pattern'][n]['scale'] = float(profile_1[0])
            phase['pattern'][n]['shape'] = float(profile_1[1])
            phase['pattern'][n]['biso_overall'] = float(profile_1[2])
            phase['pattern'][n]['strain_param1'] = float(profile_1[3])
            phase['pattern'][n]['strain_param2'] = float(profile_1[4])
            phase['pattern'][n]['strain_param3'] = float(profile_1[5])
            phase['pattern'][n]['strain_model'] = int(profile_1[6])

            phase['pattern'][n]['halfwidth_U'] = profile_2[0]
            phase['pattern'][n]['halfwidth_V'] = profile_2[1]
            phase['pattern'][n]['halfwidth_W'] = profile_2[2]
            phase['pattern'][n]['lorrenzian_strain_X'] = profile_2[3]
            phase['pattern'][n]['lorrenzian_strain_Y'] = profile_2[4]
            phase['pattern'][n]['gaussian_particle_size'] = profile_2[5]
            phase['pattern'][n]['lorenzian_particle_size'] = profile_2[6]

            cell = list(map(float, lines[line].split()))
            line = line + 1
            cell_codes = list(map(float, lines[line].split()))
            line = line + 1
            phase["cell"] = {}
            phase['cell']['a'] = cell[0]
            phase['cell']['b'] = cell[1]
            phase['cell']['c'] = cell[2]
            phase['cell']['alpha'] = cell[3]
            phase['cell']['beta'] = cell[4]
            phase['cell']['gamma'] = cell[5]

            phase['pattern'][n]['halfwidth_U'] = profile_2[0]
            phase['pattern'][n]['halfwidth_V'] = profile_2[1]
            phase['pattern'][n]['halfwidth_W'] = profile_2[2]
            phase['pattern'][n]['lorrenzian_strain_X'] = profile_2[3]
            phase['pattern'][n]['lorrenzian_strain_Y'] = profile_2[4]
            phase['pattern'][n]['gaussian_particle_size'] = profile_2[5]
            phase['pattern'][n]['lorenzian_particle_size'] = profile_2[6]

            orientation = list(map(float, lines[line].split()))
            line = line + 1
            orientation_codes = list(map(float, lines[line].split()))
            line = line + 1
            phase['pattern'][n]['orientation_param1'] = profile_2[0]
            phase['pattern'][n]['orientation_param2'] = profile_2[1]
            phase['pattern'][n]['assymetry_param1'] = profile_2[2]
            phase['pattern'][n]['assymetry_param2'] = profile_2[3]
            phase['pattern'][n]['assymetry_param3'] = profile_2[4]
            phase['pattern'][n]['assymetry_param4'] = profile_2[5]

            pcr["phases"][ph] = phase

    # pattern to plot
    pcr["plot_pattern"] = list(map(float, lines[line].split()))

    return pcr
