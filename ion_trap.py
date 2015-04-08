#!/usr/bin/env python
from __future__ import division, absolute_import, print_function, unicode_literals
import numpy as np
from simulation_parameters import simulation_parameters
from equilibrium_positions import equilibrium_positions

class IonTrap:

        def __init__(self, omegax, omegaz, potential_config='potential', freq_reference = 0.0, magnetic_field_gradient = 0.0):
                
                self.omegax   =  2*np.pi * omegax
                self.omegaz   =  2*np.pi * omegaz
                self.potential_config = potential_config

                #Frequency reference is the frequency with respect to
                # which all other frequencies in the entire simulation 
                # are measured:
                self.freq_reference  = freq_reference  
                self.magnetic_field_gradient = magnetic_field_gradient

        def load(self, chain, zpositions=[]):

                #self.zpositions = zpositions
                self.chain    =   chain
                #Find the eq positions:
                p             =   simulation_parameters()

                #Set the position of ions:
                if self.potential_config == 'potential':
                        self.chain.set_zpositions( equilibrium_positions.get_positions(self.chain.num_of_ions, self.omegaz, p) )
                elif self.potential_config == 'positions':  
                        if len(zpositions) == self.chain.num_of_ions:
                                self.chain.set_zpositions( zpositions )
                        else:
                                raise Exception("Z position of ions must be given as a list with length equal to\n number of ions")
                else:
                        raise Exception('Wrong specification for potential_config {}.'.format(self.potential_config))
               
                self.chain.set_carrier_frequencies(self.freq_reference, self.magnetic_field_gradient)

                #Find and set the ion-ion couplings:
                self.chain.set_couplings( self.omegax )

                #Set expansion of chain's motion local in terms of normal destruction operators and vice versa, and eigenvalues.
                self.chain.set_normal_mode_structure()


                self.loaded   =  True
        
        def set_omegaz(self, omegaz):

                self.omegaz   =  2*np.pi * omegaz
                if self.loaded  == True:
                        self.load(self.chain)

        def set_omegax(self, omegax):
                
                self.omegax   =  2*np.pi * omegax
