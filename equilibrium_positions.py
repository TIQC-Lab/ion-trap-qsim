import numpy as np
from numpy import *
from scipy.optimize import newton_krylov as nt
import simulation_parameters
import math

p = simulation_parameters.SimulationParameters()

class equilibrium_positions(object):

    
    @classmethod
    def get_positions(cls, number_of_ions, potential, initial_positions_guess=[]):
        
        '''If potenial.config is 'harmonic' it takes the trap frequency in Rad/Sec and returns the axial positions of an ion chain for that frequency
           If potenial.config is 'generic' it takes potential function on the trap axis and returns positions (assuming 
            a minimum exists for the given number of ions.

            initial_positions_guess is an initial guess for positions of ions in SI units. 
        '''

        N = number_of_ions

        if potential.config == 'generic':



                energy_coeffs       = array( potential.energy_along_Z )[::-1]
                potential.energy_deriv_along_Z           =  polyder( potential.energy_along_Z, 1 )
                energy_deriv_coeffs_inverted = array( potential.energy_deriv_along_Z )[::-1]

                
                #Find the first nonzero coefficient in Z dependent energy function 
                #of second or higher order in Z, 
                try: 
                        nonzero_index = min([i for i in range(1, len(energy_deriv_coeffs_inverted)) if abs(energy_deriv_coeffs_inverted[i]) > 0])


                except ValueError, e:
                        raise Exception(e, "\nNontrapping potential energy.")

                #and use that coeff to find appropriate position_scale_factor.
                #For example, if second element of energy_deriv_coeffs_inverted is nonzero, then nonzero_index = 1, 
                #and that would be equivalent to mass * omegaz**2, 
                #and in this case, position_scale_factor will reduce to that of DJames 1997.
                #In general case, that coeff may not be zero, and the following will give the right scaling factor:
                n = nonzero_index + 1
                position_scale_factor  = ( p.coulomb_coeff / abs(energy_deriv_coeffs_inverted[nonzero_index]) )**(1./(n+1)) 
                #print("position_scale_factor " + str(position_scale_factor))
                #print energy_deriv_coeffs_inverted[nonzero_index]
                
                energy_deriv_along_Z_rescaled  = poly1d(  [ (position_scale_factor**i) * energy_deriv_coeffs_inverted[i]/( (position_scale_factor**nonzero_index) * energy_deriv_coeffs_inverted[nonzero_index]) \
                                                             for i in range(len(energy_deriv_coeffs_inverted)) ][::-1] )
                

                if p.do_print:
                    print("nonzero_index is: ", nonzero_index)
                    print("energy_deriv_coeffs_inverted: ", energy_deriv_coeffs_inverted)
                    
                    print("Potential energy: ", potential.energy_along_Z)
                    print("Potential energy deriv: ", potential.energy_deriv_along_Z)
                    print("Rescaled potential energy deriv: ", energy_deriv_along_Z_rescaled)
                    print("Guess positions: "+str(u_guess*position_scale_factor) )
                    print("Positions: ", positions_arr)
                    

                '''
                if nonzero_index == 1:
                        ax_freq_sq  = polyder(potential.energy_deriv_along_Z,1)(0.)/p.mass 
                        if ax_freq_sq>0:
                                potential.axial_freq  = sqrt( ax_freq_sq )
                                if p.do_print:
                                    print("Axial freq from deriv: ",  potential.axial_freq)
                        else:
                                raise Exception("\nNontrapping potential energy.")

                else:
                        #If coefficient of Z^2 in potential energy is zero, estimate axial freq at 10 microns from Z center
                        ax_freq_sq  = polyder(potential.energy_deriv_along_Z,1)(5.e-6)/p.mass
                        
                        if ax_freq_sq>0:
                                potential.axial_freq  = sqrt( ax_freq_sq )
                                if p.do_print:
                                    print("Axial freq from deriv: ",  potential.axial_freq )
                        else:
                                raise Exception("\nNontrapping potential energy.")

                '''



                if len(initial_positions_guess) == 0:
                            u0                     = (2.018/(N**0.559)) * np.array( np.linspace(-1,1, N) )
                            func_harmonic          = lambda m, u: u[m] - sum( [ 1./(u[m]-u[n])**2 for n in range(m) ] ) + sum( [ 1./(u[m]-u[n])**2 for n in range(m+1, N) ] )
                            f_harmonic             = lambda u : [func_harmonic(m,u) for m in range(N)]
                            #position_scale_factor  = (p.coulomb_coeff / (self.axial_freq**2 * p.mass))**(1./3) 
                            u_guess                =  nt(f_harmonic, u0)
                        
                else:
                            u_guess                = initial_positions_guess/position_scale_factor

                
                #print u_guess
                #print energy_deriv_along_Z_rescaled

                #Using rescaled ion positions in a harmonic potential obtained from coefficient of z^2 as initial guess for potential
                #minimization, find ion positions in the case of generic potential
                func          = lambda m, u: energy_deriv_along_Z_rescaled(u[m]) - sum( [ 1./(u[m]-u[n])**2 for n in range(m) ] ) + sum( [ 1./(u[m]-u[n])**2 for n in range(m+1, N) ] )
                f             = lambda u : [func(m,u) for m in range(N)]

                #import IPython as ip
                #ip.embed()

                for fun in f(u_guess):
                    if math.isnan(fun):
                        raise Exception("Is not a Number")


                u_arr =  nt(f, u_guess, maxiter=10) 

                #if min(abs(diff(u_arr))) <= 2.018/N**0.559
                #print("u_arr ", u_arr)

                positions_arr = u_arr * position_scale_factor

               

        elif potential.config == 'harmonic':
                omegaz  = potential.axial_freq #Assuming it already contains 2*np.pi when Potential instance was created.

                #Look at DJ 1997 paper
                u_guess = (2.018/(N**0.559)) * np.array( np.linspace(-1,1, N) )
                func    = lambda m, u: u[m] - sum( [ 1./(u[m]-u[n])**2 for n in range(m) ] ) + sum( [ 1./(u[m]-u[n])**2 for n in range(m+1, N) ] )
                f       = lambda u : [func(m,u) for m in range(N)]
                position_scale_factor  = (p.coulomb_coeff / (omegaz**2 * p.mass))**(1./3) 
                positions_arr =  nt(f, u_guess) * position_scale_factor

        



        return positions_arr


