CREATE MIGRATION m1s7zpqhvkkmjdgcnbm66eun3fvwmdhsnd6yqw53n43honq5rntosq
    ONTO m15aqfmut4mglgtqvdmigb2dngjkfb25r2yf7ki5mowz2etqp3kbia
{
  ALTER TYPE default::Camera {
      ALTER LINK room {
          ON TARGET DELETE ALLOW;
      };
  };
  ALTER TYPE default::Rule {
      ALTER LINK rooms {
          ON TARGET DELETE ALLOW;
      };
  };
};
