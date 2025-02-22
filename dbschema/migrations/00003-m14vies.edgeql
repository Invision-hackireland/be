CREATE MIGRATION m14viesnuwtsrr5eorf2kv5rsvn6qzj35efaikbalt4jb4syhpbwxa
    ONTO m1lna5bix4n4bzf2shsqfi4w2gndjxbx2fxsgz2nytwngqcqyuxmba
{
  ALTER TYPE default::Rule {
      ALTER PROPERTY description {
          RENAME TO text;
      };
  };
  ALTER TYPE default::RuleSet {
      DROP LINK rules;
  };
  ALTER TYPE default::User {
      DROP LINK ruleset;
  };
  DROP TYPE default::RuleSet;
  ALTER TYPE default::User {
      CREATE REQUIRED MULTI LINK rules: default::Rule {
          SET REQUIRED USING (<default::Rule>{});
      };
  };
};
