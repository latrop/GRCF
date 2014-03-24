#include <math.h>
#include <gsl/gsl_sf_gamma.h>

/*********************************************************************/
/*********************************************************************/

double
  bn (double n)
{
return 2*n - 1.0 / 3.0 + (4.0 / 405.0 + 46.0 / 25515.0 / n) / n;
}
/*********************************************************************/
/*********************************************************************/

double
  bn_find (double x, void* params)
{
  struct bn_find_params *p
    = (struct bn_find_params *) params;

  double m = (p->n)*2;

  return gsl_sf_gamma_inc(x, m) - 0.5*gsl_sf_gamma(m);
}
/*********************************************************************/
/*********************************************************************/

double
  bn_find_deriv (double x, void* params)
{
  struct bn_find_params *p
    = (struct bn_find_params *) params;

  double m = (p->n)*2;

  return  gsl_sf_gamma_inc(x, m) - 0.5*gsl_sf_gamma(m);
}
/*********************************************************************/
/*********************************************************************/

double
  fb_integrate (double v, void* params)
{
  struct fb_integrate_params *p
    = (struct fb_integrate_params *)params;

  double nsersic = (p->nsersic);
  double       a = (p->a);
  double      n2 = 2.0*nsersic;

  return pow(v, nsersic-2)*exp(-1.0/v)/sqrt(1.0 - pow(v, n2)*a);
}
/*********************************************************************/
/*********************************************************************/

double
  dens3 (double a, void* params)
{
  struct dens3_params *p
    = (struct dens3_params *)params;

  double nsersic = (p->nsersic);

  double     n_1 = 1.0 / nsersic;
  double      n2 = 2*nsersic;

  double   x_right = pow(1.0 / a, n_1);

   gsl_function FUN;
   FUN.function = &fb_integrate;
   struct fb_integrate_params pi;

   pi.nsersic = nsersic;
   pi.a = a*a;

   FUN.params = &pi;

   gsl_integration_workspace* w =
     gsl_integration_workspace_alloc(100000);

   double rez;
   double rezerr;

   gsl_integration_qags(&FUN, 0, x_right, 0, 1e-7, 100000, w, &rez, &rezerr);

   gsl_integration_workspace_free (w);

return rez;
}
/*********************************************************************/
/*********************************************************************/

double
  dM (double a, void* params)
{
  struct dens3_params *p
    = (struct dens3_params *)params;

  double nsersic = (p->nsersic);

  double     n_1 = 1.0 / nsersic;
  double      n2 = 2*nsersic;

  double   x_right = pow(1.0 / a, n_1);

   gsl_function FUN;
   FUN.function = &fb_integrate;
   struct fb_integrate_params pi;

   pi.nsersic = nsersic;
   pi.a = a*a;

   FUN.params = &pi;

   gsl_integration_workspace* w = 
     gsl_integration_workspace_alloc(100000);

   double rez;
   double rezerr;

   gsl_integration_qags(&FUN, 0, x_right, 0, 1e-7, 100000, w, &rez, &rezerr);

   gsl_integration_workspace_free (w);

return rez*a*a;
}
/*********************************************************************/
/*********************************************************************/

double
  M_b (double x, void* params)
{
  struct dens3_params *p
    = (struct dens3_params *)params;

  double nsersic = (p->nsersic);

   gsl_function F;
   F.function = &dM;
   struct dens3_params pm;

   pm.nsersic = nsersic;

   F.params = &pm;

   gsl_integration_workspace* w =
     gsl_integration_workspace_alloc(100000);

   double rez;
   double rezerr;

   gsl_integration_qags(&F, 0, x, 0, 1e-7, 100000, w, &rez, &rezerr);

   gsl_integration_workspace_free (w);

return rez;
}
/*********************************************************************/
/*********************************************************************/

double
  dForceb (double a, void* params)
{
  struct dForceb_params *p
    = (struct dForceb_params *)params;

  double nsersic = (p->nsersic);
  double      qb = (p->qb);
  double      rr = (p->rr);

  double     n_1 = 1.0 / nsersic;
  double      n2 = 2*nsersic;
  double    eps2 = 1.0 - qb*qb;
  double     rr2 = rr*rr;

  double x_right = pow(1.0 / a, n_1);
  double      a2 = a*a;

   gsl_function FUN;
   FUN.function = &fb_integrate;
   struct fb_integrate_params pi;

   pi.nsersic = nsersic;
   pi.a = a*a;

   FUN.params = &pi;

   gsl_integration_workspace* w = 
     gsl_integration_workspace_alloc(100000);

   double rez;
   double rezerr;

   gsl_integration_qags(&FUN, 0, x_right, 0, 1e-7, 100000, w, &rez, &rezerr);

   gsl_integration_workspace_free (w);

return rez*a2 / sqrt(rr2 - a2*eps2);
}
/*********************************************************************/
/*********************************************************************/

double
  vb2 (double x, void* params)
{
  struct vb2_params *p
    = (struct vb2_params *)params;

  double nsersic = (p->nsersic);
  double      qb = (p->qb);

   gsl_function F;
   F.function = &dForceb;
   struct dForceb_params pi;

   pi.nsersic = nsersic;
   pi.qb = qb;
   pi.rr = x;

   F.params = &pi;

   gsl_integration_workspace* w =
     gsl_integration_workspace_alloc(100000);

   double rez;
   double rezerr;

   gsl_integration_qags(&F, 0, x, 0, 1e-7, 100000, w, &rez, &rezerr);

   gsl_integration_workspace_free (w);

return rez;
}
/*********************************************************************/
/*********************************************************************/

double
  dM_sph (double u, void* params)
{
  struct dM_sph_params *p
    = (struct dM_sph_params *)params;

  double nsersic = (p->nsersic);
  double       a = (p->x);

  double     n_1 = 1.0 / nsersic;
  double     n21 = 2*nsersic + 1;

  double       z = pow((a / u),n_1);

return u*u*(gsl_sf_gamma(n21) - gsl_sf_gamma_inc(n21,z)) / sqrt(1 - u*u);
}
/***********************************************************************/
/***********************************************************************/

double
  M_bsph (double x, void* params)
{
  struct dens3_params *p
    = (struct dens3_params *)params;

  double nsersic = (p->nsersic);

   gsl_function F;
   F.function = &dM_sph;
   struct dM_sph_params pi;

   pi.nsersic = nsersic;
         pi.x = x;

   F.params = &pi;

   gsl_integration_workspace* w =
     gsl_integration_workspace_alloc(100000);

   double rez;
   double rezerr;

   gsl_integration_qags(&F, 0, 1, 0, 1e-7, 100000, w, &rez, &rezerr);

   gsl_integration_workspace_free (w);

return rez;
}