'''
known relative positions of the ions within a linear ion chain

Extension on Daniel James 'Quantum dynamics of cold trapped ions with application to quantum computation'. Table 1.


    position_dict = {
                    1:                                         [0],
                    2:                                  [-.62996, .62996],
                    3:                                 [-1.0772, 0, 1.0772],
                    4:                          [-1.4368, -0.454379, 0.454379,1.4368],
                    5:                         [-1.7429, -0.822101, 0, 0.822099,1.7429],
                    6:                  [-2.01227, -1.13612, -0.36992, 0.36992, 1.13612, 2.01227],
                    7:                 [-2.25454, -1.41292, -0.686944, 0, 0.686942, 1.41292, 2.25454],
                    8:           [-2.47582, -1.66206, -0.967007, -0.318021,0.318021, 0.967007, 1.66206, 2.47582],
                    9:         [-2.68026, -1.8897, -1.21947, -0.599575, 0, 0.599576, 1.21947, 1.8897,2.68026],
                    10: [-2.87082, -2.10003, -1.45038, -0.853778, -0.282103, 0.282103, 0.853778, 1.45038, 2.10003, 2.87082],
                    11: [-3.04973, -2.29608, -1.66389, -1.08654, -0.537174, 0, 0.53717, 1.08654, 1.66388, 2.29607,3.04972],
                    12: [-3.21865, -2.48009, -1.86298, -1.30194, -0.770985, -0.255408, 0.255407, 0.770984, 1.30194, 1.86298, 2.48009, 3.21865],
                    13: [-3.37893, -2.6538, -2.04993, -1.50294, -0.987549, -0.489777, 0, 0.489772, 0.987544, 1.50293, 2.04992, 2.6538, 3.37892],
                    14: [-3.53161, -2.81857, -2.22644, -1.69175, -1.18977, -0.707032, -0.234593, 0.234593, 0.707031, 1.18977, 1.69175, 2.22644, 2.81857, 3.53161],
                    15: [-3.67758, -2.97549, -2.39389, -1.87011, -1.37984, -0.910043, -0.452233, 0, 0.452228, 0.910038,1.37984, 1.87011, 2.39389, 2.97548, 3.67758],
                    16: [-3.81754, -3.12545, -2.55338, -2.03936, -1.55946, -1.10096, -0.655727, -0.217797, 0.217796, 0.655726, 1.10096, 1.55946,2.03936, 2.55338, 3.12545, 3.81754],
                    17: [-3.9521, -3.2692, -2.70581, -2.2006, -1.72997, -1.28146, -0.847207, -0.421567, 0, 0.421565, 0.847205, 1.28146, 1.72997, 2.2006, 2.70581, 3.2692, 3.9521],
                    18: [-4.08177, -3.40736, -2.85192, -2.35473, -1.89246, -1.45287, -1.02832, -0.613404, -0.203887, 0.203886, 0.613402, 1.02832, 1.45287, 1.89246, 2.35473, 2.85192, 3.40735,4.08177],
                    19: [-4.20698, -3.54044, -2.99234, -2.50249, -2.04782, -1.61628, -1.20039, -0.794937, -0.395929, 0, 0.395927, 0.794935, 1.20038, 1.61628, 2.04782, 2.50249, 2.99234, 3.54044, 4.20698],
                    20: [-4.32811, -3.66892, -3.12761, -2.64451, -2.19679, -1.77255, -1.36446, -0.967463, -0.577733, -0.192132, 0.192129, 0.577731, 0.967461, 1.36446, 1.77255, 2.19679, 2.64451, 3.12761, 3.66892, 4.32811],
                    25: [-4.87094, -4.24383, -3.73163, -3.27695, -2.85793, -2.46328, -2.08616, -1.72197, -1.36739, -1.01986, -0.677284, -0.337872, 0, 0.337872, 0.677284, 1.01986, 1.36739, 1.72197, 2.08616, 2.46328, 2.85793, 3.27695, 3.73163, 4.24383, 4.87094],
                    }


'''


