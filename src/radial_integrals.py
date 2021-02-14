import math
import sys
import time

import scipy.integrate as integrate
from hankel import HankelTransform

from wave_functions import *


def main():
	start_tot = time.time()
	
	# Test individual integrals with different methods
	element = Ar
	n = 3
	l = 1
	integral = 2
	lPrime = 2
	L = 1
	k = 5*keV
	q = 10*keV
	
	for method in ["quadosc","Hankel","analytic","tanh-sinh-stepwise","numpy-stepwise"]:
	    print(method)
	    start = time.time()
	    int1 = radial_integral(integral,element,n,l,k,lPrime,L,q,method)
	    end = time.time()
	    print(int1,"\t(", end-start,"s)\n")

	# Find the best integration method
	print("\nFind the best integration method for a given set of parameters.\n")
	best_method = evaluate_integration_methods(integral, element, n, l, k, lPrime, L, q,True);

	####################################################################################
	end_tot = time.time()
	print("\nProcessing time:\t", end_tot - start_tot, "s\n")

# Radial integral wrapper function
def radial_integral(integral, element, n, l, kPrime, lPrime, L, q,method):
	if method == "quadosc":
		return radial_integral_quadosc(integral,element, n, l, kPrime, lPrime, L, q)
	elif method == "Hankel":
		return radial_integral_hankel(integral,element, n, l, kPrime, lPrime, L, q)
	elif method == "analytic":
		return radial_integral_analytic(integral,element, n, l, kPrime, lPrime, L, q)
	elif method == "tanh-sinh":
		return radial_integral_tanhsinh(integral,element, n, l, kPrime, lPrime, L, q)
	elif method == "tanh-sinh-stepwise":
		return radial_integral_tanhsinh_stepwise(integral,element, n, l, kPrime, lPrime, L, q)
	elif method == "numpy":
		return radial_integral_numpy(integral,element, n, l, kPrime, lPrime, L, q)
	elif method == "numpy-stepwise":
		return radial_integral_numpy_stepwise(integral,element, n, l, kPrime, lPrime, L, q)
	else:
		sys.exit("Error in radial_integral: Method not recognized.")

# Various integration methods

def radial_integral_quadosc(integral, element, n, l, kPrime, lPrime, L, q):
	if integral == 1:
		integrand = lambda r : r*r*element.R(n,l,r)*R_final_kl(r,kPrime,lPrime,element.Z_effective(n,l)) * mp.sqrt(mp.pi / 2 / q / r) * mp.besselj(L+1/2,q*r)
	elif integral == 2:
	   integrand = lambda r : r*r*element.dRdr(n,l,r)*R_final_kl(r,kPrime,lPrime,element.Z_effective(n,l)) * mp.sqrt(mp.pi / 2 / q / r) * mp.besselj(L+1/2,q*r)
	elif integral == 3:
		integrand = lambda r : r*element.R(n,l,r)*R_final_kl(r,kPrime,lPrime,element.Z_effective(n,l)) * mp.sqrt(mp.pi / 2 / q / r) * mp.besselj(L+1/2,q*r)
	else:
		sys.exit("Error in radial_integral_quadosc(): Invalid integral.")

	frequency = max(kPrime/2/mp.pi ,  q/2/mp.pi , keV/2/mp.pi) 
	return mp.quadosc(integrand,[0,mp.inf],omega = frequency)

def radial_integral_analytic(integral,element, n, l, kPrime, lPrime, L, q):
	S=0
	SMAX = 200
	result = 0
	tol = 1e-20
	eps_1=1;
	eps_2=1;
	if integral == 1 or integral == 3:
		a = lPrime + 1 + 1j* element.Z_effective(n,l) / (kPrime*a0);
		b = 2 * lPrime + 2;
		while( (eps_1 > tol or eps_2 > tol) and S <= SMAX ):
			eps_2 = eps_1
			As = 0
			for j in range(len(element.C_nlj[n-1][l])):
				alpha = lPrime + element.n_lj[l][j] + S;
				if integral == 1:
					alpha += 1
				beta = element.Z_lj[l][j]/a0 + 1j * kPrime
				As += 4 * mp.pi * mp.power(2*kPrime,lPrime) * element.C_nlj[n-1][l][j] * mp.power(2*element.Z_lj[l][j],element.n_lj[l][j]+0.5) / mp.power(a0,element.n_lj[l][j]+0.5) * (mp.sqrt(mp.pi)/mp.power(2,L+1) * mp.power(q,L) * mp.hyp2f1(0.5*(L+alpha+1),0.5*(L+alpha+2),L+1.5,-mp.power(q/beta,2))) * mp.exp(S*mp.log(2j*kPrime) - (alpha+L+1)*mp.log(beta)+ mp.loggamma(lPrime+1-1j*element.Z_effective(n,l)/kPrime/a0).real + mp.loggamma(S+a)+mp.loggamma(b)-mp.loggamma(2*lPrime+2)-mp.loggamma(S+b)-mp.loggamma(a)-mp.loggamma(S+1)+mp.pi*element.Z_effective(n,l)/2/kPrime/a0-0.5*mp.loggamma(2*element.n_lj[l][j]+1)+mp.loggamma(L+alpha+1)-mp.loggamma(L+1.5))
			
			result += As
			eps_1 = abs(As) / abs(result)
			S += 1
	elif integral == 2:
		result = 0
	else:
		sys.exit("Error in radial_integral_analytic(): Invalid integral.")   
	if S > SMAX:
		return False
	else: 
		return result.real

