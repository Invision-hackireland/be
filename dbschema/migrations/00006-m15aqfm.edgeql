CREATE MIGRATION m15aqfmut4mglgtqvdmigb2dngjkfb25r2yf7ki5mowz2etqp3kbia
    ONTO m1ksee55orh36ge33us7ad3nuclh5wd3huftdqho3mti5ag7dae4eq
{
  ALTER TYPE default::Base {
      ALTER ANNOTATION std::description := 'Base abstract type for other types to inherit.';
  };
  ALTER TYPE default::User {
      ALTER LINK rooms {
          RESET OPTIONALITY;
      };
      ALTER LINK rules {
          RESET OPTIONALITY;
      };
  };
};
