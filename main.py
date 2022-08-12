# region imports
from AlgorithmImports import *
# endregion

import numpy as np
class EnergeticMagnetaViper(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2019, 1, 1)# Set Start Date
        self.SetEndDate(2020,6,30)#Set End Date
        self.SetCash(10000)  # Set Strategy Cash
                                  #Strong Inc               Inc                   Stag                     Dec            Strong Dec
        self.Tmat =    np.array([[0.0,0.0,0.0,0.0,0.0],[0.0,0.0,0.0,0.0,0.0],[0.0,0.0,0.0,0.0,0.0],[0.0,0.0,0.0,0.0,0.0],[0.0,0.0,0.0,0.0,0.0]])
        self.tempMat = np.array([[0.0,0.0,0.0,0.0,0.0],[0.0,0.0,0.0,0.0,0.0],[0.0,0.0,0.0,0.0,0.0],[0.0,0.0,0.0,0.0,0.0],[0.0,0.0,0.0,0.0,0.0]])
        self.typeTotal = np.array([0.0,0.0,0.0,0.0,0.0])
        self.costs = []
        self.name = "TSLA"
        self.diff = 1.0
        self.SetWarmUp(200,Resolution.Daily)
        self.AddEquity(self.name, Resolution.Daily)
    def change(self,c):
        if c>.5:
            return 0
        elif c>.25:
            return 1
        elif c<-.5:
            return 4
        elif c<-.25:
            return 3
        else:
            return 2
    def makeMarkov(self, cost):
        self.typeTotal = self.typeTotal*0.0
        self.Tmat = self.Tmat * 0
        f = (self.costs[1]-self.costs[0])
        for i in range(1,len(self.costs)-1):
            t = (self.costs[i+1]-self.costs[i])
            self.Tmat[self.change(f)][self.change(t)]+=1
            self.typeTotal[self.change(f)]+=1
            f = t
        self.tempMat = self.Tmat * 1
        self.Tmat[0] = self.Tmat[0]/self.typeTotal[0]
        self.Tmat[1] = self.Tmat[1]/self.typeTotal[1]
        self.Tmat[2] = self.Tmat[2]/self.typeTotal[2]
        self.Tmat[3] = self.Tmat[3]/self.typeTotal[3]
        self.Tmat[4] = self.Tmat[4]/self.typeTotal[4]
    def OnData(self, data):
        if (self.EndDate - self.Time).days == 0:
                self.Debug("end and liquidate")
                self.Liquidate(self.name)
                return
        if self.IsWarmingUp:
            self.costs.append(data[self.name].Close)
            self.Debug(f"Time: {self.Time}\nCost: {self.costs[-1]}\n")
        else:
            self.makeMarkov(self.costs)
            self.costs.append(data[self.name].Close)
            x = self.Tmat[self.change(self.costs[-1]-self.costs[-2])]
            self.Debug(f"{self.change(self.costs[-1]-self.costs[-2])}")
            m = np.argmax(x)
            if abs((x[0]+x[1])-(x[3]+x[4]))<0.05:
                self.Debug("change too similar")
                return
            elif m<2:
                self.SetHoldings(self.name,1.5*(x[0])+x[1])
            elif m>2:
                self.SetHoldings(self.name,(-1*(x[3]+(1.25*x[4]))))
            self.Debug(f"{m}")
            self.Debug(f"{self.Tmat[0]}")
            self.Debug(f"{self.Tmat[1]}")
            self.Debug(f"{self.Tmat[2]}")
            self.Debug(f"{self.Tmat[3]}")
            self.Debug(f"{self.Tmat[4]}")
        return