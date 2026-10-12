#pragma once
#include <nlohmann/json.hpp>
#include "entity_admin.h"
#include <mutex>
#include "MovementState.h"
#include <ixwebsocket/IXWebSocket.h>
#include <ixwebsocket/IXWebSocketMessage.h>
#include <ixwebsocket/IXWebSocketServer.h>
#include <map>
#include <atomic>
#include "../server/relay.h"

class state_replicator {
public:
	typedef std::string playerid;
	class MsgBase {
	public:
		using MessageType = preservation::legacy::Type;
		MessageType type;

	protected:
		MsgBase(MessageType typ) : type(typ) {}
		virtual void please_be_polymorphic() {}
	};

	class NoneMessage : public MsgBase {
	public:
		NoneMessage() : MsgBase(MessageType::None) {}
	};

	class ChangeHeroMessage : public MsgBase {
	public:
		ChangeHeroMessage() : MsgBase(MessageType::ChangeHero) {}

		playerid player_id;
		__int64 heroid{};
		__int64 skinid{};

		NLOHMANN_DEFINE_TYPE_INTRUSIVE(ChangeHeroMessage, type, player_id, heroid, skinid);
	};

	class PositionUpdateMessage : public MsgBase {
	public:
		PositionUpdateMessage() : MsgBase(MessageType::PositionUpdate) {}

		playerid player_id;
		nlohmann::json data; //serialized MovementState

		NLOHMANN_DEFINE_TYPE_INTRUSIVE(PositionUpdateMessage, type, player_id, data);
	};

	class JoinInstanceMessage : public MsgBase {
	public:
		JoinInstanceMessage() : MsgBase(MessageType::JoinInstance) {}

		playerid player_id;
		std::string name;
		
		NLOHMANN_DEFINE_TYPE_INTRUSIVE(JoinInstanceMessage, type, player_id, name);
	};

	class LeaveInstanceMessage : public MsgBase {
	public:
		LeaveInstanceMessage() : MsgBase(MessageType::LeaveInstance) {}

		playerid player_id;

		NLOHMANN_DEFINE_TYPE_INTRUSIVE(LeaveInstanceMessage, type, player_id);
	};

	class AssignPlayerIDMessage : public MsgBase {
	public:
		AssignPlayerIDMessage() : MsgBase(MessageType::AssignPlayerID) {}

		playerid player_id;

		NLOHMANN_DEFINE_TYPE_INTRUSIVE(AssignPlayerIDMessage, type, player_id);
	};

	static inline std::atomic_bool is_connected = false;
	static playerid get_local_playerid();

	static void start_server();
	static void connect(std::string ip_addr, unsigned short port = 6969);
	static void disconnect();
	static std::shared_ptr<MsgBase> get_outstanding_message(); //returns NoneMessage if empty
	static void emplace_hero_update(ChangeHeroMessage msg);
	static void emplace_positon_update(MovementState* state);
private:
	static void network_init();
	static inline std::atomic_bool _is_server = false;
	static inline ix::WebSocket _ws{};
	static inline ix::WebSocketServer _wss{6969, "127.0.0.1"};
	static inline std::once_flag _network_init{};
	static void ws_client_callback(const ix::WebSocketMessagePtr&);
	static void ws_server_callback(std::shared_ptr<ix::ConnectionState>, ix::WebSocket&, const ix::WebSocketMessagePtr&);
	static void push_message(std::shared_ptr<MsgBase> msg);
	static std::vector<std::uint8_t> serialize_message(MsgBase* msg);
	static std::shared_ptr<MsgBase> deserialize_message(nlohmann::json input);
	static void deliver(const preservation::RelayResult& result);
	static void send_local(const std::vector<std::uint8_t>& bytes);

	static inline std::mutex _outstanding_messages_mut{};
	static inline std::mutex _local_state_mut{};
	static inline playerid _local_playerid{};
	static inline std::mutex _relay_mut{};
	static inline preservation::Relay _relay{};
	static inline std::map<playerid, ix::WebSocket*> _sockets{};
	static inline std::vector<std::shared_ptr<MsgBase>> _outstanding_messages{}; //OUT: Updates from other clients / servers... At this point we dont care if its a server or client really
	//static inline std::vector<nlohmann::json> _local_position_updates{}; //IN: Local Position updates to be sent
	static inline ChangeHeroMessage _local_hero{};
};
