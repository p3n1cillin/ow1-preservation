#include "ngdp.h"
#include "base/http.h"
#include <iostream>

// Authored for this project; uses an external BlizzGet checkout without vendoring it.
// This prerequisite probe fetches public metadata/config only, not game content.
int main(int argc, char** argv) {
    try {
        NGDP::NGDP client("pro");
        if (!client.setRegion("eu")) { std::cerr << "EU metadata unavailable\n"; return 1; }
        const auto version = client.version();
        std::cout << "CURRENT_VERSION=" << version->version << "\nCURRENT_BUILD=" << version->build
                  << "\nCURRENT_CDN=" << version->cdn << '\n';
        auto cdn_file = client.load(version->cdn);
        if (!cdn_file) { std::cerr << "CDN config unavailable\n"; return 1; }
        const auto config = NGDP::ParseConfig(cdn_file);
        const auto builds = config.find("builds");
        std::cout << "ADVERTISED_BUILDS=" << (builds == config.end() ? "(none)" : builds->second) << '\n';
        const std::string hash = argc > 1 ? argv[1] : version->build;
        if (hash.size() != 32 || hash.find_first_not_of("0123456789abcdef") != std::string::npos) return 2;
        HttpRequest request(client.geturl(hash));
        if (!request.send()) { std::cerr << "Build config request failed\n"; return 1; }
        std::cout << "BUILD_CONFIG_HTTP_STATUS=" << request.status() << '\n';
        if (request.status() != 200) return 3;
        for (const auto& entry : NGDP::ParseConfig(request.response()))
            std::cout << entry.first << " = " << entry.second << '\n';
        return 0;
    } catch (const std::exception& error) { std::cerr << error.what() << '\n'; return 1; }
}
