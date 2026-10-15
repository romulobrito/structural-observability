# -*- coding: utf-8 -*-
"""
Created on Wed Oct  7 11:10:36 2026

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
        # ============================================================
        # 1.1 Eletrocloradora (10 eq.)
        # ============================================================
        "Eq1":  ["F_7_in_AM", "F_7_in_BB_ABC", "F_7_out_AM_DR"],
        "Eq2":  ["F_7_in_BB_ABC", "F_7_out_BB_ABC"],
        "Eq3":  ["F_7_out_BB_ABC", "F_7_out_BB_ABC_DR", "F_7_out_BB_ABC_MIS_1"],
        "Eq4":  ["F_7_out_BB_ABC_MIS_1", "F_7_in_SR", "F_7_in_EC"],
        "Eq5":  ["F_7_in_EC", "F_7_in_EC_1", "F_7_in_EC_2"],
        "Eq6":  ["F_7_in_EC_1", "F_7_out_EC_1", "F_7_out_EC_1_DR"],
        "Eq7":  ["F_7_in_EC_2", "F_7_out_EC_2", "F_7_out_EC_2_DR"],
        "Eq8":  ["F_7_in_TQ_HC_EC", "F_7_out_EC_1", "F_7_out_EC_2"],
        "Eq9":  ["F_7_out_EC_1_DR", "F_7_out_EC_2_DR", "F_7_out_EC_12_DR"],
        "Eq10": ["F_7_out_AM_DR", "F_7_out_BB_ABC_DR", "F_7_out_EC_12_DR",
                 "F_7_out_SR_DR", "F_7_EC_DR"],

        # ============================================================
        # 1.2 Tanque de Hipoclorito (3 eq.)
        # ============================================================
        "Eq11": ["F_7_in_B_ABC", "F_7_out_TQ_HC_DR",
                 "F_7_in_TQ_HC_EC", "F_7_in_TQ_HC_B_ABC"],
        "Eq12": ["F_7_in_B_ABC", "F_7_in_TQ_HC_B_ABC",
                 "F_7_in_INJ_B_ABC", "F_7_out_B_ABC_DR"],
        "Eq13": ["F_7_out_HC_DR", "F_7_out_TQ_HC_DR", "F_7_out_B_ABC_DR"],

        # ============================================================
        # 1.3 Captação e Injeção de Hipoclorito (13 eq.)
        # ============================================================
        "Eq14": ["F_7_in_CAP_INJ_HC1", "F_7_in_BC_A_HC1", "F_7_out_INJ_HC1_DR"],
        "Eq15": ["F_7_out_BC_A", "F_7_in_BC_A_HC1", "F_7_in_BC_A_AM"],
        "Eq16": ["F_7_in_CAP_INJ_HC2", "F_7_in_BC_B_HC2", "F_7_out_INJ_HC2_DR"],
        "Eq17": ["F_7_out_BC_B", "F_7_in_BC_B_HC2", "F_7_in_BC_B_AM"],
        "Eq18": ["F_7_in_CAP_INJ_HC3", "F_7_in_BC_C_HC3", "F_7_out_INJ_HC3_DR"],
        "Eq19": ["F_7_out_BC_C", "F_7_in_BC_C_HC3", "F_7_in_BC_C_AM"],
        "Eq20": ["F_7_in_CAP_INJ_HC4", "F_7_in_BC_D_HC4", "F_7_out_INJ_HC4_DR"],
        "Eq21": ["F_7_out_BC_D", "F_7_in_BC_D_HC4", "F_7_in_BC_D_AM"],
        "Eq22": ["F_7_in_CAP_INJ_HC5", "F_7_in_BC_E_HC5", "F_7_out_INJ_HC5_DR"],
        "Eq23": ["F_7_out_BC_E", "F_7_in_BC_E_HC5", "F_7_in_BC_E_AM"],
        "Eq24": ["F_7_out_BC_A", "F_7_out_BC_B", "F_7_out_BC_C",
                 "F_7_out_BC_D", "F_6_in_F_ABCD_BC_ABCD"],
        "Eq25": ["F_7_out_INJ_HC_DR", "F_7_out_INJ_HC1_DR", "F_7_out_INJ_HC2_DR",
                 "F_7_out_INJ_HC3_DR", "F_7_out_INJ_HC4_DR", "F_7_out_INJ_HC5_DR"],
        "Eq26": ["F_7_out_INJ_TC_DR", "F_7_out_INJ_HC_DR", "F_6_out_F_ABCDE_BC_OB"],

        # ============================================================
        # 2 Distribuição de Água (2 eq.)
        # ============================================================
        "Eq27": ["F_5_in_DAM", "F_6_out_TC_DAM_LAV", "F_6_out_F_ABCDE_DAM"],
        "Eq28": ["F_5_in_DAM", "F_5_in_FG_DAM", "F_8_in_DES_SK_DAM", "F_5_out_DAM_UTI"],

        # ============================================================
        # 2.1 Filtros - Distribuição (6 eq.)
        # ============================================================
        "Eq29": ["F_6_in_F_ABCD_BC_ABCD", "F_6_in_F_E_BC_E",
                 "F_6_in_TC_F_ABCD", "F_6_out_F_ABCD_DAM",
                 "F_6_out_F_ABCD_VAC_1", "F_6_out_F_ABCD_VAC_2",
                 "F_6_in_ANC_F_ABCDE", "F_6_out_F_ABCDE_BC_OB",
                 "F_6_out_F_ABCDE_FG_OB", "F_6_out_F_ABCDE_FG_OD"],
        "Eq30": ["F_6_in_F_A", "F_6_out_F_A", "F_6_out_F_A_OD"],
        "Eq31": ["F_6_in_F_B", "F_6_out_F_B", "F_6_out_F_B_OD"],
        "Eq32": ["F_6_in_F_C", "F_6_out_F_C", "F_6_out_F_C_OD"],
        "Eq33": ["F_6_in_F_D", "F_6_out_F_D", "F_6_out_F_D_OD"],
        "Eq34": ["F_6_in_F_E", "F_6_out_F_E", "F_6_out_F_E_OD"],

        # ============================================================
        # 2.2 Trocadores de Calor (6 eq.)
        # ============================================================
        "Eq35": ["F_6_in_TC_F_ABCD", "F_6_in_TC_INT_INJ_BB", "F_6_in_TC_AC",
                 "F_6_out_TC_DAR", "F_6_in_AC_TC", "F_6_out_TC_DAM_LAV",
                 "F_8_in_INT_INJ_B_TC", "F_6_out_TC_OB1", "F_6_out_TC_OB2",
                 "F_6_out_TC_AC_OB"],
        "Eq36": ["F_6_in_TC_A1", "F_6_in_TC_A2",
                 "F_6_out_TC_A", "F_6_out_TC_A_OB"],
        "Eq37": ["F_6_in_TC_B1", "F_6_in_TC_B2",
                 "F_6_out_TC_B", "F_6_out_TC_B_OB"],
        "Eq38": ["F_6_in_TC_C1", "F_6_in_TC_C2",
                 "F_6_out_TC_C", "F_6_out_TC_C_OB"],
        "Eq39": ["F_6_in_TC_D1", "F_6_in_TC_D2",
                 "F_6_out_TC_D", "F_6_out_TC_D_OB"],
        "Eq40": ["F_6_in_TC_E1", "F_6_in_TC_E2",
                 "F_6_out_TC_E", "F_6_out_TC_E_OB"],

        # ============================================================
        # 2.3 Água de Refrigeração - AC (9 eq.)
        # ============================================================
        "Eq41": ["F_6_in_AC_DAR_1", "F_6_in_AC_DAR_2", "F_6_in_AC_TC",
                 "F_6_in_AC_AF_MK", "F_6_in_AC_GI",
                 "F_6_in_TC_AC", "F_6_out_AC_UTI", "F_6_out_AC_ANC_OD1",
                 "F_6_out_AC_TC_OB", "F_6_out_AC_ANC_OD2",
                 "F_6_out_AC_SL_1", "F_6_out_AC_SL_2", "F_6_out_AC_VE_OB",
                 "F_6_out_AC_B_AB_OB", "F_6_out_AC_F_OB"],
        "Eq42": ["F_6_in_B_A1", "F_6_out_B_A1", "F_6_out_B_A1_OD"],
        "Eq43": ["F_6_in_B_B1", "F_6_out_B_B1", "F_6_out_B_B1_OD"],
        "Eq44": ["F_6_in_B_C1", "F_6_out_B_C1", "F_6_out_B_C1_OD"],
        "Eq45": ["F_6_in_B_A2", "F_6_out_B_A2", "F_6_out_B_A2_OD", "F_6_out_B_A2_OB"],
        "Eq46": ["F_6_in_B_B2", "F_6_out_B_B2", "F_6_out_B_B2_OD", "F_6_out_B_B2_OB"],
        "Eq47": ["F_6_in_F", "F_6_out_F", "F_6_out_F_OB"],
        "Eq48": ["F_6_in_VE1_1", "F_6_in_VE1_2", "F_6_in_VE1_3",
                 "F_6_in_SL_1", "F_6_in_SL_2",
                 "F_6_out_VE1", "F_6_out_VE1_OB"],
        "Eq49": ["F_6_in_VE2", "F_6_out_VE2_1", "F_6_out_VE2_2"],

        # ============================================================
        # 2.4 Água de Refrigeração - ANC (8 eq.)
        # ============================================================
        "Eq50": ["F_6_in_ANC_F_ABCDE", "F_6_in_ANC_B_AQ", "F_6_in_ANC_DAR",
                 "F_6_in_TC_ANC", "F_6_out_ANC_AC_OB",
                 "F_6_out_ANC_DAR", "F_6_out_ANC_B_AQ"],
        "Eq51": ["F_6_in_B_A", "F_6_out_B_A", "F_6_out_B_A_OD_OB"],
        "Eq52": ["F_6_in_B_B", "F_6_out_B_B", "F_6_out_B_B_OD_OB"],
        "Eq53": ["F_6_in_B_C", "F_6_out_B_C", "F_6_out_B_C_OD_OB"],
        "Eq54": ["F_6_in_TC_A1", "F_6_in_TC_A2", "F_6_out_TC_A1",
                 "F_6_out_TC_A2", "F_6_out_TC_A_OD_OB"],
        "Eq55": ["F_6_in_TC_B1", "F_6_in_TC_B2", "F_6_out_TC_B1",
                 "F_6_out_TC_B2", "F_6_out_TC_B_OD_OB"],
        "Eq56": ["F_6_in_VE", "F_6_out_VE", "F_6_out_VE_OD_OB"],
        "Eq57": ["F_6_in_TQ", "F_6_out_TQ_1", "F_6_out_TQ_2"],

        # ============================================================
        # 3 Tratamento de Água
        # ============================================================
        # ============================================================
        # 3.1 Filtros Grossos (5 eq.)
        # ============================================================
        "Eq58": ["F_1_in_FG_DAM", "F_1_in_FG_BI_SK1", "F_1_in_FF_FG",
                 "F_1_out_FG_ABC_OD", "F_1_out_FG_ABC_OB"],
        "Eq59": ["F_1_in_FG_A", "F_1_out_FG_A", "F_1_out_FG_A_OB", "F_1_out_FG_A_OD"],
        "Eq60": ["F_1_in_FG_B", "F_1_out_FG_B", "F_1_out_FG_B_OB", "F_1_out_FG_B_OD"],
        "Eq61": ["F_1_in_FG_C", "F_1_out_FG_C", "F_1_out_FG_C_OB", "F_1_out_FG_C_OD"],
        "Eq62": ["F_1_in_FF_FG", "F_1_out_FG_A", "F_1_out_FG_B", "F_1_out_FG_C"],

        # ============================================================
        # 3.2 Filtros Finos (5 eq.)
        # ============================================================
        "Eq63": ["F_1_in_FF_FG", "F_1_in_FF_BI_SK1", "F_1_in_FF_NaHSO3_SK3",
                 "F_1_in_FF_AI_SK2", "F_1_out_FF_AF", "F_1_in_BB_FF",
                 "F_1_out_FF_ABC_OB", "F_1_out_FF_ABC_OD"],
        "Eq64": ["F_1_in_FF_A", "F_1_out_FF_A", "F_1_out_FF_A_OB", "F_1_out_FF_A_OD"],
        "Eq65": ["F_1_in_FF_B", "F_1_out_FF_B", "F_1_out_FF_B_OB", "F_1_out_FF_B_OD"],
        "Eq66": ["F_1_in_FF_C", "F_1_out_FF_C", "F_1_out_FF_C_OB", "F_1_out_FF_C_OD"],
        "Eq67": ["F_1_in_BB_FF", "F_1_out_FF_A", "F_1_out_FF_B", "F_1_out_FF_C"],

        # ============================================================
        # 3.3 Bomba Booster (5 eq.)
        # ============================================================
        "Eq68": ["F_1_in_BB_FF", "FA", "FB", "FC", "FD", "FE",
                 "F_1_in_URS_BP_BB", "F_1_in_TA_OB", "F_1_in_FF_OD"],
        "Eq69": ["F_1_out_BB_URS", "F_1_in_URS_BP_BB", "F_1_in_TA_OB"],
        "Eq70": ["F_1_in_BB_FF", "F_1_in_BB_A", "F_1_in_BB_B"],
        "Eq71": ["F_1_in_BB_A", "F_1_out_BB_A", "F_1_out_BB_A_OD"],
        "Eq72": ["F_1_in_BB_B", "F_1_out_BB_B", "F_1_out_BB_B_OD"],

        # ============================================================
        # 3.4 Sistema de Membranas da URS
        # ============================================================
        # ------------------------------------------------------------
        # Reconciliação (20 eq.)
        # ------------------------------------------------------------
        "Eq73": ["F", "R", "P"],                          # F = R + P
        "Eq74": ["P", "PA", "PB", "PC", "PD", "PE"],      # P = PA + PB + PC + PD + PE
        "Eq75": ["PA", "Pa_A", "Pb_A", "Pc_A"],           # PA = Pa,A + Pb,A + Pc,A
        "Eq76": ["PB", "Pa_B", "Pb_B", "Pc_B"],           # PB = Pa,B + Pb,B + Pc,B
        "Eq77": ["PC", "Pa_C", "Pb_C", "Pc_C"],           # PC = Pa,C + Pb,C + Pc,C
        "Eq78": ["PD", "Pa_D", "Pb_D", "Pc_D"],           # PD = Pa,D + Pb,D + Pc,D
        "Eq79": ["PE", "Pa_E", "Pb_E", "Pc_E"],           # PE = Pa,E + Pb,E + Pc,E

        "Eq80": ["R", "Rc_A", "Rc_B", "Rc_C", "Rc_D", "Rc_E"],  # R = Rc,A + Rc,B + Rc,C + Rc,D + Rc,E
        "Eq81": ["F", "FA", "FB", "FC", "FD", "FE"],            # F = FA + FB + FC + FD + FE

        "Eq82": ["FA", "Ra_A", "Pa_A", "Rb_A", "Pb_A"],        # FA = Ra,A + Pa,A + Rb,A + Pb,A
        "Eq83": ["FB", "Ra_B", "Pa_B", "Rb_B", "Pb_B"],        # FB = Ra,B + Pa,B + Rb,B + Pb,B
        "Eq84": ["FC", "Ra_C", "Pa_C", "Rb_C", "Pb_C"],        # FC = Ra,C + Pa,C + Rb,C + Pb,C
        "Eq85": ["FD", "Ra_D", "Pa_D", "Rb_D", "Pb_D"],        # FD = Ra,D + Pa,D + Rb,D + Pb,D
        "Eq86": ["FE", "Ra_E", "Pa_E", "Rb_E", "Pb_E"],        # FE = Ra,E + Pa,E + Rb,E + Pb,E

        "Eq87": ["Rb_A", "Rc_A", "Pc_A", "Ra_A"],      # Rb,A =  Fc,A - Ra,A = Rc,A + Pc,A − Ra,A
        "Eq88": ["Rb_B", "Rc_B", "Pc_B", "Ra_B"],      # Rb,B =  Fc,B - Ra,B = Rc,B + Pc,B − Ra,B
        "Eq89": ["Rb_C", "Rc_C", "Pc_C", "Ra_C"],      # Rb,C =  Fc,C - Ra,C = Rc,C + Pc,C − Ra,C
        "Eq90": ["Rb_D", "Rc_D", "Pc_D", "Ra_D"],      # Rb,D =  Fc,D - Ra,D = Rc,D + Pc,D − Ra,D
        "Eq91": ["Rb_E", "Rc_E", "Pc_E", "Ra_E"],      # Rb,E =  Fc,E - Ra,E = Rc,E + Pc,E − Ra,E
        "Eq92": ["F_8_in_DES_URS", "P", "F_1_in_URS_BP_BB"], # F_{8,in,DES,URS} = P + F_{1,in,URS_BP,BB}

        # ------------------------------------------------------------
        # Monitoramento por estágios (30 eq.)
        # ------------------------------------------------------------
        # Algumas variáveis representam o MESMO PONTO FÍSICO, mas
        # recebem nomes diferentes em cada contexto (estágio / banco).
        #
        # Adota-se um NOME CANÔNICO ÚNICO para cada ponto, de forma a
        # evitar redundância no sistema de equações:
        #
        #   PT_RF -> PT_1R = PT_2F = PT_cF
        #   PT_R -> PT_cR = PT_2R
        #   PDI_c2 -> PDI_c = PDI_2
        #   PT_P -> PT_2P = PT_cP
        #   Pa_X, Pb_X, Pc_X -> vazões de permeado dos bancos a, b, c

        # --- S_1: Permeabilidade do Estágio 1 (por trem) ---
        "Eq93":  ["S_1_A", "Pa_A", "Pb_A", "A", "PT_RF_A", "PT_1P_A", "Dpi"],
        "Eq94":  ["S_1_B", "Pa_B", "Pb_B", "A", "PT_RF_B", "PT_1P_B", "Dpi"],
        "Eq95":  ["S_1_C", "Pa_C", "Pb_C", "A", "PT_RF_C", "PT_1P_C", "Dpi"],
        "Eq96":  ["S_1_D", "Pa_D", "Pb_D", "A", "PT_RF_D", "PT_1P_D", "Dpi"],
        "Eq97":  ["S_1_E", "Pa_E", "Pb_E", "A", "PT_RF_E", "PT_1P_E", "Dpi"],

        # --- S_2: Permeabilidade do Estágio 2 (por trem) ---
        "Eq98":  ["S_2_A", "Pc_A", "A", "PT_R_A", "PT_P_A", "Dpi"],
        "Eq99":  ["S_2_B", "Pc_B", "A", "PT_R_B", "PT_P_B", "Dpi"],
        "Eq100": ["S_2_C", "Pc_C", "A", "PT_R_C", "PT_P_C", "Dpi"],
        "Eq101": ["S_2_D", "Pc_D", "A", "PT_R_D", "PT_P_D", "Dpi"],
        "Eq102": ["S_2_E", "Pc_E", "A", "PT_R_E", "PT_P_E", "Dpi"],

        # --- IDF_1: Índice de Fouling do Estágio 1 (por trem) ---
        "Eq103": ["IDF_1_A", "Lp", "PT_RF_A", "PT_1P_A", "Dpi", "Pa_A", "Pb_A", "A"],
        "Eq104": ["IDF_1_B", "Lp", "PT_RF_B", "PT_1P_B", "Dpi", "Pa_B", "Pb_B", "A"],
        "Eq105": ["IDF_1_C", "Lp", "PT_RF_C", "PT_1P_C", "Dpi", "Pa_C", "Pb_C", "A"],
        "Eq106": ["IDF_1_D", "Lp", "PT_RF_D", "PT_1P_D", "Dpi", "Pa_D", "Pb_D", "A"],
        "Eq107": ["IDF_1_E", "Lp", "PT_RF_E", "PT_1P_E", "Dpi", "Pa_E", "Pb_E", "A"],

        # --- IDF_2: Índice de Fouling do Estágio 2 (por trem) ---
        "Eq108": ["IDF_2_A", "Lp", "PT_R_A", "PT_P_A", "Dpi", "Pc_A", "A"],
        "Eq109": ["IDF_2_B", "Lp", "PT_R_B", "PT_P_B", "Dpi", "Pc_B", "A"],
        "Eq110": ["IDF_2_C", "Lp", "PT_R_C", "PT_P_C", "Dpi", "Pc_C", "A"],
        "Eq111": ["IDF_2_D", "Lp", "PT_R_D", "PT_P_D", "Dpi", "Pc_D", "A"],
        "Eq112": ["IDF_2_E", "Lp", "PT_R_E", "PT_P_E", "Dpi", "Pc_E", "A"],

        # --- PDI_1: Diferencial de Pressão do Estágio 1 (por trem) ---
        "Eq113": ["PDI_1_A", "PT_1F_A", "PT_RF_A"],
        "Eq114": ["PDI_1_B", "PT_1F_B", "PT_RF_B"],
        "Eq115": ["PDI_1_C", "PT_1F_C", "PT_RF_C"],
        "Eq116": ["PDI_1_D", "PT_1F_D", "PT_RF_D"],
        "Eq117": ["PDI_1_E", "PT_1F_E", "PT_RF_E"],

        # --- PDI_c2: Diferencial de Pressão do Estágio 2 (por trem) ---
        "Eq118": ["PDI_c2_A", "PT_RF_A", "PT_R_A"],
        "Eq119": ["PDI_c2_B", "PT_RF_B", "PT_R_B"],
        "Eq120": ["PDI_c2_C", "PT_RF_C", "PT_R_C"],
        "Eq121": ["PDI_c2_D", "PT_RF_D", "PT_R_D"],
        "Eq122": ["PDI_c2_E", "PT_RF_E", "PT_R_E"],

        # ------------------------------------------------------------
        # Monitoramento por bancos (45 eq.)
        # ------------------------------------------------------------

        # --- S_a: Permeabilidade do banco a (por trem) ---
        "Eq123": ["S_a_A", "Pa_A", "A", "PT_aR_A", "PT_aP_A", "Dpi"],
        "Eq124": ["S_a_B", "Pa_B", "A", "PT_aR_B", "PT_aP_B", "Dpi"],
        "Eq125": ["S_a_C", "Pa_C", "A", "PT_aR_C", "PT_aP_C", "Dpi"],
        "Eq126": ["S_a_D", "Pa_D", "A", "PT_aR_D", "PT_aP_D", "Dpi"],
        "Eq127": ["S_a_E", "Pa_E", "A", "PT_aR_E", "PT_aP_E", "Dpi"],

        # --- S_b: Permeabilidade do banco b (por trem) ---
        "Eq128": ["S_b_A", "Pb_A", "A", "PT_bR_A", "PT_bP_A", "Dpi"],
        "Eq129": ["S_b_B", "Pb_B", "A", "PT_bR_B", "PT_bP_B", "Dpi"],
        "Eq130": ["S_b_C", "Pb_C", "A", "PT_bR_C", "PT_bP_C", "Dpi"],
        "Eq131": ["S_b_D", "Pb_D", "A", "PT_bR_D", "PT_bP_D", "Dpi"],
        "Eq132": ["S_b_E", "Pb_E", "A", "PT_bR_E", "PT_bP_E", "Dpi"],

        # --- S_c: Permeabilidade do banco c (por trem) ---
        "Eq133": ["S_c_A", "Pc_A", "A", "PT_R_A", "PT_P_A", "Dpi"],
        "Eq134": ["S_c_B", "Pc_B", "A", "PT_R_B", "PT_P_B", "Dpi"],
        "Eq135": ["S_c_C", "Pc_C", "A", "PT_R_C", "PT_P_C", "Dpi"],
        "Eq136": ["S_c_D", "Pc_D", "A", "PT_R_D", "PT_P_D", "Dpi"],
        "Eq137": ["S_c_E", "Pc_E", "A", "PT_R_E", "PT_P_E", "Dpi"],

        # --- IDF_a: Índice de Fouling do banco a (por trem) ---
        "Eq138": ["IDF_a_A", "Lp", "PT_aR_A", "PT_aP_A", "Dpi", "Pa_A", "A"],
        "Eq139": ["IDF_a_B", "Lp", "PT_aR_B", "PT_aP_B", "Dpi", "Pa_B", "A"],
        "Eq140": ["IDF_a_C", "Lp", "PT_aR_C", "PT_aP_C", "Dpi", "Pa_C", "A"],
        "Eq141": ["IDF_a_D", "Lp", "PT_aR_D", "PT_aP_D", "Dpi", "Pa_D", "A"],
        "Eq142": ["IDF_a_E", "Lp", "PT_aR_E", "PT_aP_E", "Dpi", "Pa_E", "A"],

        # --- IDF_b: Índice de Fouling do banco b (por trem) ---
        "Eq143": ["IDF_b_A", "Lp", "PT_bR_A", "PT_bP_A", "Dpi", "Pb_A", "A"],
        "Eq144": ["IDF_b_B", "Lp", "PT_bR_B", "PT_bP_B", "Dpi", "Pb_B", "A"],
        "Eq145": ["IDF_b_C", "Lp", "PT_bR_C", "PT_bP_C", "Dpi", "Pb_C", "A"],
        "Eq146": ["IDF_b_D", "Lp", "PT_bR_D", "PT_bP_D", "Dpi", "Pb_D", "A"],
        "Eq147": ["IDF_b_E", "Lp", "PT_bR_E", "PT_bP_E", "Dpi", "Pb_E", "A"],

        # --- IDF_c: Índice de Fouling do banco c (por trem) ---
        "Eq148": ["IDF_c_A", "Lp", "PT_R_A", "PT_P_A", "Dpi", "Pc_A", "A"],
        "Eq149": ["IDF_c_B", "Lp", "PT_R_B", "PT_P_B", "Dpi", "Pc_B", "A"],
        "Eq150": ["IDF_c_C", "Lp", "PT_R_C", "PT_P_C", "Dpi", "Pc_C", "A"],
        "Eq151": ["IDF_c_D", "Lp", "PT_R_D", "PT_P_D", "Dpi", "Pc_D", "A"],
        "Eq152": ["IDF_c_E", "Lp", "PT_R_E", "PT_P_E", "Dpi", "Pc_E", "A"],

        # --- PDI_a: Diferencial de Pressão do banco a (por trem) ---
        "Eq153": ["PDI_a_A", "PT_aF_A", "PT_aR_A"],
        "Eq154": ["PDI_a_B", "PT_aF_B", "PT_aR_B"],
        "Eq155": ["PDI_a_C", "PT_aF_C", "PT_aR_C"],
        "Eq156": ["PDI_a_D", "PT_aF_D", "PT_aR_D"],
        "Eq157": ["PDI_a_E", "PT_aF_E", "PT_aR_E"],

        # --- PDI_b: Diferencial de Pressão do banco b (por trem) ---
        "Eq158": ["PDI_b_A", "PT_bF_A", "PT_bR_A"],
        "Eq159": ["PDI_b_B", "PT_bF_B", "PT_bR_B"],
        "Eq160": ["PDI_b_C", "PT_bF_C", "PT_bR_C"],
        "Eq161": ["PDI_b_D", "PT_bF_D", "PT_bR_D"],
        "Eq162": ["PDI_b_E", "PT_bF_E", "PT_bR_E"],

        # --- PDI_c2: Diferencial de Pressão do banco c (por trem) ---
        "Eq163": ["PDI_c2_A", "PT_RF_A", "PT_R_A"],
        "Eq164": ["PDI_c2_B", "PT_RF_B", "PT_R_B"],
        "Eq165": ["PDI_c2_C", "PT_RF_C", "PT_R_C"],
        "Eq166": ["PDI_c2_D", "PT_RF_D", "PT_R_D"],
        "Eq167": ["PDI_c2_E", "PT_RF_E", "PT_R_E"],
        

        # ============================================================
        # 3.5 Injeção de Biocida (4 eq.)
        # ============================================================
        "Eq168": ["F_1_in_TQ_1_TOT_BI", "F_1_in_FG_BI_SK1", "F_1_in_FF_BI_SK1",
                  "F_1_out_TQ_1_LIM_OD", "F_1_out_SK1_LIM_OD"],
        "Eq169": ["F_1_in_TQ_1", "F_1_out_TQ_1_LIM_OD", "F_1_in_SK1"],
        "Eq170": ["F_1_in_SK1", "F_1_in_FG_BI_SK1", "F_1_in_FF_BI_SK1",
                  "F_1_out_SK1_LIM_OD"],
        "Eq171": ["F_1_out_SK1", "F_1_in_FG_BI_SK1", "F_1_in_FF_BI_SK1"],

        # ============================================================
        # 3.6 Injeção de Anti-incrustante (3 eq.)
        # ============================================================
        "Eq172": ["F_3_in_TQ_2_TOT_AI", "F_1_in_FF_AI_SK2",
                  "F_3_out_TQ_2_LIM_OD", "F_3_out_SK2_LIM_OD"],
        "Eq173": ["F_3_in_TQ_2", "F_3_out_TQ_2_LIM_OD", "F_3_in_SK2"],
        "Eq174": ["F_3_in_SK2", "F_1_in_FF_AI_SK2", "F_3_out_SK2_LIM_OD"],

        # ============================================================
        # 3.7 Injeção de Bissulfito de Sódio (4 eq.)
        # ============================================================
        "Eq175": ["F_3_in_TQ_3_TOT_NaHSO3", "F_1_in_FF_NaHSO3_SK3",
                  "F_4_in_LIM_NaHSO3_SK3", "F_3_out_TQ_3_LIM_OD",
                  "F_3_out_SK3_LIM_OD"],
        "Eq176": ["F_3_in_TQ_3", "F_3_out_TQ_3_LIM_OD", "F_3_in_SK3"],
        "Eq177": ["F_3_in_SK3", "F_1_in_FF_NaHSO3_SK3",
                  "F_4_in_LIM_NaHSO3_SK3", "F_3_out_SK3_LIM_OD"],
        "Eq178": ["F_3_out_SK3", "F_1_in_FF_NaHSO3_SK3", "F_4_in_LIM_NaHSO3_SK3"],

        # ============================================================
        # 3.8 Sistema de Limpeza (14 eq.)
        # ============================================================
        "Eq179": ["F_4_in_LIM_AD", "F_4_in_LIM_NaHSO3_SK3",
                  "F_4_in_MIS_1", "F_4_in_MIS_2"],
        "Eq180": ["F_4_in_RLQ_TABCDE", "F_4_in_RLQ_AFDO",
                  "F_4_in_MIS_3", "F_4_in_MIS_4"],
        "Eq181": ["F_4_in_TQ_A_AL", "F_4_in_TQ_A_AC", "F_4_in_MIS_1", "F_4_in_MIS_3",
                  "F_4_out_TQ_A", "F_4_out_TQ_A_MIS_OD"],
        "Eq182": ["F_4_in_TQ_B_AL", "F_4_in_TQ_B_AC", "F_4_in_MIS_2", "F_4_in_MIS_4",
                  "F_4_in_TQ_B_B_ABC", "F_4_out_TQ_B", "F_4_out_TQ_B_MIS_OD"],
        "Eq183": ["F_4_out_TQ_A", "F_4_out_TQ_B",
                  "F_4_in_B_A", "F_4_in_B_B", "F_4_in_B_C"],
        "Eq184": ["F_4_in_B_A", "F_4_out_B_A"],
        "Eq185": ["F_4_in_B_B", "F_4_out_B_B"],
        "Eq186": ["F_4_in_B_C", "F_4_out_B_C"],
        "Eq187": ["F_4_out_B_A", "F_4_out_B_B", "F_4_out_B_C",
                  "F_4_in_TQ_B_B_ABC", "F_4_in_F_3"],
        "Eq188": ["F_4_in_F_3", "F_4_out_F_3", "F_4_out_F_3_ADO_OB"],
        "Eq189": ["F_4_out_F_3", "F_4_in_LQ_TABCDE_FT3",
                  "F_4_in_LQDO_TA_FT3", "F_4_in_LQDO_TB_FT3"],
        "Eq190": ["F_4_in_LINHAAF", "F_4_out_AF_UTI", "F_4_in_ANC_AF",
                  "F_4_in_UTI_AQ_AF", "F_4_in_AF_MK_AF"],
        "Eq191": ["F_4_in_AF_MK_AF", "F_4_out_AF_MK_B_AQ",
                  "F_6_in_AC_AF_MK", "F_4_out_AF_MK_OB"],
        "Eq192": ["F_4_in_LINHAAD", "F_4_in_SO",
                  "F_4_out_AD_UTI", "F_4_in_LIM_AD"],

        # ============================================================
        # 4.1 Desaeração a Vácuo (5 eq.)
        # ============================================================
        "Eq193": ["F_8_in_DES_URS", "F_8_in_DES_BI",
                  "F_8_in_DES_URS_BI", "F_8_in_INJ_URS_BI"],
        "Eq194": ["F_8_out_DES_G", "F_8_out_DES_G1",
                  "F_8_out_DES_G2", "F_8_out_VENT"],
        "Eq195": ["F_8_in_DES_URS_BI", "F_8_in_DES_INJ", "F_8_in_DES_SE",
                  "F_8_out_DES_1", "F_8_out_DES_2", "F_8_out_DES_G"],
        "Eq196": ["F_8_in_INJ_DES", "F_8_out_DES_1_OB",
                  "F_8_out_DES_1", "F_8_in_INJ_URS_BI",
                  "F_8_in_INJ_BI", "F_8_in_INJ_SE", "F_8_in_INJ_BD"],
        "Eq197": ["F_8_out_SK_FF_OB", "F_8_in_SK_G_1", "F_8_in_SK_G_2",
                  "F_8_in_DES_SK_DAM", "F_8_in_SK_AR"],

        # ============================================================
        # 4.2 Bombeamento de Água de Injeção (10 eq.)
        # ============================================================
        "Eq198": ["F_8_in_INJ_BB_DES", "F_8_in_BB_A", "F_8_in_BB_B", "F_8_in_BB_C"],
        "Eq199": ["F_8_in_BB_A", "F_8_out_BB_A", "F_8_out_BB_A_OD"],
        "Eq200": ["F_8_in_BB_B", "F_8_out_BB_B", "F_8_out_BB_B_OD"],
        "Eq201": ["F_8_in_BB_C", "F_8_out_BB_C", "F_8_out_BB_C_OD"],
        "Eq202": ["F_8_out_BB_A", "F_8_out_BB_B", "F_8_out_BB_C",
                  "F_6_in_TC_INT_INJ_BB", "F_8_out_BB_URS"],
        "Eq203": ["F_8_in_INT_INJ_B_TC", "F_8_in_B_A_TC", "F_8_in_B_B_TC"],
        "Eq204": ["F_8_in_B_A_TC", "F_8_in_B_A_DAR",
                  "F_8_out_B_A", "F_8_out_B_A_OD",
                  "F_8_out_B_A_URS_OB", "F_8_out_B_A_ANC"],
        "Eq205": ["F_8_in_B_B_TC", "F_8_in_B_B_DAR",
                  "F_8_out_B_B", "F_8_out_B_B_OD",
                  "F_8_out_B_B_URS_OB", "F_8_out_B_B_ANC"],
        "Eq206": ["F_8_out_B_AB", "F_8_out_B_A", "F_8_out_B_B"],
        "Eq207": ["F_8_out_B_AB", "F_8_in_AI_IJN", "F_8_in_ADO_INJ"]}
        
    # ============================================================
    # VARIÁVEIS DO SISTEMA
    # ============================================================
    variaveis = sorted({v for eq in equacoes.values() for v in eq})

    # ============================================================
    # SENSORES INSTALADOS
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