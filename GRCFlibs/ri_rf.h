struct fun_root_params
{
   double md,  mb, c, d, rb0, nsersic, qb_obs, lim_mb, rf;
};

double fun_ri (double x, void *params);
double fun_ri_deriv (double x, void *params);
void fun_ri_fdf (double x, void *params,
double *y, double *dy);
double fun_root (void *params);
