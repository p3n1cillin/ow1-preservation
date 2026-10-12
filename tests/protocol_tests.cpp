#include "fixtures.h"
#include "server/relay.h"
#include <limits>

using namespace preservation;
using namespace preservation::legacy;
int main() {
    try {
        check(static_cast<int>(Type::AssignPlayerID) == 5, "wire IDs changed");
        auto message = position_fixture("p");
        check(decode(encode(message)) == message, "BSON movement roundtrip");
        check(decode("garbage").is_null(), "reject malformed BSON");
        check(decode(std::string(max_message_bytes + 1, 'x')).is_null(), "bound message size");
        check(!valid({}), "reject empty object");
        check(!valid({{"type", 99}, {"player_id", "p"}}), "reject unknown type");
        check(!valid({{"type", 2}, {"player_id", "p"}, {"data", {}}}), "require movement schema");
        message["data"]["220"]["x"] = std::numeric_limits<double>::infinity();
        check(!valid(message), "reject nonfinite movement");
        message = position_fixture("p"); message["data"]["1A0"] = INT64_MAX;
        check(!valid(message), "reject integer truncation");
        message = position_fixture("p"); message["data"]["244"] = -1;
        check(!valid(message), "reject negative unsigned field");
        message = position_fixture("p"); message["data"].erase("250");
        check(!valid(message), "require every serialized field");
        message = hero_fixture("p", 0); check(!valid(message), "reject zero hero");
        message["heroid"] = std::uint64_t(0); check(!valid(message), "reject unsigned zero hero");
        message = join_fixture("p"); message["name"] = std::string(65, 'a');
        check(!valid(message), "bound name");
        // Independently specified BSON document: {player_id: "p", type: int32(5)}.
        const unsigned char golden[] = {0x20,0,0,0, 2,'p','l','a','y','e','r','_','i','d',0,
            2,0,0,0,'p',0, 0x10,'t','y','p','e',0, 5,0,0,0, 0};
        check(decode({reinterpret_cast<const char*>(golden), sizeof(golden)}) == event(Type::AssignPlayerID,"p"), "golden BSON interoperability");

        Relay relay(2);
        auto r = relay.open("a"); check(r.accepted && r.deliveries.size() == 1, "assign ID");
        check(!relay.open("a").accepted, "reject duplicate connection");
        check(relay.open("b").accepted, "second connection");
        check(!relay.open("c").accepted, "capacity limit");
        check(!relay.receive("a", encode(hero_fixture("a"))).accepted, "require join before hero");
        check(!relay.receive("a", encode(join_fixture("a")), false).accepted, "require binary");
        check(relay.receive("a", encode(join_fixture("spoof"))).accepted, "join a");
        check(!relay.receive("a", encode(join_fixture("a"))).accepted, "no duplicate join");
        check(!relay.receive("a", encode(event(Type::AssignPlayerID,"a"))).accepted, "server-only message");
        check(!relay.receive("a", encode(position_fixture("a"))).accepted, "require hero before position");
        check(relay.receive("a", encode(hero_fixture("spoof",1))).accepted, "select hero");
        check(!relay.receive("a", encode(position_fixture("a",-1))).accepted, "drop uninitialized frame");
        check(relay.receive("a", encode(position_fixture("a",4,12))).accepted, "movement stored");
        r = relay.receive("b", encode(join_fixture("b")));
        check(r.accepted && r.deliveries.size() == 4, "late join gets join hero movement, peers get join");
        check(decode(r.deliveries[0].bytes).at("player_id") == "a", "socket controls identity");
        check(decode(r.deliveries[2].bytes).at("data").at("220").at("x") == 12, "meaningful state replay");
        r = relay.receive("a", encode(hero_fixture("b",2)));
        check(r.accepted && decode(r.deliveries.at(0).bytes).at("player_id") == "a", "cannot impersonate peer");
        check(relay.close("b").accepted && relay.open("b").accepted, "reconnect slot released");
        r = relay.receive("b", encode(join_fixture("b")));
        check(r.deliveries.size() == 3 && decode(r.deliveries[1].bytes).at("heroid") == 2, "latest hero replaces cached selection and invalidates old movement");
        r = relay.close("a");
        check(r.accepted && r.deliveries.size() == 1 && decode(r.deliveries[0].bytes).at("type") == 4, "leave broadcast");
        check(!relay.close("a").accepted, "close idempotent without second leave");
        check(!relay.receive("a", encode(join_fixture("a"))).accepted, "closed identity rejected");
        check(relay.receive("b", encode(event(Type::LeaveInstance,"b"))).accepted && relay.size() == 0, "explicit leave");
        Relay full;
        for (int i=0;i<12;++i) check(full.open(std::to_string(i)).accepted, "twelve slots");
        check(!full.open("overflow").accepted, "thirteenth denied");
        std::cout << "PASS: protocol schema, BSON, lifecycle, identity, late join, capacity\n";
        return 0;
    } catch (const std::exception& error) { std::cerr << error.what() << '\n'; return 1; }
}
