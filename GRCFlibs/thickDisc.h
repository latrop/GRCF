struct fdz_integrate_params {double z0, u, r;};
struct intz_params {double z0, r;};
struct dForced_params {double z0, r;};
struct vd2_params {double z0;};

double fdz_integrate (double z, void* params);
double intz (double u, void* params);
double dForced (double u, void* params);
double vd2 (double r, double z0);
