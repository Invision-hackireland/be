CREATE MIGRATION m1akk3bmu7krqi74n5jmjiastt67izye5s3dpjg22retjymytdqtka
    ONTO m15aqfmut4mglgtqvdmigb2dngjkfb25r2yf7ki5mowz2etqp3kbia
{
  ALTER TYPE default::Camera {
      CREATE REQUIRED PROPERTY chunks: array<std::str> {
          SET default := (<array<std::str>>[]);
      };
  };
};
