CREATE MIGRATION m1lna5bix4n4bzf2shsqfi4w2gndjxbx2fxsgz2nytwngqcqyuxmba
    ONTO m1zj6rxdnyaqoeadik5mlopdqddrnw7bhcbg67hrshrqw5iercx54q
{
  ALTER TYPE default::Logs {
      DROP PROPERTY rule_tag;
  };
  ALTER TYPE default::Logs RENAME TO default::LogEntry;
  ALTER TYPE default::LogEntry {
      CREATE REQUIRED LINK camera: default::Camera {
          SET REQUIRED USING (<default::Camera>{});
      };
  };
  CREATE TYPE default::Rule EXTENDING default::Base {
      CREATE REQUIRED PROPERTY description: std::str;
      CREATE OPTIONAL PROPERTY rooms: array<std::str>;
      CREATE REQUIRED PROPERTY shared: std::bool;
  };
  ALTER TYPE default::LogEntry {
      CREATE REQUIRED LINK rule: default::Rule {
          SET REQUIRED USING (<default::Rule>{});
      };
  };
  ALTER TYPE default::RuleSet {
      DROP PROPERTY rules;
  };
  ALTER TYPE default::RuleSet {
      CREATE MULTI LINK rules: default::Rule;
  };
};
