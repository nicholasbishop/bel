@0xf40d4f744cafb877;

struct Size2u32 {
  width @0 :UInt32;
  height @1 :UInt32;
}

struct MsgCreateWindow {
  size @0 :Size2u32;
  title @1 :Text;
}

# union Msg {
# create_window @0 :MsgCreateWindow;
# }
interface Gpu {
}