def radial_integral_hankel(integral,element, n, l, kPrime, lPrime, L, q):
	ht = HankelTransform(
		nu= L+1/2 ,    	# The order of the bessel function
		N = 500,   		# Number of steps in the integration
		h = 0.001   	# Proxy for "size" of steps in integration
	)
	if integral == 1:
		f = lambda r: np.sqrt(np.pi*r/2/q) * element.R_alternative(n,l,r) * R_final_kl_alternative(r,kPrime,lPrime,element.Z_effective(n,l))
	elif integral ==2:
		f = lambda r: np.sqrt(np.pi*r/2/q) * element.dRdr_alternative(n,l,r) * R_final_kl_alternative(r,kPrime,lPrime,element.Z_effective(n,l))
	elif integral == 3:
		f = lambda r: np.sqrt(np.pi/2/q/r) * element.R_alternative(n,l,r) * R_final_kl_alternative(r,kPrime,lPrime,element.Z_effective(n,l))
	else:
		sys.exit("Error in radial_integral_hankel(): Invalid integral.")
	return ht.transform(f,q,ret_err=False).real

def radial_integral_tanhsinh(integral,element, n, l, kPrime, lPrime, L, q):
	if integral == 1:
		integrand = lambda r : r*r*element.R(n,l,r)*R_final_kl(r,kPrime,lPrime,element.Z_effective(n,l)) * mp.sqrt(mp.pi / 2 / q / r) * mp.besselj(L+1/2,q*r)
	elif integral == 2:
		integrand = lambda r : r*r*element.dRdr(n,l,r)*R_final_kl(r,kPrime,lPrime,element.Z_effective(n,l)) * mp.sqrt(mp.pi / 2 / q / r) * mp.besselj(L+1/2,q*r)
	elif integral == 3:
		integrand = lambda r : r*element.R(n,l,r)*R_final_kl(r,kPrime,lPrime,element.Z_effective(n,l)) * mp.sqrt(mp.pi / 2 / q / r) * mp.besselj(L+1/2,q*r)
	else:
		sys.exit("Error in radial_integral_tanhsinh(): Invalid integral.")
	
	return mp.quad(integrand, [0, 100*a0],method='tanh-sinh')

def radial_integral_tanhsinh_stepwise(integral,element, n, l, kPrime, lPrime, L, q):
	if integral == 1:
		integrand = lambda r : r*r*element.R(n,l,r)*R_final_kl(r,kPrime,lPrime,element.Z_effective(n,l)) * mp.sqrt(mp.pi / 2 / q / r) * mp.besselj(L+1/2,q*r)
	elif integral == 2:
		integrand = lambda r : r*r*element.dRdr(n,l,r)*R_final_kl(r,kPrime,lPrime,element.Z_effective(n,l)) * mp.sqrt(mp.pi / 2 / q / r) * mp.besselj(L+1/2,q*r)
	elif integral == 3:
		integrand = lambda r : r*element.R(n,l,r)*R_final_kl(r,kPrime,lPrime,element.Z_effective(n,l)) * mp.sqrt(mp.pi / 2 / q / r) * mp.besselj(L+1/2,q*r)
	else:
		sys.exit("Error in radial_integral_tanhsinh_stepwise(): Invalid integral.")
	
	da0 = 1
	integral = 0
	eps_1 = 1
	eps_2 = 1
	tol = 1e-6
	i=0
	while eps_1 > tol or eps_2 > tol:
		eps_2 = eps_1
		dintegral = mp.quad(integrand, [i*a0,(i+da0)*a0],method='tanh-sinh')
		integral += dintegral
		eps_1 = abs(dintegral) / abs(integral)
		i+=da0
	return integral

