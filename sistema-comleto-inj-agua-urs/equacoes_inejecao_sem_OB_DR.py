# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 08:00:10 2026

@author: dmnev
"""

# ============================================================
# Equacionamento do Sistema de Injeção
# ============================================================
def equacoes_injecao():
    equacoes = {
        # ============================================================
        # 1. Captação de Água do Mar
        # ============================================================
        # ------------------------------------------------------------
        # 1.1 Eletrocloradora (9 eq.)
        # ------------------------------------------------------------
        "Eq1":  ["F_7_in_AM", "F_7_in_BB_ABC"],
        "Eq2":  ["F_7_in_BB_ABC", "F_7_out_BB_ABC"],
        "Eq3":  ["F_7_out_BB_ABC", "F_7_out_BB_ABC_MIS_1"],
        "Eq4":  ["F_7_out_BB_ABC_MIS_1", "F_7_in_SR", "F_7_in_EC"],
        "Eq5":  ["F_7_in_SR", "F_7_out_SR_DR"],
        "Eq6":  ["F_7_in_EC", "F_7_in_EC_1", "F_7_in_EC_2"],
        "Eq7":  ["F_7_in_EC_1", "F_7_out_EC_1"],
        "Eq8":  ["F_7_in_EC_2", "F_7_out_EC_2"],
        "Eq9":  ["F_7_in_TQ_HC_EC", "F_7_out_EC_1", "F_7_out_EC_2"],

        # ------------------------------------------------------------
        # 1.2 Tanque de Hipoclorito (2 eq.)
        # ------------------------------------------------------------
        "Eq10": ["F_7_in_B_ABC", "F_7_in_TQ_HC_EC", "F_7_in_TQ_HC_B_ABC"],
        "Eq11": ["F_7_in_B_ABC", "F_7_in_TQ_HC_B_ABC", "F_7_in_INJ_B_ABC"],

        # ------------------------------------------------------------
        # 1.3 Captação e Injeção de Hipoclorito (11 eq.)
        # ------------------------------------------------------------
        "Eq12": ["F_7_in_CAP_INJ_HC1", "F_7_in_BC_A_HC1"],
        "Eq13": ["F_7_out_BC_A", "F_7_in_BC_A_HC1", "F_7_in_BC_A_AM"],
        "Eq14": ["F_7_in_CAP_INJ_HC2", "F_7_in_BC_B_HC2"],
        "Eq15": ["F_7_out_BC_B", "F_7_in_BC_B_HC2", "F_7_in_BC_B_AM"],
        "Eq16": ["F_7_in_CAP_INJ_HC3", "F_7_in_BC_C_HC3"],
        "Eq17": ["F_7_out_BC_C", "F_7_in_BC_C_HC3", "F_7_in_BC_C_AM"],
        "Eq18": ["F_7_in_CAP_INJ_HC4", "F_7_in_BC_D_HC4"],
        "Eq19": ["F_7_out_BC_D", "F_7_in_BC_D_HC4", "F_7_in_BC_D_AM"],
        "Eq20": ["F_7_in_CAP_INJ_HC5", "F_7_in_BC_E_HC5"],
        "Eq21": ["F_7_out_BC_E", "F_7_in_BC_E_HC5", "F_7_in_BC_E_AM"],
        "Eq22": ["F_7_out_BC_A", "F_7_out_BC_B", "F_7_out_BC_C",
                 "F_7_out_BC_D", "F_6_in_F_ABCD_BC_ABCD"],

        # ============================================================
        # 2. Distribuição de Água
        # ============================================================
        "Eq23": ["F_5_in_DAM", "F_6_out_TC_DAM_LAV", "F_6_out_F_ABCDE_DAM"],
        "Eq24": ["F_5_in_DAM", "F_5_in_FG_DAM", "F_8_in_DES_SK_DAM", "F_5_out_DAM_UTI"],

        # ------------------------------------------------------------
        # 2.1 Filtros - Distribuição (6 eq.)
        # ------------------------------------------------------------
        "Eq25": ["F_6_in_F_ABCD_BC_ABCD", "F_6_in_F_E_BC_E",
                 "F_6_in_TC_F_ABCD", "F_6_in_ANC_F_ABCDE",
                 "F_6_out_F_ABCD_DAM", "F_6_out_F_ABCD_VAC_1",
                 "F_6_out_F_ABCD_VAC_2"],
        "Eq26": ["F_6_in_F_A", "F_6_out_F_A"],
        "Eq27": ["F_6_in_F_B", "F_6_out_F_B"],
        "Eq28": ["F_6_in_F_C", "F_6_out_F_C"],
        "Eq29": ["F_6_in_F_D", "F_6_out_F_D"],
        "Eq30": ["F_6_in_F_E", "F_6_out_F_E"],

        # ------------------------------------------------------------
        # 2.2 Trocadores de Calor (6 eq.)
        # ------------------------------------------------------------
        "Eq31": ["F_6_in_TC_F_ABCD", "F_6_in_TC_INT_INJ_BB", "F_6_in_TC_AC",
                 "F_6_out_TC_DAR", "F_6_in_AC_TC", "F_6_out_TC_DAM_LAV",
                 "F_8_in_INT_INJ_B_TC"],
        "Eq32": ["F_6_in_TC_A1", "F_6_in_TC_A2", "F_6_out_TC_A"],
        "Eq33": ["F_6_in_TC_B1", "F_6_in_TC_B2", "F_6_out_TC_B"],
        "Eq34": ["F_6_in_TC_C1", "F_6_in_TC_C2", "F_6_out_TC_C"],
        "Eq35": ["F_6_in_TC_D1", "F_6_in_TC_D2", "F_6_out_TC_D"],
        "Eq36": ["F_6_in_TC_E1", "F_6_in_TC_E2", "F_6_out_TC_E"],

        # ------------------------------------------------------------
        # 2.3 Água de Refrigeração - AC (9 eq.)
        # ------------------------------------------------------------
        "Eq37": ["F_6_in_AC_DAR_1", "F_6_in_AC_DAR_2", "F_6_in_AC_TC",
                 "F_6_in_AC_AF_MK", "F_6_in_AC_GI",
                 "F_6_in_TC_AC", "F_6_out_AC_UTI",
                 "F_6_out_AC_SL_1", "F_6_out_AC_SL_2"],
        "Eq38": ["F_6_in_B_A1", "F_6_out_B_A1"],
        "Eq39": ["F_6_in_B_B1", "F_6_out_B_B1"],
        "Eq40": ["F_6_in_B_C1", "F_6_out_B_C1"],
        "Eq41": ["F_6_in_B_A2", "F_6_out_B_A2"],
        "Eq42": ["F_6_in_B_B2", "F_6_out_B_B2"],
        "Eq43": ["F_6_in_F", "F_6_out_F"],
        "Eq44": ["F_6_in_VE1_1", "F_6_in_VE1_2", "F_6_in_VE1_3",
                 "F_6_in_SL_1", "F_6_in_SL_2", "F_6_out_VE1"],
        "Eq45": ["F_6_in_VE2", "F_6_out_VE2_1", "F_6_out_VE2_2"],

        # ------------------------------------------------------------
        # 2.4 Água de Refrigeração - ANC (8 eq.)
        # ------------------------------------------------------------
        "Eq46": ["F_6_in_ANC_F_ABCDE", "F_6_in_ANC_B_AQ", "F_6_in_ANC_DAR",
                 "F_6_in_TC_ANC", "F_6_out_ANC_DAR", "F_6_out_ANC_B_AQ"],
        "Eq47": ["F_6_in_B_A", "F_6_out_B_A"],
        "Eq48": ["F_6_in_B_B", "F_6_out_B_B"],
        "Eq49": ["F_6_in_B_C", "F_6_out_B_C"],
        "Eq50": ["F_6_in_TC_A1", "F_6_in_TC_A2", "F_6_out_TC_A1", "F_6_out_TC_A2"],
        "Eq51": ["F_6_in_TC_B1", "F_6_in_TC_B2", "F_6_out_TC_B1", "F_6_out_TC_B2"],
        "Eq52": ["F_6_in_VE", "F_6_out_VE"],
        "Eq53": ["F_6_in_TQ", "F_6_out_TQ_1", "F_6_out_TQ_2"],

        # ============================================================
        # 3. Tratamento de Água
        # ============================================================
        # ------------------------------------------------------------
        # 3.1 Filtros Grossos (5 eq.)
        # ------------------------------------------------------------
        "Eq54": ["F_1_in_FG_DAM", "F_1_in_FG_BI_SK1", "F_1_in_FF_FG"],
        "Eq55": ["F_1_in_FG_A", "F_1_out_FG_A"],
        "Eq56": ["F_1_in_FG_B", "F_1_out_FG_B"],
        "Eq57": ["F_1_in_FG_C", "F_1_out_FG_C"],
        "Eq58": ["F_1_in_FF_FG", "F_1_out_FG_A", "F_1_out_FG_B", "F_1_out_FG_C"],

        # ------------------------------------------------------------
        # 3.2 Filtros Finos (5 eq.)
        # ------------------------------------------------------------
        "Eq59": ["F_1_in_FF_FG", "F_1_in_FF_BI_SK1", "F_1_in_FF_NaHSO3_SK3",
                 "F_1_in_FF_AI_SK2", "F_1_out_FF_AF", "F_1_in_BB_FF"],
        "Eq60": ["F_1_in_FF_A", "F_1_out_FF_A"],
        "Eq61": ["F_1_in_FF_B", "F_1_out_FF_B"],
        "Eq62": ["F_1_in_FF_C", "F_1_out_FF_C"],
        "Eq63": ["F_1_in_BB_FF", "F_1_out_FF_A", "F_1_out_FF_B", "F_1_out_FF_C"],

        # ------------------------------------------------------------
        # 3.3 Bomba Booster (5 eq.)
        # ------------------------------------------------------------
        "Eq64": ["F_1_in_BB_FF", "FA", "FB", "FC", "FD", "FE", "F_1_in_URS_BP_BB"],
        "Eq65": ["F_1_out_BB_URS", "F_1_in_URS_BP_BB"],
        "Eq66": ["F_1_in_BB_FF", "F_1_in_BB_A", "F_1_in_BB_B"],
        "Eq67": ["F_1_in_BB_A", "F_1_out_BB_A"],
        "Eq68": ["F_1_in_BB_B", "F_1_out_BB_B"],

        # ============================================================
        # 3.4 Sistema de Membranas da URS
        # ============================================================
        # ------------------------------------------------------------
        # Reconciliação (20 eq.)
        # ------------------------------------------------------------
        "Eq69": ["F", "R", "P"],
        "Eq70": ["P", "PA", "PB", "PC", "PD", "PE"],
        "Eq71": ["PA", "Pa_A", "Pb_A", "Pc_A"],
        "Eq72": ["PB", "Pa_B", "Pb_B", "Pc_B"],
        "Eq73": ["PC", "Pa_C", "Pb_C", "Pc_C"],
        "Eq74": ["PD", "Pa_D", "Pb_D", "Pc_D"],
        "Eq75": ["PE", "Pa_E", "Pb_E", "Pc_E"],
        "Eq76": ["R", "Rc_A", "Rc_B", "Rc_C", "Rc_D", "Rc_E"],
        "Eq77": ["F", "FA", "FB", "FC", "FD", "FE"],
        "Eq78": ["FA", "Ra_A", "Pa_A", "Rb_A", "Pb_A"],
        "Eq79": ["FB", "Ra_B", "Pa_B", "Rb_B", "Pb_B"],
        "Eq80": ["FC", "Ra_C", "Pa_C", "Rb_C", "Pb_C"],
        "Eq81": ["FD", "Ra_D", "Pa_D", "Rb_D", "Pb_D"],
        "Eq82": ["FE", "Ra_E", "Pa_E", "Rb_E", "Pb_E"],
        "Eq83": ["Rb_A", "Rc_A", "Pc_A", "Ra_A"],
        "Eq84": ["Rb_B", "Rc_B", "Pc_B", "Ra_B"],
        "Eq85": ["Rb_C", "Rc_C", "Pc_C", "Ra_C"],
        "Eq86": ["Rb_D", "Rc_D", "Pc_D", "Ra_D"],
        "Eq87": ["Rb_E", "Rc_E", "Pc_E", "Ra_E"],
        "Eq88": ["F_8_in_DES_URS", "P", "F_1_in_URS_BP_BB"],

        # ------------------------------------------------------------
        # Monitoramento por estágios (30 eq.)
        # ------------------------------------------------------------
        # Equivalências:
        #   PT_RF -> PT_1R = PT_2F = PT_cF
        #   PT_R -> PT_cR = PT_2R
        #   PT_P -> PT_2P = PT_cP
        #   PDI_c2 -> PDI_c = PDI_2

        # S_1
        "Eq89":  ["S_1_A", "Pa_A", "Pb_A", "A", "PT_RF_A", "PT_1P_A", "Dpi"],
        "Eq90":  ["S_1_B", "Pa_B", "Pb_B", "A", "PT_RF_B", "PT_1P_B", "Dpi"],
        "Eq91":  ["S_1_C", "Pa_C", "Pb_C", "A", "PT_RF_C", "PT_1P_C", "Dpi"],
        "Eq92":  ["S_1_D", "Pa_D", "Pb_D", "A", "PT_RF_D", "PT_1P_D", "Dpi"],
        "Eq93":  ["S_1_E", "Pa_E", "Pb_E", "A", "PT_RF_E", "PT_1P_E", "Dpi"],

        # S_2
        "Eq94":  ["S_2_A", "Pc_A", "A", "PT_R_A", "PT_P_A", "Dpi"],
        "Eq95":  ["S_2_B", "Pc_B", "A", "PT_R_B", "PT_P_B", "Dpi"],
        "Eq96":  ["S_2_C", "Pc_C", "A", "PT_R_C", "PT_P_C", "Dpi"],
        "Eq97":  ["S_2_D", "Pc_D", "A", "PT_R_D", "PT_P_D", "Dpi"],
        "Eq98":  ["S_2_E", "Pc_E", "A", "PT_R_E", "PT_P_E", "Dpi"],

        # IDF_1
        "Eq99":  ["IDF_1_A", "Lp", "PT_RF_A", "PT_1P_A", "Dpi", "Pa_A", "Pb_A", "A"],
        "Eq100": ["IDF_1_B", "Lp", "PT_RF_B", "PT_1P_B", "Dpi", "Pa_B", "Pb_B", "A"],
        "Eq101": ["IDF_1_C", "Lp", "PT_RF_C", "PT_1P_C", "Dpi", "Pa_C", "Pb_C", "A"],
        "Eq102": ["IDF_1_D", "Lp", "PT_RF_D", "PT_1P_D", "Dpi", "Pa_D", "Pb_D", "A"],
        "Eq103": ["IDF_1_E", "Lp", "PT_RF_E", "PT_1P_E", "Dpi", "Pa_E", "Pb_E", "A"],

        # IDF_2
        "Eq104": ["IDF_2_A", "Lp", "PT_R_A", "PT_P_A", "Dpi", "Pc_A", "A"],
        "Eq105": ["IDF_2_B", "Lp", "PT_R_B", "PT_P_B", "Dpi", "Pc_B", "A"],
        "Eq106": ["IDF_2_C", "Lp", "PT_R_C", "PT_P_C", "Dpi", "Pc_C", "A"],
        "Eq107": ["IDF_2_D", "Lp", "PT_R_D", "PT_P_D", "Dpi", "Pc_D", "A"],
        "Eq108": ["IDF_2_E", "Lp", "PT_R_E", "PT_P_E", "Dpi", "Pc_E", "A"],

        # PDI_1
        "Eq109": ["PDI_1_A", "PT_1F_A", "PT_RF_A"],
        "Eq110": ["PDI_1_B", "PT_1F_B", "PT_RF_B"],
        "Eq111": ["PDI_1_C", "PT_1F_C", "PT_RF_C"],
        "Eq112": ["PDI_1_D", "PT_1F_D", "PT_RF_D"],
        "Eq113": ["PDI_1_E", "PT_1F_E", "PT_RF_E"],

        # PDI_c2
        "Eq114": ["PDI_c2_A", "PT_RF_A", "PT_R_A"],
        "Eq115": ["PDI_c2_B", "PT_RF_B", "PT_R_B"],
        "Eq116": ["PDI_c2_C", "PT_RF_C", "PT_R_C"],
        "Eq117": ["PDI_c2_D", "PT_RF_D", "PT_R_D"],
        "Eq118": ["PDI_c2_E", "PT_RF_E", "PT_R_E"],

        # ------------------------------------------------------------
        # Monitoramento por bancos (45 eq.)
        # ------------------------------------------------------------

        # S_a
        "Eq119": ["S_a_A", "Pa_A", "A", "PT_aR_A", "PT_aP_A", "Dpi"],
        "Eq120": ["S_a_B", "Pa_B", "A", "PT_aR_B", "PT_aP_B", "Dpi"],
        "Eq121": ["S_a_C", "Pa_C", "A", "PT_aR_C", "PT_aP_C", "Dpi"],
        "Eq122": ["S_a_D", "Pa_D", "A", "PT_aR_D", "PT_aP_D", "Dpi"],
        "Eq123": ["S_a_E", "Pa_E", "A", "PT_aR_E", "PT_aP_E", "Dpi"],

        # S_b
        "Eq124": ["S_b_A", "Pb_A", "A", "PT_bR_A", "PT_bP_A", "Dpi"],
        "Eq125": ["S_b_B", "Pb_B", "A", "PT_bR_B", "PT_bP_B", "Dpi"],
        "Eq126": ["S_b_C", "Pb_C", "A", "PT_bR_C", "PT_bP_C", "Dpi"],
        "Eq127": ["S_b_D", "Pb_D", "A", "PT_bR_D", "PT_bP_D", "Dpi"],
        "Eq128": ["S_b_E", "Pb_E", "A", "PT_bR_E", "PT_bP_E", "Dpi"],

        # S_c
        "Eq129": ["S_c_A", "Pc_A", "A", "PT_R_A", "PT_P_A", "Dpi"],
        "Eq130": ["S_c_B", "Pc_B", "A", "PT_R_B", "PT_P_B", "Dpi"],
        "Eq131": ["S_c_C", "Pc_C", "A", "PT_R_C", "PT_P_C", "Dpi"],
        "Eq132": ["S_c_D", "Pc_D", "A", "PT_R_D", "PT_P_D", "Dpi"],
        "Eq133": ["S_c_E", "Pc_E", "A", "PT_R_E", "PT_P_E", "Dpi"],

        # IDF_a
        "Eq134": ["IDF_a_A", "Lp", "PT_aR_A", "PT_aP_A", "Dpi", "Pa_A", "A"],
        "Eq135": ["IDF_a_B", "Lp", "PT_aR_B", "PT_aP_B", "Dpi", "Pa_B", "A"],
        "Eq136": ["IDF_a_C", "Lp", "PT_aR_C", "PT_aP_C", "Dpi", "Pa_C", "A"],
        "Eq137": ["IDF_a_D", "Lp", "PT_aR_D", "PT_aP_D", "Dpi", "Pa_D", "A"],
        "Eq138": ["IDF_a_E", "Lp", "PT_aR_E", "PT_aP_E", "Dpi", "Pa_E", "A"],

        # IDF_b
        "Eq139": ["IDF_b_A", "Lp", "PT_bR_A", "PT_bP_A", "Dpi", "Pb_A", "A"],
        "Eq140": ["IDF_b_B", "Lp", "PT_bR_B", "PT_bP_B", "Dpi", "Pb_B", "A"],
        "Eq141": ["IDF_b_C", "Lp", "PT_bR_C", "PT_bP_C", "Dpi", "Pb_C", "A"],
        "Eq142": ["IDF_b_D", "Lp", "PT_bR_D", "PT_bP_D", "Dpi", "Pb_D", "A"],
        "Eq143": ["IDF_b_E", "Lp", "PT_bR_E", "PT_bP_E", "Dpi", "Pb_E", "A"],

        # IDF_c
        "Eq144": ["IDF_c_A", "Lp", "PT_R_A", "PT_P_A", "Dpi", "Pc_A", "A"],
        "Eq145": ["IDF_c_B", "Lp", "PT_R_B", "PT_P_B", "Dpi", "Pc_B", "A"],
        "Eq146": ["IDF_c_C", "Lp", "PT_R_C", "PT_P_C", "Dpi", "Pc_C", "A"],
        "Eq147": ["IDF_c_D", "Lp", "PT_R_D", "PT_P_D", "Dpi", "Pc_D", "A"],
        "Eq148": ["IDF_c_E", "Lp", "PT_R_E", "PT_P_E", "Dpi", "Pc_E", "A"],

        # PDI_a
        "Eq149": ["PDI_a_A", "PT_aF_A", "PT_aR_A"],
        "Eq150": ["PDI_a_B", "PT_aF_B", "PT_aR_B"],
        "Eq151": ["PDI_a_C", "PT_aF_C", "PT_aR_C"],
        "Eq152": ["PDI_a_D", "PT_aF_D", "PT_aR_D"],
        "Eq153": ["PDI_a_E", "PT_aF_E", "PT_aR_E"],

        # PDI_b
        "Eq154": ["PDI_b_A", "PT_bF_A", "PT_bR_A"],
        "Eq155": ["PDI_b_B", "PT_bF_B", "PT_bR_B"],
        "Eq156": ["PDI_b_C", "PT_bF_C", "PT_bR_C"],
        "Eq157": ["PDI_b_D", "PT_bF_D", "PT_bR_D"],
        "Eq158": ["PDI_b_E", "PT_bF_E", "PT_bR_E"],

        # PDI_c2
        "Eq159": ["PDI_c2_A", "PT_RF_A", "PT_R_A"],
        "Eq160": ["PDI_c2_B", "PT_RF_B", "PT_R_B"],
        "Eq161": ["PDI_c2_C", "PT_RF_C", "PT_R_C"],
        "Eq162": ["PDI_c2_D", "PT_RF_D", "PT_R_D"],
        "Eq163": ["PDI_c2_E", "PT_RF_E", "PT_R_E"],

        # ============================================================
        # 3.5 Injeção de Biocida (4 eq.)
        # ============================================================
        "Eq164": ["F_1_in_TQ_1_TOT_BI", "F_1_in_FG_BI_SK1", "F_1_in_FF_BI_SK1"],
        "Eq165": ["F_1_in_TQ_1", "F_1_in_SK1"],
        "Eq166": ["F_1_in_SK1", "F_1_in_FG_BI_SK1", "F_1_in_FF_BI_SK1"],
        "Eq167": ["F_1_out_SK1", "F_1_in_FG_BI_SK1", "F_1_in_FF_BI_SK1"],

        # ============================================================
        # 3.6 Injeção de Anti-incrustante (3 eq.)
        # ============================================================
        "Eq168": ["F_3_in_TQ_2_TOT_AI", "F_1_in_FF_AI_SK2"],
        "Eq169": ["F_3_in_TQ_2", "F_3_in_SK2"],
        "Eq170": ["F_3_in_SK2", "F_1_in_FF_AI_SK2"],

        # ============================================================
        # 3.7 Injeção de Bissulfito de Sódio (4 eq.)
        # ============================================================
        "Eq171": ["F_3_in_TQ_3_TOT_NaHSO3", "F_1_in_FF_NaHSO3_SK3", "F_4_in_LIM_NaHSO3_SK3"],
        "Eq172": ["F_3_in_TQ_3", "F_3_in_SK3"],
        "Eq173": ["F_3_in_SK3", "F_1_in_FF_NaHSO3_SK3", "F_4_in_LIM_NaHSO3_SK3"],
        "Eq174": ["F_3_out_SK3", "F_1_in_FF_NaHSO3_SK3", "F_4_in_LIM_NaHSO3_SK3"],

        # ============================================================
        # 3.8 Sistema de Limpeza (14 eq.)
        # ============================================================
        "Eq175": ["F_4_in_LIM_AD", "F_4_in_LIM_NaHSO3_SK3",
                  "F_4_in_MIS_1", "F_4_in_MIS_2"],
        "Eq176": ["F_4_in_RLQ_TABCDE", "F_4_in_RLQ_AFDO",
                  "F_4_in_MIS_3", "F_4_in_MIS_4"],
        "Eq177": ["F_4_in_TQ_A_AL", "F_4_in_TQ_A_AC", "F_4_in_MIS_1", "F_4_in_MIS_3",
                  "F_4_out_TQ_A"],
        "Eq178": ["F_4_in_TQ_B_AL", "F_4_in_TQ_B_AC", "F_4_in_MIS_2", "F_4_in_MIS_4",
                  "F_4_in_TQ_B_B_ABC", "F_4_out_TQ_B"],
        "Eq179": ["F_4_out_TQ_A", "F_4_out_TQ_B",
                  "F_4_in_B_A", "F_4_in_B_B", "F_4_in_B_C"],
        "Eq180": ["F_4_in_B_A", "F_4_out_B_A"],
        "Eq181": ["F_4_in_B_B", "F_4_out_B_B"],
        "Eq182": ["F_4_in_B_C", "F_4_out_B_C"],
        "Eq183": ["F_4_out_B_A", "F_4_out_B_B", "F_4_out_B_C",
                  "F_4_in_TQ_B_B_ABC", "F_4_in_F_3"],
        "Eq184": ["F_4_in_F_3", "F_4_out_F_3"],
        "Eq185": ["F_4_out_F_3", "F_4_in_LQ_TABCDE_FT3",
                  "F_4_in_LQDO_TA_FT3", "F_4_in_LQDO_TB_FT3"],
        "Eq186": ["F_4_in_LINHAAF", "F_4_out_AF_UTI", "F_4_in_ANC_AF",
                  "F_4_in_UTI_AQ_AF", "F_4_in_AF_MK_AF"],
        "Eq187": ["F_4_in_AF_MK_AF", "F_4_out_AF_MK_B_AQ",
                  "F_6_in_AC_AF_MK"],
        "Eq188": ["F_4_in_LINHAAD", "F_4_in_SO",
                  "F_4_out_AD_UTI", "F_4_in_LIM_AD"],

        # ============================================================
        # 4.1 Desaeração a Vácuo (5 eq.)
        # ============================================================
        "Eq189": ["F_8_in_DES_URS", "F_8_in_DES_BI",
                  "F_8_in_DES_URS_BI", "F_8_in_INJ_URS_BI"],
        "Eq190": ["F_8_out_DES_G", "F_8_out_DES_G1",
                  "F_8_out_DES_G2", "F_8_out_VENT"],
        "Eq191": ["F_8_in_DES_URS_BI", "F_8_in_DES_INJ", "F_8_in_DES_SE",
                  "F_8_out_DES_1", "F_8_out_DES_2", "F_8_out_DES_G"],
        "Eq192": ["F_8_in_INJ_DES",
                  "F_8_out_DES_1", "F_8_in_INJ_URS_BI",
                  "F_8_in_INJ_BI", "F_8_in_INJ_SE", "F_8_in_INJ_BD"],
        "Eq193": ["F_8_out_SK_FF_OB", "F_8_in_SK_G_1", "F_8_in_SK_G_2",
                  "F_8_in_DES_SK_DAM", "F_8_in_SK_AR"],

        # ============================================================
        # 4.2 Bombeamento de Água de Injeção (10 eq.)
        # ============================================================
        "Eq194": ["F_8_in_INJ_BB_DES", "F_8_in_BB_A", "F_8_in_BB_B", "F_8_in_BB_C"],
        "Eq195": ["F_8_in_BB_A", "F_8_out_BB_A"],
        "Eq196": ["F_8_in_BB_B", "F_8_out_BB_B"],
        "Eq197": ["F_8_in_BB_C", "F_8_out_BB_C"],
        "Eq198": ["F_8_out_BB_A", "F_8_out_BB_B", "F_8_out_BB_C",
                  "F_6_in_TC_INT_INJ_BB", "F_8_out_BB_URS"],
        "Eq199": ["F_8_in_INT_INJ_B_TC", "F_8_in_B_A_TC", "F_8_in_B_B_TC"],
        "Eq200": ["F_8_in_B_A_TC", "F_8_in_B_A_DAR",
                  "F_8_out_B_A", "F_8_out_B_A_ANC"],
        "Eq201": ["F_8_in_B_B_TC", "F_8_in_B_B_DAR",
                  "F_8_out_B_B", "F_8_out_B_B_ANC"],
        "Eq202": ["F_8_out_B_AB", "F_8_out_B_A", "F_8_out_B_B"],
        "Eq203": ["F_8_out_B_AB", "F_8_in_AI_IJN", "F_8_in_ADO_INJ"],
    }

    # ============================================================
    # VARIÁVEIS DO SISTEMA
    # ============================================================
    variaveis = sorted({v for eq in equacoes.values() for v in eq})

    # ============================================================
    # SENSORES INSTALADOS
    # (variáveis com \textcolor{corMedida} no LaTeX)
    # ============================================================
    sensores_instalados = [
        # --- Vazões medidas (globais) ---
        "F_7_out_BB_ABC",
        "F_7_out_SR_DR",
        "F_7_in_INJ_B_ABC",
        "F_1_in_FF_AI_SK2",
        "F_1_out_BB_URS",
        "F_1_out_SK1",
        "F_3_out_SK3",
        "F_4_in_F_3",
        "F_4_out_F_3",
        "F_8_in_DES_URS_BI",
        "F_8_in_B_A_TC",
        "F_8_in_B_B_TC",
        "F_8_out_B_AB",

        # --- Parâmetros globais de permeabilidade ---
        "A", "Lp", "Dpi",

        # --- Vazões de reciclo/purga (URS) ---
        "R",
        "Pa_A", "Pb_A", "Pc_A",
        "Pa_B", "Pb_B", "Pc_B",
        "Pa_C", "Pb_C", "Pc_C",
        "Pa_D", "Pb_D", "Pc_D",
        "Pa_E", "Pb_E", "Pc_E",
        "Ra_A", "Ra_B", "Ra_C", "Ra_D", "Ra_E",
        "Rc_A", "Rc_B", "Rc_C", "Rc_D", "Rc_E",

        # --- Pressões medidas (URS - por trem) ---
        # Trem A
        "PT_1F_A", "PT_RF_A", "PT_R_A",
        # Trem B
        "PT_1F_B", "PT_RF_B", "PT_R_B",
        # Trem C
        "PT_1F_C", "PT_RF_C", "PT_R_C",
        # Trem D
        "PT_1F_D", "PT_RF_D", "PT_R_D",
        # Trem E
        "PT_1F_E", "PT_RF_E", "PT_R_E",

        # --- PDIs medidos (por trem) ---
        "PDI_1_A", "PDI_1_B", "PDI_1_C", "PDI_1_D", "PDI_1_E",
        "PDI_c2_A", "PDI_c2_B", "PDI_c2_C", "PDI_c2_D", "PDI_c2_E",
    ]

    # ============================================================
    # VARIÁVEIS CALCULADAS
    # ============================================================
    variaveis_calculadas = [
        # --- Utilidades ---
        "F_4_out_AD_UTI",
        "F_4_out_AF_UTI",
        "F_5_out_DAM_UTI",
        "F_6_out_AC_UTI",

        # --- URS - KPIs por estágio (por trem) ---
        "S_1_A", "S_1_B", "S_1_C", "S_1_D", "S_1_E",
        "S_2_A", "S_2_B", "S_2_C", "S_2_D", "S_2_E",
        "IDF_1_A", "IDF_1_B", "IDF_1_C", "IDF_1_D", "IDF_1_E",
        "IDF_2_A", "IDF_2_B", "IDF_2_C", "IDF_2_D", "IDF_2_E",

        # --- URS - KPIs por banco (por trem) ---
        "S_a_A", "S_a_B", "S_a_C", "S_a_D", "S_a_E",
        "S_b_A", "S_b_B", "S_b_C", "S_b_D", "S_b_E",
        "S_c_A", "S_c_B", "S_c_C", "S_c_D", "S_c_E",
        "IDF_a_A", "IDF_a_B", "IDF_a_C", "IDF_a_D", "IDF_a_E",
        "IDF_b_A", "IDF_b_B", "IDF_b_C", "IDF_b_D", "IDF_b_E",
        "IDF_c_A", "IDF_c_B", "IDF_c_C", "IDF_c_D", "IDF_c_E",
        "PDI_a_A", "PDI_a_B", "PDI_a_C", "PDI_a_D", "PDI_a_E",
        "PDI_b_A", "PDI_b_B", "PDI_b_C", "PDI_b_D", "PDI_b_E",
    ]

    # ============================================================
    # PESOS
    # ============================================================
    pesos = {v: 1.0 for v in variaveis}

    return equacoes, variaveis, pesos, sensores_instalados, variaveis_calculadas