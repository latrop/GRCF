struct fb_integrate_params{double nsersic, a;};
double fb_integrate (double v, void* params);

double bn(double n);

struct dens3_params {double nsersic;};
struct dForceb_params {double nsersic, qb, rr;};
struct vb2_params {double nsersic, qb;};

double dens3 (double a, void* params);
double dM (double a, void* params);
double Mass_b (double x, void* params);
double dForceb (double a, void* params);
double vb2 (double x, void* params);

struct dM_sph_params {double nsersic, x;};

double dM_sph (double u, void* params);
double Mass_b (double x, void* params);

struct bn_find_params {double n;};
double bn_find (double x, void* params);
double bn_find_deriv (double x, void* params);
