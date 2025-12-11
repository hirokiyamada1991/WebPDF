import numpy as np
import os
import math
import matplotlib.pyplot as plt
from scipy import interpolate
from scipy import fft
from scipy.fft import dst, idst
from scipy import integrate
from pyodide.http import open_url

# path 情報取得
### 実行中のディレクトリpath取得 >> PyScriptの設定に依る

class Calc_PDF_from_xy():
    def __init__(self):
        #
        # Essential Parameters for PDF calculation
        #

        # UIにてダイナミックに変更する予定がある値群
        self.energyX = 113.0 * 1000 # eV           プロパティ
        self.atomList = [14, 8] # atomic number    プロパティ　
        self.atomConc = [1.0, 2.0] # atomic concentration
        self.pol = 0.55
        self.recoil = 1.0
        self.norm_min = 15.0 # A-1
        self.norm_max = 23.8 # A-1
        self.dr = 0.03
        self.r_max = 10

        self.rr      = np.arange(0.01, self.r_max, self.dr)
        # self.rr_show = np.arange(self.dr, self.r_max, self.dr)
        self.density = 0.065

        self.r_cut = 1.3
        self.norm_for_bg = 10

        #
        # No need to touch
        #

        self.fpL = [0.0, 0.0]  # f' anomalous X-ray formfactor
        self.fppL = [0.0, 0.0] # f" anomalous X-ray formfactor

        # ファイルからデータ読み込み
        ### txt データ配列
        self.comp_data = np.loadtxt("Compton.txt")
        self.form_data = np.loadtxt("FormFactor.txt")

        self.comp_list = []
        self.comp_total = []
        
        self.form_list = []
        self.form_total = []
        
        
        self.tt = np.arange(0.1, 28.0, 0.01)
        self.intensityRaw = self.tt * 0.0

        self.tt_bg = None
        self.intensityBG = self.tt * 0.0

        self.bg_factor = 1
        
        self.intensityCorr = self.tt * 0.0

        self.qq = self.CalcQfromTT()

        self.f2sum = self.tt * 0.0 # <f2>
        self.fsum_2 = self.tt * 0.0 + 0.0j # <f>2

        # 各種配列作成
        self.qq_interpolate = []
        self.qq_interpolate_raw = []
        
        self.iq_interpolate = []
        
        self.qq_interpolate_fill0 = []
        self.iq_interpolate_fill0 = []

        self._Gr = []    #   G(r)
        self._ggr = []   #   g(r)
        self._Tr = []    #   Tr
        self._RDF= []    #   RDF

        self._Gr_bFT = []    #     G(r) -bFT                            
        self._ggr_bFT = []   #     g(r) -bFT                          
        # self._Tr_bFT = []    #     Tr   -bFT                         
        # self._RDF_bFT= []    #     RDF  -bFT                         

        self._Gr_Lorch = []     #       G_Lorch(r)                                       
        self._ggr_Lorch = []    #       g_Lorch(r)                                        
        self._Tr_Lorch = []     #       Tr_Lorch                                         
        self._RDF_Lorch= []     #       RDF_Lorch         


        self.dl_filename  = "dl"                         
        self.bg_filename  = ""                         

        self.intensityCorr_norm_value=None

        self.sum_comp_total = None
    
    # for getting Sasaki f' and f"
    def Tr_bFT(self):
        return self._Tr * self._Gr_bFT
    def RDF_bFT(self):
        return self._RDF * self._Gr_bFT

    def RDF_bFT(self):
        return self._RDF * self._Gr_bFT

    def rr_show_cal(self): 
        return np.arange(self.dr, self.r_max, self.dr)
    def rmax_pos(self):
        return int(self.r_max/self.dr)
    
    def __print_debug(self, str):
        # print(str)
        pass
    def GetSasakiF1F2(self):
        self.fpL = []
        self.fppL = []
        for i in range(len(self.atomList)):
            if self.atomList[i] == 1 or self.atomList[i] == 2 or self.atomList[i] ==3:
                self.fpL.append(0.0)
                self.fppL.append(0.0)
                
            else:
                # 対象の元素のデータ読み込み
                fname = "f1f2_" + str(self.atomList[i]) + ".dat"
                ene, vf1, vf2 = np.loadtxt(fname, delimiter=" ").T
                
                f1 = interpolate.interp1d(ene, vf1)
                f2 = interpolate.interp1d(ene, vf2)
                fp = f1(self.energyX)
                fpp = f2(self.energyX)

                self.fpL.append(fp)
                self.fppL.append(fpp)            
                
        return  self.fpL, self.fppL

    # for getting comption scattering vs q
    def CalcComp(self):        
        self.comp_list = []
        for atom_number in self.atomList:
            temp = self.comp_data[atom_number-1][1]*np.exp((-self.comp_data[atom_number-1][2])*np.power((self.qq/4.0/np.pi),2.0)) \
                 + self.comp_data[atom_number-1][3]*np.exp((-self.comp_data[atom_number-1][4])*np.power((self.qq/4.0/np.pi),2.0)) \
                 + self.comp_data[atom_number-1][5]*np.exp((-self.comp_data[atom_number-1][6])*np.power((self.qq/4.0/np.pi),2.0)) \
                 + self.comp_data[atom_number-1][7]

            temp_comp = self.comp_data[atom_number-1][0] - np.power(temp, 2.0)
            self.comp_list.append(temp_comp)


        self.comp_total = self.qq * 0.0
        
        for i in range(len(self.atomConc)):
            self.comp_total = self.comp_total + (self.atomConc[i] / np.sum(np.array(self.atomConc))) * self.comp_list[i]

        self.comp_total = np.power(self.comp_total, self.recoil)
        
        return self.comp_total        
        
    # for getting formfactor vs q
    def CalcForm(self):
        self.form_list = []
        for atom_number in self.atomList:
            tempForm = self.form_data[atom_number-1][1]*np.exp(-self.form_data[atom_number-1][2]*np.power((self.qq/4.0/np.pi), 2.0)) \
                     + self.form_data[atom_number-1][3]*np.exp(-self.form_data[atom_number-1][4]*np.power((self.qq/4.0/np.pi), 2.0)) \
                     + self.form_data[atom_number-1][5]*np.exp(-self.form_data[atom_number-1][6]*np.power((self.qq/4.0/np.pi), 2.0)) \
                     + self.form_data[atom_number-1][7]*np.exp(-self.form_data[atom_number-1][8]*np.power((self.qq/4.0/np.pi), 2.0)) \
                     + self.form_data[atom_number-1][9]*np.exp(-self.form_data[atom_number-1][10]*np.power((self.qq/4.0/np.pi), 2.0)) \
                     + self.form_data[atom_number-1][11]

            self.form_list.append(tempForm)

    # for polarization correction
    def CorrPol(self):
        polList = self.pol + (1-self.pol) * np.cos(np.radians(self.tt)) * np.cos(np.radians(self.tt))
        self.intensityCorr = np.array(self.subtract_bg()) / polList
        return self.intensityCorr

    # for calculating Q from twotheta
    def CalcQfromTT(self):
        lamda = 12.3984 / (self.energyX / 1000)
        self.qq = []
        self.qq = 4.0 * np.pi * np.sin(np.radians(self.tt/2.0)) / lamda

        return self.qq

    # for calculating <f2> and <f>2
    def CalcFseries(self):
        # <f2>
        self.f2sum = []
        temp_f2sum = self.qq * 0.0
        for i in range(len(self.atomList)):
            temp_f2sum = temp_f2sum + (float(self.atomConc[i]) / np.sum(np.array(self.atomConc))) * np.power( (self.form_list[i] + self.fpL[i] + self.fppL[i] * 1j), 2.0).real
        self.f2sum = temp_f2sum


        # <f>2
        self.fsum_2 = []
        temp_fsum_2 = self.qq * 0.0
        for i in range(len(self.atomList)):
            temp_fsum_2 = temp_fsum_2 + ((float(self.atomConc[i]) / np.sum(np.array(self.atomConc))) * (self.form_list[i] + self.fpL[i] + self.fppL[i] * 1j))


        # numpy の複素数計算がいまいちなせいで仕方なく下記の実装、分かり次第修正した方が早い（いうてもほぼ速度は変わらんはず）
        for fsum2_each_q in temp_fsum_2:
            self.fsum_2.append(((fsum2_each_q * fsum2_each_q).real))

        self.fsum_2 = np.array(self.fsum_2)

        return self.f2sum, self.fsum_2

    # Calculating i(Q) and S(Q)
    def Calc_iQ_SQ(self):
        
        self.num_norm_min = 0
        self.num_norm_max = len(self.qq)-1
        print(self.qq)

        ip=None
        for i in range(len(self.qq)):
            if self.norm_min < self.qq[i]:
                self.num_norm_min = i
                ip=i
                break        

        for i in range(len(self.qq)):
            if self.norm_max < self.qq[i]:
                self.num_norm_max = i
                break   

        norm_value =np.average(self.intensityCorr[self.num_norm_min:self.num_norm_max] / (self.f2sum[self.num_norm_min:self.num_norm_max] + self.comp_total[self.num_norm_min:self.num_norm_max]))
        self.iq = (self.intensityCorr / norm_value - self.f2sum - self.comp_total) / self.fsum_2 
        self.sq = self.iq + 1
        self.__add_intensityCorr_norm_value(self.intensityCorr/norm_value)
        self.__add_sum_comp_total(self.f2sum+self.comp_total)
    
    def __add_intensityCorr_norm_value(self, value):  # 1. y1
        self.intensityCorr_norm_value=value 

    def __add_sum_comp_total(self, value):  # 1. y1
        self.sum_comp_total = value
    
    
    # Conventional slow FT, not recommended
    def CalcGrRaw(self):
        
        self.gGrRaw = []   
        
        for i in range(len(self.rr)):
            tempY = 2/math.pi * np.array(self.qq[:self.num_norm_max]) * np.array(self.iq[:self.num_norm_max]) * np.sin(np.array(self.qq[:self.num_norm_max]) * self.rr[i]) 
            tempGr = integrate.simps(tempY, self.qq[:self.num_norm_max])
            self.gGrRaw.append(tempGr)
        
        # プロット系一時コメントアウト

        return self.rr, self.gGrRaw

    def Interpolate(self):
        dq = self.qq[1] - self.qq[0]
        # qq_interpolate_0fill = np.arange(0, np.pi / self.dr , dq)
        qq_interpolate_0fill = np.arange(0, 2 * np.pi / dq , dq)



        self.nn = len(np.arange(0, self.qq[self.num_norm_max] , dq))
        self.nn_min = len(np.arange(0, self.qq[1] , dq))


        self.nn_max = len(qq_interpolate_0fill)

        # to make the high-resolution iQ, 0 value is filled in higher Q range
        iq_fill0 = self.iq
        iq_fill0[self.num_norm_max:] = iq_fill0[self.num_norm_max:] * 0
        fx = interpolate.interp1d(self.qq, iq_fill0 ,bounds_error=False, fill_value=(-1,0))
        iq_interpolate = fx(qq_interpolate_0fill)

        self.qq_interpolate_fill0 = qq_interpolate_0fill
        self.qq_interpolate = self.qq_interpolate_fill0[:self.nn]
        self.iq_interpolate_fill0 = iq_interpolate
        self.iq_interpolate = iq_interpolate[:self.nn]
        self.iq_interpolate_raw = self.iq_interpolate.copy()
        



    # Discrete sine Fourier transformation
    def CalcGrFFT(self):
        self.iq_interpolate_fill0[:self.nn] = self.iq_interpolate
        
        for_FT = np.array(self.qq_interpolate_fill0) * np.array(self.iq_interpolate_fill0)
        rr = np.linspace(np.pi/self.qq_interpolate_fill0[-1], np.pi/self.qq_interpolate_fill0[-1] * len(for_FT), len(for_FT), endpoint=True)

        
        self.rr = rr
        
        self._Gr = []
        self._ggr = []
        self._Tr = []
        self._RDF = []
        
        try:
            self.__print_debug("self._Gr = fft.dst")
            self.__print_debug((self._Gr[0]))
        except:
            pass
        self._Gr = fft.dst(x=for_FT, type=1) / (self.nn_max+1)**0.5 / np.pi * 2
        try:
            self.__print_debug("self._Gr = fft.dst")
            self.__print_debug((self._Gr[0]))
            self.__print_debug(type(self._Gr))
        except:
            pass
        self.__print_debug("shape::" + str(self._Gr.shape))
        self._ggr = self._Gr / (4.0 * np.pi * self.rr * self.density) + 1.0
        self._Tr = self._ggr * (4.0 * np.pi * self.rr * self.density)
        self._RDF = self._Tr * self.rr




    def Rcut_and_bFT(self):
    
        for_FT = np.array(self.qq_interpolate_fill0) * np.array(self.iq_interpolate_fill0)
        rr = np.linspace(np.pi/self.qq_interpolate_fill0[-1], np.pi/self.qq_interpolate_fill0[-1] * len(for_FT), len(for_FT), endpoint=True)
        
        self.rr = rr


        
        
        pos_cut =  int(self.r_cut / (self.rr[1]-self.rr[0]))
        print("rcut : dr")
        print((self.rr[1]-self.rr[0]))


    
        while True:
            if pos_cut == 0:
                break
            
            if (self._ggr[pos_cut] * self._ggr[pos_cut-1]) <= 0:
                break
            # print(pos_cut)
            pos_cut = pos_cut - 1
        
        self._ggr_bFT = self._ggr
        self._ggr_bFT[:pos_cut] = self._ggr_bFT[:pos_cut] * 0

        self._Gr_bFT = (self._ggr_bFT - 1.0) * (4.0 * np.pi * self.rr * self.density)
        
        self.iq_interpolate_fill0_bFT = fft.dst(x=self._Gr_bFT, type=1) / np.power(self.nn_max+1, 0.5) / self.qq_interpolate_fill0 / (np.pi/2)**0.5

        # self.iq_interpolate_bFT =  (self.iq_interpolate_fill0_bFT[self.nn_min:self.nn]).copy()
        self.iq_interpolate_bFT =  (self.iq_interpolate_fill0_bFT[:self.nn])
        print("self.iq_interpolate_bFT[0]")
        self.iq_interpolate_bFT[0] = self.iq_interpolate_bFT[1] - (self.iq_interpolate_bFT[2] - self.iq_interpolate_bFT[1])
        print("self.iq_interpolate_bFT[0] = -1")
        
        
        
        diff_iq = self.iq_interpolate - self.iq_interpolate_bFT
        v = np.ones(self.norm_for_bg)/float(self.norm_for_bg) # 移動平均をとるための配列vを設定。
        diff_iq_norm = np.convolve(diff_iq, v, mode='same') 

        self.iq_interpolate_bFT_smooth =  self.iq_interpolate - diff_iq_norm
        
        
    def UseSmoothBG(self):
        self.iq_interpolate = self.iq_interpolate_bFT_smooth.copy()
        
    def UseDirectBG(self):
        self.iq_interpolate = self.iq_interpolate_bFT.copy()
        self.iq_interpolate_fill0 = self.iq_interpolate_fill0_bFT.copy()
        

    def CalcGrLorch(self):
        
        self._Gr_Lorch  = []
        self._ggr_Lorch = []
        self._Tr_Lorch  = []
        self._RDF_Lorch = []

        delta_r = np.pi / self.qq_interpolate[-1]
        
        for i in range(len(self.rr_show_cal())):
            tempY = 2/math.pi * np.array(self.qq_interpolate[self.nn_min:]) * np.array(self.iq_interpolate[self.nn_min:]) * np.sin(np.array(self.qq_interpolate[self.nn_min:]) * self.rr_show_cal()[i]) * np.sin(np.array(self.qq_interpolate[self.nn_min:]) * delta_r) / (np.array(self.qq_interpolate[self.nn_min:]) * delta_r)
            
            tempGr = integrate.cumtrapz(tempY, self.qq_interpolate[self.nn_min:])
            self._Gr_Lorch.append(tempGr[-1])

        self._ggr_Lorch = self._Gr_Lorch / (4.0 * np.pi * self.rr_show_cal() * self.density) + 1.0
        self._Tr_Lorch = self._ggr_Lorch * (4.0 * np.pi * self.rr_show_cal() * self.density)
        self._RDF_Lorch = self._Tr_Lorch * self.rr_show_cal()

    def All_run(self):
        self.CalcQfromTT()
        self.GetSasakiF1F2()
        self.CorrPol()
        self.CalcComp()
        self.CalcForm()
        self.CalcFseries()
        self.Calc_iQ_SQ()
        # self.CalcGrRaw()
        self.Interpolate()
        self.CalcGrFFT()
    
    def SQ_run(self):
        self.CalcQfromTT()
        self.GetSasakiF1F2()
        self.CorrPol()
        self.CalcComp()
        self.CalcForm()
        self.CalcFseries()
        self.Calc_iQ_SQ()
        self.Interpolate()
        self.Rcut_and_bFT()
        self.UseSmoothBG()

    def BFT_smooth(self):
        self.Rcut_and_bFT()
        self.UseSmoothBG()
        self.CalcGrFFT()
        self.CalcGrLorch()

    def subtract_bg(self):
        print("1")
        if self.bg_filename == "": 
            print("2")
            return self.intensityRaw 
        else:
            print("3")
            print(self.intensityRaw.shape)
            print(self.intensityBG.shape)
            if  not self.intensityRaw.shape == self.intensityBG.shape:  # narray 比較
                print("4")
                return self.intensityRaw 
            else:
                print("5")
                subtract = self.intensityRaw - self.intensityBG * self.bg_factor
                subtract[subtract< 0] = 0
                return subtract


            # 引き算
            # 0未満を0に変換

###############################################################################################################################

if __name__ == '__main__':
    
    tes = Calc_PDF_from_xy()

    tes.tt, tes.intensityRaw = np.loadtxt("silica.xy").T
    tes.All_run()
    tes.BFT_smooth()
 
