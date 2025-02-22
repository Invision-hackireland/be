CREATE MIGRATION m1ksee55orh36ge33us7ad3nuclh5wd3huftdqho3mti5ag7dae4eq
    ONTO m1344fpyn7v25lyr6gffwkqpap5aiqzkrmq5lxo3sm6k27wp7hxr6q
{
  ALTER TYPE default::User {
      CREATE REQUIRED MULTI LINK rooms: default::Room {
          SET REQUIRED USING (<default::Room>{});
      };
  };
};
