CREATE MIGRATION m1344fpyn7v25lyr6gffwkqpap5aiqzkrmq5lxo3sm6k27wp7hxr6q
    ONTO m14viesnuwtsrr5eorf2kv5rsvn6qzj35efaikbalt4jb4syhpbwxa
{
  ALTER TYPE default::Camera {
      DROP PROPERTY room;
  };
  CREATE TYPE default::Room EXTENDING default::Base {
      CREATE REQUIRED PROPERTY name: std::str;
  };
  ALTER TYPE default::Camera {
      CREATE REQUIRED LINK room: default::Room {
          SET REQUIRED USING (<default::Room>{});
      };
  };
  ALTER TYPE default::Rule {
      DROP PROPERTY rooms;
  };
  ALTER TYPE default::Rule {
      CREATE OPTIONAL MULTI LINK rooms: default::Room;
  };
};
