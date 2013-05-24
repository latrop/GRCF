#include <stdio.h>
#include <math.h>
#include <gsl/gsl_sf_ellint.h>
#include <gsl/gsl_integration.h>
#include "thickDisc.h"

/*############################################################################*/



double
  ell (double x)
{

  double k = x;
  gsl_mode_t mode = GSL_PREC_DOUBLE;
  double var = (gsl_sf_ellint_Kcomp(k, mode) - gsl_sf_ellint_Ecomp(k, mode));

  return var;
}


double
  fdz_integrate (double z, void* params)
{
  struct fdz_integrate_params *par
    = (struct fdz_integrate_params *)params;

  double z0 = (par->z0);
  double  u = (par->u);
  double  r = (par->r);

  double  x = (r*r + u*u + z*z) / (2.0*r*u);
  double x2 = x*x;
  double  p = x - sqrt(x2 - 1);
  double  var = 1.0 / cosh(z/z0);
  double fz = var*var;

  if (p > 0.0001) return ell(p)*fz / sqrt(p);
  else
   {
    double m2 = p*p / 8.0;
    double m = sqrt(m2);
    return 2.0*M_PI*m2*m*(1.0 + 3.0*m2)*fz*M_SQRT1_2*sqrt(M_SQRT1_2);
   };
}



double
  intz (double u, void* params)
{
  struct intz_params *p
    = (struct intz_params *)params;

  double z0 = (p->z0);
  double  r = (p->r);

   gsl_function FUN;
   FUN.function = &fdz_integrate;
   struct fdz_integrate_params pi;
   pi.z0 = z0;
   pi.u = u;
   pi.r = r;
   FUN.params = &pi;

   gsl_integration_workspace* w =
     gsl_integration_workspace_alloc(100000);

  double rez;
  double rezerr;

   gsl_integration_qagiu(&FUN, 0, 0, 1e-6, 100000, w, &rez, &rezerr);

   gsl_integration_workspace_free (w);

   return rez;
}



double
  dForced (double u, void* params)
{
  struct dForced_params *p
    = (struct dForced_params *)params;

  double z0 = (p->z0);
  double  r = (p->r);

   gsl_function FUN;
   FUN.function = &intz;
   struct intz_params pi;
   pi.z0 = z0;
   pi.r = r;
   FUN.params = &pi;

   return intz(u, (void*) &pi)*exp(-u)*sqrt(u);
}



double
  vd2 (double r, double z0)
{

   gsl_function F;
   F.function = &dForced;
   struct dForced_params pi;
   pi.z0 = z0;
   pi.r = r;
   F.params = &pi;

   gsl_integration_workspace* w =
     gsl_integration_workspace_alloc(100000);

  double rez;
  double rezerr;

   gsl_integration_qagiu(&F, 0, 0, 1e-6, 100000, w, &rez, &rezerr);

   gsl_integration_workspace_free (w);
   return rez*sqrt(r);
}
