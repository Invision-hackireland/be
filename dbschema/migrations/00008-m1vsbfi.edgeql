CREATE MIGRATION m1vsbfiupqfksuyhiapgrhr3sl7pwkvi5tn244iro32kmnmsjzkx2a
    ONTO m1akk3bmu7krqi74n5jmjiastt67izye5s3dpjg22retjymytdqtka
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
  ALTER TYPE default::User {
      ALTER LINK rooms {
          ON TARGET DELETE ALLOW;
      };
  };
};
