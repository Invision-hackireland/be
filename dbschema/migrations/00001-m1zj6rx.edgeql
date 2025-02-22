CREATE MIGRATION m1zj6rxdnyaqoeadik5mlopdqddrnw7bhcbg67hrshrqw5iercx54q
    ONTO initial
{
  CREATE ABSTRACT TYPE default::Base {
      CREATE ANNOTATION std::description := 'Base \n        abstract type for other types to inherit.';
      CREATE PROPERTY date_created: std::datetime {
          SET default := (std::datetime_current());
      };
  };
  CREATE TYPE default::Logs EXTENDING default::Base {
      CREATE REQUIRED PROPERTY description: std::str;
      CREATE REQUIRED PROPERTY rule_tag: std::str;
      CREATE REQUIRED PROPERTY time: std::datetime;
  };
  CREATE TYPE default::Camera EXTENDING default::Base {
      CREATE MULTI LINK logs: default::Logs;
      CREATE REQUIRED PROPERTY ip_address: std::str {
          CREATE CONSTRAINT std::exclusive;
      };
      CREATE REQUIRED PROPERTY room: std::str;
  };
  CREATE TYPE default::RuleSet EXTENDING default::Base {
      CREATE MULTI PROPERTY rules: std::str;
  };
  CREATE TYPE default::User EXTENDING default::Base {
      CREATE MULTI LINK camera: default::Camera;
      CREATE REQUIRED LINK ruleset: default::RuleSet;
      CREATE REQUIRED PROPERTY email: std::str {
          CREATE CONSTRAINT std::exclusive;
      };
      CREATE REQUIRED PROPERTY firstname: std::str;
  };
};
