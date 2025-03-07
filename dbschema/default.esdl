module default {

    abstract type Base {
        annotation description := "Base abstract type for other types to inherit.";
        property date_created -> datetime {
            default := datetime_current();
        }
    }

    type Room extending Base {
        required property name -> str;
    }

    type LogEntry extending Base {
        required property time -> datetime;
        required property description -> str;
        required link rule -> Rule;
        required link camera -> Camera;
        # TODO: Add footage link
    }

    type Camera extending Base {
        required property ip_address -> str {
            constraint exclusive;
        }
        required link room -> Room{
            on target delete allow;
        };
        multi link logs -> LogEntry;
        required property chunks -> array<str> {
            default := <array<str>>[];
        }
    }

    type Rule extending Base {
        required property text -> str;
        required property shared -> bool;
        optional multi link rooms -> Room {
            on target delete allow;
        };
    }

    type User extending Base {
        required property email -> str {
            constraint exclusive;
        }
        required property firstname -> str;
        multi link camera -> Camera;
        multi link rules -> Rule;
        multi link rooms -> Room{
            on target delete allow;
        };
    }
}
