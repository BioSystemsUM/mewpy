import os
import time
import warnings

from mewpy.regulation import SRFBAModel

warnings.filterwarnings("ignore")


def sample_network():
    """
    Sample network available in examples using cobra as reader

    :return: sample sr-fba model
    """

    # Sample network

    import cobra.io
    from mewpy.simulation.cobra import Simulation

    DIR = os.path.dirname(os.path.realpath(__file__))
    cbm_model_f = os.path.join(DIR, '../models/regulation/SampleNet.xml')
    reg_model_f = os.path.join(DIR, '../models/regulation/SampleRegNet.csv')

    _BIOMASS_ID = 'r11'

    t0 = time.time()
    model = cobra.io.read_sbml_model(cbm_model_f)
    model.objective = _BIOMASS_ID

    simulation = Simulation(model)
    t1 = time.time()

    print(t1 - t0)

    t0 = time.time()
    srfba = SRFBAModel.from_tabular_format(reg_model_f, model, cbm_simulation_interface=simulation,
                                           sep=',', id_col=0, rule_col=1, header=None)
    t1 = time.time()

    print(t1 - t0)

    # r15
    initial_state = {
        'pH': 7,
        'g21': 1,
        'g22': 0,
        'g23': 1,
        'g24': 1,
        'g25': 1,
        'g26': 1,
        'g27': 1,
        'g28': 1,
        'g29': 1,
        'g30': 0,
        'g31': 0,
        'g32': 0,
        'g33': 1,
        'g36': 1,
    }

    # # not r15
    # initial_state = {
    #     'pH': 7,
    #     'g21': 1,
    #     'g22': 0,
    #     'g23': 1,
    #     'g24': 0,
    #     'g25': 0,
    #     'g26': 0,
    #     'g27': 1,
    #     'g28': 1,
    #     'g29': 1,
    #     'g30': 0,
    #     'g31': 1,
    #     'g32': 0,
    #     'g33': 1,
    #     'g36': 0,
    # }

    srfba.initial_state = initial_state

    t0 = time.time()
    srfba.simulate()
    t1 = time.time()

    print(t1 - t0)

    return srfba


def cobra_ecoli_core_model():
    """

    SRFBA COBRA Ecoli Core Model (subset of the genome-scale metabolic reconstruction iAF1260)

    Available at Orth J, Fleming R, Palsson B. 2010. Reconstruction and Use of Microbial Metabolic Networks:
    the Core Escherichia coli Metabolic Model as an Educational Guide, EcoSal Plus 2010;
    doi:10.1128/ecosalplus.10.2.1

    Ecoli core model from cobra.test
    Regulatory model from http://systemsbiology.ucsd.edu/Downloads/EcoliCore

    :return: srfba model
    """

    import cobra.test
    from mewpy.simulation.cobra import Simulation

    DIR = os.path.dirname(os.path.realpath(__file__))
    reg_model_f = os.path.join(DIR, '../models/regulation/core_TRN_v2.csv')
    aliases_f = os.path.join(DIR, '../models/regulation/core_TRN_srfba_aliases.csv')

    _BIOMASS_ID = 'Biomass_Ecoli_core'
    _O2 = 'EX_o2_e'
    _GLC = 'EX_glc__D_e'
    _FUM = 'EX_fum_e'

    t0 = time.time()
    model = cobra.test.create_test_model("textbook")
    model.objective = _BIOMASS_ID

    envcond = {_GLC: (-10.0, 100000.0), _O2: (-30, 100000.0), _FUM: (-10, 100000.0)}
    simulation = Simulation(model, envcond=envcond)
    t1 = time.time()

    print(t1 - t0)

    t0 = time.time()
    srfba = SRFBAModel.from_tabular_format(reg_model_f, model, cbm_simulation_interface=simulation,
                                           sep=',', id_col=1, rule_col=2, aliases_cols=[0], header=0)
    srfba.update_aliases_from_tabular_format_file(aliases_f, id_col=1, aliases_cols=[0])
    t1 = time.time()

    print(t1 - t0)

    initial_state = {
        'Biomass_Ecoli_core_w_GAM': 1
    }

    srfba.initial_state = initial_state

    t0 = time.time()
    srfba.simulate()
    t1 = time.time()

    print(t1 - t0)

    return srfba


