@0xb0cabe68e690610c;

# We use capnproto for defining, serializing, and deserializing
# messages, but not for RPC currently.

struct UpdateBuffer {
    uid @0 :Text;
    array @1 :Data;
}

struct Attribute {
    key @0 :Text;
    buffer @1 :Text;
    gltype @2 :Text;
    normalized @3 :Bool;
    offset @4 :UInt64;
    stride @5 :UInt64;
}

struct UpdateDrawCommand {
    uid @0 :Text;
    material @1 :Text;
    attributes @2 :List(Attribute);
}

struct Message {
    union {
        wndUpdateBuffer @0 :UpdateBuffer;
        wndUpdateDrawCommand @1 :UpdateDrawCommand;
    }
}
