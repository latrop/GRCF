#include <stdio.h>
#include <gsl/gsl_math.h>
#include "gsl/gsl_integration.h"
#include "gsl/gsl_sf.h"
#include <gsl/gsl_errno.h>
#include <gsl/gsl_roots.h>
#include <gsl/gsl_spline.h>
#include <iostream>

using namespace std;

#include "disc.h"
#include "bulge.h"
#include "halo.h"
#include "ri_rf.h"
#include "disc.cpp"
#include "bulge.cpp"
#include "halo.cpp"
#include "ri_rf.cpp"
#include "const.h"

extern "C" int c_v_disk(double * disk_params,
			double * general_params,
			double * distances,
			double * v_squared,
			int num_of_points){

  /* Unpack parameters of disk model */
  double m0, h, z0_h, qd_obs, M_L_d;
  m0 = disk_params[0];
  h = disk_params[1];
  z0_h = disk_params[2];
  qd_obs = disk_params[3];
  M_L_d = disk_params[4];
  /* Unpack general parameters */
  double Hz, DL_Mpc, DL_kpc, scale, M_sun;  
  Hz = general_params[0];
  DL_Mpc = general_params[1];
  scale = general_params[2];
  M_sun = general_params[3];
  
  /* Produce all necessary convertations between units */
  DL_kpc = DL_Mpc*1e3/206265; //in kpc  
  h = h*scale; // in kpc
  double z0=z0_h*h;  // in kpc
  double correction = DL_kpc*DL_kpc / scale / scale;
  
  double     q0 = z0_h;
  double    q02 = q0*q0;
  double  cosi2 = (qd_obs*qd_obs - q02)/(1.0 - q02);
  
  double     I0d = 4.255*pow(10, 0.4*(M_sun - m0))*1e4; 
  // m0 - is face-on!
  
  double      Ld = 2*M_PI*I0d*h*h;
  // if I0d is face-on one using h*h
  // at edge-on position - h*z0
  // in 10^10 L_sun
  
  Ld = Ld*correction;
  
  double    fact_md = MSUN*M_L_d;
  double     Mass_d = Ld*fact_md;
  double      fact1 = 2*Mass_d*GRAV / PARSEC;
  double fact_thick = fact1 / M_PI / z0;
  double  fact_thin = fact1 / h;
  
  struct vd2_params params_d1;
  params_d1.z0 = z0_h;
  double rr; // in kpc
  double vd;
  int i=0;

  /* Compute velocities for all distances */
  for(i=0; i < num_of_points; i++)
    {
      rr = distances[i];
      if (z0_h <= 0.01)
	{
	  double y = 0.5*rr / h;
	  vd = fact_thin*vd2_thin(y);
	}
      else
	vd = fact_thick*vd2(rr / h, (void*) &params_d1);
      v_squared[i] = vd;
    }
  return 0;
}


extern "C" int c_v_bulge(double * bulge_params,
			 double * disk_params,
			 double * general_params,
			 double * distances,
			 double * v_squared,
			 int num_of_points){

  /* Unpack bulge parameters */
  double mu_eb, reb, nsersic, qb_obs, M_L_b;
  mu_eb = bulge_params[0];
  reb = bulge_params[1];
  nsersic = bulge_params[2];
  qb_obs = bulge_params[3];
  M_L_b = bulge_params[4];

  /* Unpack disc parameters (we need them for inclination computing) */
  double z0_h, qd_obs;
  z0_h = disk_params[0];
  qd_obs = disk_params[1];

  /* Unpack general parameters */
  double Hz, DL_Mpc, scale, M_sun;
  Hz = general_params[0];
  DL_Mpc = general_params[1];
  scale = general_params[2];
  M_sun = general_params[3];

  reb*=scale; // in kpc
  double DL_kpc = DL_Mpc*1e3; //in kpc
  DL_kpc = DL_kpc / 206265;
  
  double correction = DL_kpc*DL_kpc / scale / scale;

  double qb_int;
  double    q02 = z0_h*z0_h;
  double  cosi2 = (qd_obs*qd_obs - q02)/(1.0 - q02);
  qb_int = sqrt((qb_obs*qb_obs - cosi2)/(1.0 - cosi2));
  if (qb_obs==1) qb_int = 1.0;

  double   n_1 = 1.0 / nsersic;
  double   n_2 = 2.0 * nsersic;
  double    r0 = reb / pow(bn(nsersic), nsersic);
  double fact2 = GRAV / PARSEC;
  double   I0b = 4.255*pow(10, 0.4*(M_sun - mu_eb)) * exp(bn(nsersic))*1e4;
  // in 10^10 L_sun / kpc^2

  double Lb_fact = 4*I0b*r0*r0*qb_obs;
  double      Lb = 2*M_PI*nsersic*gsl_sf_gamma(n_2)*I0b*r0*r0*qb_obs;
  //*1e6;
  // with qb_obs - elliptical isophotes
  // in 10^10 L_sun
  Lb_fact = Lb_fact*correction;
  Lb = Lb*correction;
  
  double fact_mb = MSUN*M_L_b;
  double  Mass_b = Lb*fact_mb;

  struct vb2_params params_b1;
  params_b1.nsersic = nsersic;
  params_b1.qb = qb_int;

  int i=0;
  double fact_velb = fact_mb*Lb_fact*fact2 / r0;
  /* Compute velocities for all distances */
  for(i=0; i < num_of_points; i++)
      v_squared[i] = fact_velb*vb2(distances[i] / r0, (void*) &params_b1);

  return 0;
}