def framed_imc1010_model():
    """

    SRFBA FRAMED Ecoli iMC1010 model from Covert et al. 2004 at https://doi.org/10.1038/nature02456
    This model uses the E. coli metabolic model iJR904 available at https://www.ebi.ac.uk/biomodels/MODEL1507180060
    and published at https://doi.org/10.1186/gb-2003-4-9-r54

    Some rules had to be adjusted though
    iJR904 had to be adjusted, as it didn't match SR_FBA original publication or had errors

    The following reactions were added as in the original publication:
        - h2so: 2 o2_c + h2s_c -> (0, 999999) so4_c + 2 h_c
        - h2st: h2s_e <-> (-999999, 999999) h2s_c
        - h2s_ext: h2s_e -> (0, 999999)
        - 5dglcn_ext: 5dglcn_e -> (0, 999999)
        - btn_ext: btn_e -> (0, 999999)
        - cbi_ext: cbi_e -> (0, 999999)
        - h2o2_ext: h2o2_e -> (0, 999999)
        - ppa_ext: ppa_e -> (0, 999999)
        - thym_ext: thym_e-> (0, 999999)

    The following reactions were removed from iJR904, as they were duplicated or wrong
        - GALU (duplicated GALUi (correct GPR))

    The following reactions were removed from SR-FBA orginal publication model, as they were duplicated or wrong:
        - ptrca (duplicated PTRCTA)
        - indolet (unbalanced and duplicated indolet2r)

    The following indirect mappings were found:

        cbiat, R_CBIAT_DELETE
        cblat, R_CBLAT_DELETE
        d-lact2, R_D_LACt2
        dhptdc, R_DHPTDCs
        l-lacd2, R_L_LACD2
        l-lact2r, R_L_LACt2r
        lcar, R_LCARS
        nh3t, R_NH4t
        l-lacd3, R_L_LACD3
        test_akgdh, R_AKGDH
        test_nadtrhd, R_NADTRHD
        trpas1, CYSDS

    Others:
        - iJR904 has an additional reaction to ptrcta, namely ORNTA


    :return: srfba model
    """

    from reframed.io.sbml import load_cbmodel
    from mewpy.simulation.reframed import Simulation

    DIR = os.path.dirname(os.path.realpath(__file__))
    cbm_model_f = os.path.join(DIR, "../models/iJR904_srfba.xml")
    reg_model_f = os.path.join(DIR, '../models/regulation/imc1010_v6.csv')
    aliases_f = os.path.join(DIR, '../models/regulation/imc1010_srfba_aliases.csv')

    _BIOMASS_ID = 'R_BiomassEcoli'
    _O2 = 'R_EX_o2_e'
    _GLC = 'R_EX_glc_DASH_D_e'
    _CO2 = 'R_EX_co2_e'
    _FE2 = "R_EX_fe2_e"
    _H = "R_EX_h_e"
    _H2O = "R_EX_h2o_e"
    _K = "R_EX_k_e"
    _NA1 = "R_EX_na1_e"
    _NH4 = "R_EX_nh4_e"
    _PI = "R_EX_pi_e"
    _SO4 = "R_EX_so4_e"
    _SUCC = "R_EX_succ_e"

    t0 = time.time()
    model = load_cbmodel(cbm_model_f)
    model.set_objective({_BIOMASS_ID: 1})

    # envcond = {_GLC: (-10.0, 100000.0),
    #            _O2: (-100.0, 100000.0),
    #            _CO2: (-100.0, 100000.0),
    #            _FE2: (-100.0, 100000.0),
    #            _H: (-100.0, 100000.0),
    #            _H2O: (-100.0, 100000.0),
    #            _K: (-100.0, 100000.0),
    #            _NA1: (-100.0, 100000.0),
    #            _NH4: (-100.0, 100000.0),
    #            _PI: (-100.0, 100000.0),
    #            _SO4: (-100.0, 100000.0)}

    envcond = {_GLC: (-10.0, 100000.0),
               _SUCC: (0.0, 100000.0),
               _NH4: (-10.0, 100000.0),
               _O2: (-10.0, 100000.0),
               _CO2: (-15.0, 100000.0),
               _PI: (-15.0, 100000.0),
               _SO4: (-10.0, 100000.0),
               _H: (-10.0, 100000.0),
               _H2O: (-55.0, 100000.0)}

    simulation = Simulation(model, envcond=envcond)
    t1 = time.time()

    print(t1 - t0)

    t0 = time.time()
    srfba = SRFBAModel.from_tabular_format(reg_model_f, model, cbm_simulation_interface=simulation,
                                           sep=';', id_col=1, rule_col=4, aliases_cols=[0, 2, 3], header=0)
    srfba.update_aliases_from_tabular_format_file(aliases_f, sep=';', id_col=0, aliases_cols=[1])
    t1 = time.time()

    print(t1 - t0)

    m_initial_state = {i.id: 1 for i in srfba.metabolic_regulatory_genes_gen()}

    initial_state = {
        'Growth': 1,
        'pH': 7
    }

    initial_state.update(m_initial_state)

    srfba.initial_state = initial_state

    t0 = time.time()
    srfba.simulate()
    t1 = time.time()

    print(t1 - t0)

    return srfba


if __name__ == '__main__':
    srfba_sample_net = sample_network()
    srfba_ecoli_core = cobra_ecoli_core_model()
    srfba_ecoli_imc1010 = framed_imc1010_model()
