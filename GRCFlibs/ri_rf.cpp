#include <math.h>

/*********************************************************************/
/*********************************************************************/

double
  fun_ri (double x, void *params)
{
   struct fun_root_params *p
     = (struct fun_root_params *) params;

   double  md = p->md;
   double  mb = p->mb;
   double   c = p->c;
   double   d = p->d;
   double rb0 = p->rb0;
   double nsersic = p->nsersic;
   double  qb_obs = p->qb_obs;
   double  lim_mb = p->lim_mb;
   double  rf = p->rf;

   double xc = x*c;

   gsl_function F;
   F.function = &M_b;
   struct dens3_params pm;

   pm.nsersic = nsersic;
   F.params = &pm;

if(qb_obs < 0.99)
   {return rf*((md*M_d(rf/d) + mb*M_b(rf/rb0, (void*) &pm)/lim_mb)\
                             *Fh(c) / Fh(xc) + 1.0 - md - mb) - x;}
else
   {return rf*((md*M_d(rf/d) + mb*M_bsph(rf/rb0, (void*) &pm)/lim_mb)\
                             *Fh(c) / Fh(xc) + 1.0 - md - mb) - x;}
}
/*********************************************************************/
/*********************************************************************/

double
  fun_ri_deriv (double x, void *params)
{
   struct fun_root_params *p
     = (struct fun_root_params *) params;

   double md = p->md;
   double mb = p->mb;
   double  c = p->c;
   double  d = p->d;
   double rb0 = p->rb0;
   double nsersic = p->nsersic;
   double  qb_obs = p->qb_obs;
   double  lim_mb = p->lim_mb;
   double rf = p->rf;

   double xc = x*c;

   gsl_function F;
   F.function = &M_b;
   struct dens3_params pm;

   pm.nsersic = nsersic;
   F.params = &pm;

if(qb_obs < 0.99)
   {return - rf*(md*M_d(rf/d) + mb*M_b(rf/rb0, (void*) &pm)/lim_mb)\
               *Fh(c)*c*Fhdf(xc) / Fh(xc) / Fh(xc) - 1.0;}
else
   {return - rf*(md*M_d(rf/d) + mb*M_bsph(rf/rb0, (void*) &pm)/lim_mb)\
               *Fh(c)*c*Fhdf(xc) / Fh(xc) / Fh(xc) - 1.0;}
}
/*********************************************************************/
/*********************************************************************/

void
  fun_ri_fdf (double x, void *params,
      double *y, double *dy)
{
   struct fun_root_params *p
     = (struct fun_root_params *) params;

   double md = p->md;
   double mb = p->mb;
   double  c = p->c;
   double  d = p->d;
   double rb0 = p->rb0;
   double nsersic = p->nsersic;
   double  qb_obs = p->qb_obs;
   double  lim_mb = p->lim_mb;
   double rf = p->rf;

   double xc = x*c;

   gsl_function F;
   F.function = &M_b;
   struct dens3_params pm;

   pm.nsersic = nsersic;
   F.params = &pm;

if(qb_obs < 0.99)
{*y = rf*((md*M_d(rf/d) + mb*M_b(rf/rb0, (void*) &pm)/lim_mb)\
                       *Fh(c) / Fh(xc) + 1.0 - md) - x;
*dy = - rf*(md*M_d(rf/d) + mb*M_b(rf/rb0, (void*) &pm)/lim_mb)\
          *Fh(c)*c*Fhdf(xc) / Fh(xc) / Fh(xc) - 1.0;}
else
{*y = rf*((md*M_d(rf/d) + mb*M_bsph(rf/rb0, (void*) &pm)/lim_mb)\
                       *Fh(c) / Fh(xc) + 1.0 - md) - x;
*dy = - rf*(md*M_d(rf/d) + mb*M_bsph(rf/rb0, (void*) &pm)/lim_mb)\
          *Fh(c)*c*Fhdf(xc) / Fh(xc) / Fh(xc) - 1.0;}
}
/*********************************************************************/
/*********************************************************************/

double
  fun_root (void *params)
{
   int status;
   int iter = 0, max_iter = 100;
   int i;
   const gsl_root_fdfsolver_type *T;
   gsl_root_fdfsolver *s;
   double x0, x, y;

   gsl_function_fdf FDF_ri;
   struct fun_root_params *p 
     = (struct fun_root_params *) params;

   FDF_ri.f = &fun_ri;
   FDF_ri.df = &fun_ri_deriv;
   FDF_ri.fdf = &fun_ri_fdf;
   FDF_ri.params = p;

   x = p->rf; 

   T = gsl_root_fdfsolver_secant;
   s = gsl_root_fdfsolver_alloc (T);
   gsl_root_fdfsolver_set (s, &FDF_ri, x);

   do
     {
    iter++;
    status = gsl_root_fdfsolver_iterate (s);
    x0 = x;
    x = gsl_root_fdfsolver_root (s);
    status = gsl_root_test_delta (x, x0, 0, 0.0000001);

//        printf ("%5d %10.7f %10.7f\n",
//                iter, x, x - x0);
     }
   while (status == GSL_CONTINUE && iter < max_iter);

//   printf ("%5d %10.7f %10.7f %10.7f\n",
//      iter, p->rf, x, x - x0);

   y = x;
   gsl_root_fdfsolver_free (s);

   return y;
}
