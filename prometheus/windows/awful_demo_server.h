#pragma once
#include "../window_manager/window_manager.h"
#include "../state_replicator.h"

class awful_demo_server : public window {
	WINDOW_DEFINE(awful_demo_server, "Tools", "Awful Demo Server", true);

	inline void render() override {
		if (open_window()) {
			if (ImGui::Button("Start Server")) {
				state_replicator::start_server();
			}
			ImGui::Text("Relay connected: %s", state_replicator::is_connected ? "Yes" : "No");
			ImGui::TextWrapped("Experimental movement relay. Load the same map on every client. Combat and objectives are not synchronized.");
			ImGui::InputText("IP", _connect_to, sizeof(_connect_to));
			ImGui::InputInt("Port", &_port);
			if (ImGui::Button("Connect Server")) {
				if (_port >= 1 && _port <= 65535) state_replicator::connect(_connect_to, static_cast<unsigned short>(_port));
			}
			if (ImGui::Button("Disconnect / Stop Server")) state_replicator::disconnect();
		}
		ImGui::End();
	}

private:
	char _connect_to[32]{};
	int _port = 6969;
	//inline void preStartInitialize() override {}
	inline void initialize() override {
		strcpy(_connect_to, "127.0.0.1");
	}
};

WINDOW_REGISTER(awful_demo_server);
