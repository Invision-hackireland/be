CREATE MIGRATION m1n33opforce4zvezlqp3ei5ax6jrogvbjtfj4isghswc6htoi6zoq
    ONTO m1s7zpqhvkkmjdgcnbm66eun3fvwmdhsnd6yqw53n43honq5rntosq
{
  ALTER TYPE default::User {
      ALTER LINK rooms {
          ON TARGET DELETE ALLOW;
      };
  };
};