extern "C" int c_v_halo(double * bulge_params,
			double * disk_params,
			double * halo_params,
			double * general_params,
			double * distances,
			double * v_squared,
			int num_of_points){

  /* Unpack bulge parameters */
  double mu_eb, reb, nsersic, qb_obs, M_L_b, qb_int;
  mu_eb = bulge_params[0];
  reb = bulge_params[1];
  nsersic = bulge_params[2];
  qb_obs = bulge_params[3];
  M_L_b = bulge_params[4];

  /* Unpack disc parameters */
  double m0, h, z0_h, qd_obs, M_L_d, z0;
  m0 = disk_params[0];
  h = disk_params[1];
  z0_h = disk_params[2];
  qd_obs = disk_params[3];
  M_L_d = disk_params[4];

  /* Unpack halo parameters (list of parameters depends on halo type) */
  int includeAC, hType;
  hType = (int) halo_params[0];
  includeAC = (int) halo_params[1];
  double Rc, vinf, concentr, v200;
  if (hType == 0){
    // Isothermal halo
    Rc = halo_params[2];
    vinf = halo_params[3];
  }
  else{
    // NWF halo
    concentr = halo_params[2];
    v200 = halo_params[3];
  }

  /* Unpack general parameters */
  double Hz, DL_Mpc, DL_kpc, scale, M_sun;
  Hz = general_params[0];
  DL_Mpc = general_params[1];
  scale = general_params[2];
  M_sun = general_params[3];

  /* convertion of lengths to kpc */
  h*=scale; // in kpc
  z0=z0_h*h;  // in kpc
  reb*=scale; // in kpc

  DL_kpc = DL_Mpc*1e3; //in kpc
  DL_kpc = DL_kpc / 206265;
  double correction = DL_kpc*DL_kpc / scale / scale;

  /* disc parameters convertions */
  double     q0 = z0_h;
  double    q02 = q0*q0;
  double  cosi2 = (qd_obs*qd_obs - q02)/(1.0 - q02);
 
  double     I0d = 4.255*pow(10, 0.4*(M_sun - m0))*1e4; 
  // m0 - is face-on!

  double      Ld = 2*M_PI*I0d*h*h;
  Ld = Ld*correction;

  double    fact_md = MSUN*M_L_d;
  double     Mass_d = Ld*fact_md;
  double      fact1 = 2*Mass_d*GRAV / PARSEC;
  double fact_thick = fact1 / M_PI / z0;
  double  fact_thin = fact1 / h;

  /* bulge parameters convertions */

  qb_int = sqrt((qb_obs*qb_obs - cosi2)/(1 - cosi2));
  if (qb_obs==1) qb_int = 1;

  double   n_1 = 1 / nsersic;
  double   n_2 = 2*nsersic;

  double    r0 = reb / pow(bn(nsersic), nsersic);
  double fact2 = GRAV / PARSEC;
  double   I0b = 4.255*pow(10, 0.4*(M_sun - mu_eb))*exp(bn(nsersic))*1e4;

  double Lb_fact = 4*I0b*r0*r0*qb_obs;
  double      Lb = 2*M_PI*nsersic*gsl_sf_gamma(n_2)*I0b*r0*r0*qb_obs;

  Lb_fact = Lb_fact*correction;
  Lb = Lb*correction;
  double fact_mb = MSUN*M_L_b;
  double  Mass_b = Lb*fact_mb;

  /* halo parameters convertions */
  double vinf2, r200, facth2, facth1, M200, Fc, Mass_tot;
  if (hType == 0){ // isoterm halo
    vinf2 = vinf*vinf/1e4;
  }
  else{ // NFW halo
    r200 = v200*1e3 / (10 * Hz ); // r200 in kpc
    facth2 = v200*v200*v200*1e-1 / (10*Hz);
    facth1 = PARSEC / GRAV / MSUN;
    M200 = facth1*facth2; // in 10^10 M_sun  
    Fc = Fh(concentr);
    Mass_tot = Mass_d + Mass_b + M200;
  }

  double       md = Mass_d / Mass_tot;                     // TODO: place these lines to NFW or
  double       mb = Mass_b / Mass_tot;                     //  to isotermal halo section
  double   lim_mb = M_PI*nsersic*gsl_sf_gamma(n_2)/2;      //

  struct fun_root_params params_ri;
  params_ri.md = md;
  params_ri.mb = mb;
  params_ri.c = concentr;
  params_ri.d = h / r200;
  params_ri.rb0 = r0 / r200;
  params_ri.nsersic = nsersic;
  params_ri.qb_obs = qb_obs;
  params_ri.lim_mb = lim_mb;

  /* Compute velocities now */
  int i;
  double rr, rrc, ri, rh;

  if(hType==0){
    for(i=0; i < num_of_points; i++){
      rr = distances[i];
      rrc = rr / Rc;
      v_squared[i] = vinf2*(1.0 - atan(rrc)/rrc);
    }
  }
  else{
    if (includeAC==0){
      for(i=0; i < num_of_points; i++){
	rr = distances[i];
	rh = rr / r200;
	v_squared[i] = facth2*Fh(rh*concentr) / Fc / rr;
      }
    }
    else{
      for(i=0; i < num_of_points; i++){
	rr = distances[i];
	rh = rr / r200;
	params_ri.rf = rh;
	ri = fun_root((void*) &params_ri);
	v_squared[i] = facth2*Fh(ri*concentr) / Fc / rr;
      }
    }
  }
  return 0;
}
