from __future__ import absolute_import
import six

from HiggsAnalysis.CombinedLimit.PhysicsModel import *

class g2HDM_2Bbased(PhysicsModel):
  def __init__(self):
    PhysicsModel.__init__(self)
  def doParametersOfInterest(self):
    self.modelBuilder.doVar("r_2b[1,0,20]")
    self.modelBuilder.doVar("Rb[1,0,2]")
    self.modelBuilder.doSet("POI", "r_2b,Rb")
    self.modelBuilder.factory_('expr::Scaling_2b("@0", r_2b)')
    self.modelBuilder.factory_('expr::Scaling_3b("@0*@1", r_2b, Rb)')
    mass = [200, 300, 350, 400, 500, 600, 700, 800, 900, 1000]
    process_Scaling_ = dict()
    for mass_ in mass:
      process_Scaling_['CGToBHpm_a_{}_rtt06_rtc04_2b'.format(mass_)] = '2b'
      process_Scaling_['CGToBHpm_a_{}_rtt06_rtc04_3b'.format(mass_)] = '3b'
    self.processScaling = process_Scaling_
    self.modelBuilder.out.Print()
  def getYieldScale(self, bin, process):
    for prefix, model in six.iteritems(self.processScaling):
      if process.startswith(prefix):
        return "Scaling_" + model
    return 1

class g2HDM_3Bbased(PhysicsModel):
  def __init__(self):
    PhysicsModel.__init__(self)
  def doParametersOfInterest(self):
    self.modelBuilder.doVar("r_3b[1,0,20]")
    self.modelBuilder.doVar("Rb[1,0,2]")
    self.modelBuilder.doSet("POI", "r_3b,Rb")
    self.modelBuilder.factory_('expr::Scaling_2b("@0*@1", r_3b, Rb)')
    self.modelBuilder.factory_('expr::Scaling_3b("@0", r_3b)')
    mass = [200, 300, 350, 400, 500, 600, 700, 800, 900, 1000]
    process_Scaling_ = dict()
    for mass_ in mass:
      process_Scaling_['CGToBHpm_a_{}_rtt06_rtc04_2b'.format(mass_)] = '2b'
      process_Scaling_['CGToBHpm_a_{}_rtt06_rtc04_3b'.format(mass_)] = '3b'
    self.processScaling = process_Scaling_
    self.modelBuilder.out.Print()
  def getYieldScale(self, bin, process):
    for prefix, model in six.iteritems(self.processScaling):
      if process.startswith(prefix):
        return "Scaling_" + model
    return 1


g2HDM_2Bbased = g2HDM_2Bbased()
g2HDM_3Bbased = g2HDM_3Bbased()