def radial_integral_numpy(integral,element, n, l, kPrime, lPrime, L, q):
	if integral == 1:
		integrand = lambda r : r*r*element.R_alternative(n,l,r)*R_final_kl_alternative(r,kPrime,lPrime,element.Z_effective(n,l)) * special.spherical_jn(L,q*r)
	elif integral == 2:
		integrand = lambda r : r*r*element.dRdr_alternative(n,l,r)*R_final_kl_alternative(r,kPrime,lPrime,element.Z_effective(n,l)) * special.spherical_jn(L,q*r)
	elif integral == 3:
		integrand = lambda r : r*element.R_alternative(n,l,r)*R_final_kl_alternative(r,kPrime,lPrime,element.Z_effective(n,l)) * special.spherical_jn(L,q*r)
	else:
		sys.exit("Error in radial_integral_numpy(): Invalid integral.")
	return integrate.quad(integrand,0,100*a0)[0]

def radial_integral_numpy_stepwise(integral,element, n, l, kPrime, lPrime, L, q):
	if integral == 1:
		integrand = lambda r : r*r*element.R_alternative(n,l,r)*R_final_kl_alternative(r,kPrime,lPrime,element.Z_effective(n,l)) * special.spherical_jn(L,q*r)
	elif integral == 2:
		integrand = lambda r : r*r*element.dRdr_alternative(n,l,r)*R_final_kl_alternative(r,kPrime,lPrime,element.Z_effective(n,l)) * special.spherical_jn(L,q*r)
	elif integral == 3:
		integrand = lambda r : r*element.R_alternative(n,l,r)*R_final_kl_alternative(r,kPrime,lPrime,element.Z_effective(n,l)) * special.spherical_jn(L,q*r)
	else:
		sys.exit("Error in radial_integral_numpy_stepwise(): Invalid integral.")
	
	da0 = 1
	integral = 0
	eps_1 = 1
	eps_2 = 1
	tol = 1e-6
	i=0
	while eps_1 > tol or eps_2 > tol:
		eps_2 = eps_1
		dintegral = integrate.quad(integrand, i*a0,(i+da0)*a0,epsrel = 1e-3)[0]
		integral += dintegral
		eps_1 = abs(dintegral) / abs(integral)
		i+=da0
	return integral

# Function to evaluate the different methods, and return the fastest working method.
def evaluate_integration_methods(integral, element, n, l, kPrime, lPrime, L, q,output = False):
	# Integration method hierarchy
	methods_hierarchy = ["analytic", "numpy-stepwise", "quadosc"]

	# Compute the integral with different methods
	results = []
	if output: print("Initial integration results:")
	for method in methods_hierarchy:
		t_1 = time.time()
		result = radial_integral(integral, element, n,l, kPrime, lPrime, L, q, method)
		t_2 = time.time()
		duration = t_2 - t_1
		if result == result:
			results.append([method, float(result), duration])
			if output: print(method,"\t",float(result),"\t",duration)
			if method == "numpy-stepwise":
				break

	# Identify methods giving correct results
	working_methods = []
	# 1. Check for dublicates
	for result in results:
		for other_result in (x for x in results if x != result):
			if math.isclose(result[1], other_result[1], rel_tol=1e-2):
				working_methods.append(result)
				break
	if output:
		print("Dublicates:")
		if len(working_methods) == 0:
			print("None.")
		else:
			for result in working_methods:
				print(result[0],"\t",result[1],"\t",result[2])
	# 2. Without dublicates, we need to compare to quadosc
	if len(working_methods) == 0:
		if any("quadosc" in result for result in results):
			for result in results:
				if result[0] == "quadosc":
					working_methods.append(result)
					if output: print(result[0],"\t",result[1],"\t",result[2])
					break
		else:
			t_1 = time.time()
			result_quadosc = radial_integral(integral, element, n, l, kPrime, lPrime, L, q, "quadosc")
			t_2 = time.time()
			duration = t_2 - t_1
			results.append(["quadosc", float(result_quadosc), duration])
			if output: print(results[-1][0],"\t",results[-1][1],"\t",results[-1][2])
			for result in results:
				for other_result in (x for x in results if x != result):
					if math.isclose(result[1], other_result[1],rel_tol = 1e-2):
						working_methods.append(result)
			if len(working_methods) == 0:
				for result in results:
					if result[0] == "numpy-stepwise":
						working_methods.append(result)
						break

	# Return the fastest of the good methods
	working_methods.sort(key = lambda x: x[2])
	if output:
		print("Working methods:")
		for result in working_methods:
			print(result[0],"\t",result[1],"\t",result[2])
		print("\nBest method:\t",working_methods[0][0])
	return working_methods[0][0]

if __name__ == "__main__":
	main()