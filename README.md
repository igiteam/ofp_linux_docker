# ofp_linux_docker

# Operation Flashpoint Linux Server

🔄 Complete System Architecture

┌─────────────────────────────────────────────────────────────────────────────┐
│ YOUR INFRASTRUCTURE │
├─────────────────────────────────────────────────────────────────────────────┤
│ │
│ ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐ │
│ │ PufferPanel │ │ OpenSpy │ │ ofpigi.com │ │
│ │ (Game Manager) │────▶│ (Master Server) │◀────│ (Server Browser)│ │
│ │ │ │ │ │ │ │
│ │ wine.ofpigi.com │ │ wine.ofpigi.com │ │ ofpigi.com │ │
│ │ /pufferpanel │ │ /openspy │ │ │ │
│ └────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘ │
│ │ │ │ │
│ │ Creates & Deploys │ Reports to │ Displays │
│ ▼ ▼ ▼ │
│ ┌──────────────────────────────────────────────────────────────────┐ │
│ │ OFP Docker Containers │ │
│ │ ┌────────────────┐ ┌────────────────┐ ┌────────────────┐ │ │
│ │ │ ofp-server-1 │ │ ofp-server-2 │ │ ofp-server-3 │ │ │
│ │ │ Port: 2302 │ │ Port: 2303 │ │ Port: 2304 │ │ │
│ │ │ reportingIP: │ │ reportingIP: │ │ reportingIP: │ │ │
│ │ │ wine.ofpigi.com│ │ wine.ofpigi.com│ │ wine.ofpigi.com│ │ │
│ │ └────────────────┘ └────────────────┘ └────────────────┘ │ │
│ └──────────────────────────────────────────────────────────────────┘ │
│ │
└─────────────────────────────────────────────────────────────────────────────┘

📦 Step 1: OFP Linux Docker Container

Dockerfile:

FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
 wget \
 gzip \
 lib32stdc++6 \
 lib32gcc-s1 \
 lib32z1 \
 && rm -rf /var/lib/apt/lists/\*

RUN useradd -m -s /bin/bash ofp

WORKDIR /home/ofp/server

RUN wget -q ftp://ftp.ofpisnotdead.com/oflinux/ofp-server-1.96.shar.gz && \
 gunzip ofp-server-1.96.shar.gz && \
 sh ofp-server-1.96.shar && \
 rm ofp-server-1.96.shar && \
 chmod +x server

RUN cat > server.cfg << 'EOF'
hostname = "${HOSTNAME}";
password = "${PASSWORD}";
passwordAdmin = "${ADMIN_PASSWORD}";
reportingIP = "${REPORTING_IP}";
maxPlayers = ${MAX_PLAYERS};
kickDuplicate = 1;
equalModRequired = 0;
voteMissionPlayers = 3;
voteThreshold = 0.51;

class Missions {
class Mission1 {
template = "${DEFAULT_MISSION}";
cadetMode = 1;
};
};
EOF

RUN cat > entrypoint.sh << 'EOF'
#!/bin/bash
sed -i "s/\${HOSTNAME}/$HOSTNAME/g" server.cfg
sed -i "s/\${PASSWORD}/$PASSWORD/g" server.cfg
sed -i "s/\${ADMIN_PASSWORD}/$ADMIN_PASSWORD/g" server.cfg
sed -i "s/\${REPORTING_IP}/$REPORTING_IP/g" server.cfg
sed -i "s/\${MAX_PLAYERS}/$MAX_PLAYERS/g" server.cfg
sed -i "s/\${DEFAULT_MISSION}/$DEFAULT_MISSION/g" server.cfg
./server -config=server.cfg -port=2302 -netlog
EOF

RUN chmod +x entrypoint.sh && chown -R ofp:ofp /home/ofp

EXPOSE 2302-2306/udp

USER ofp

CMD ["./entrypoint.sh"]

Build and push:

docker build -t ghcr.io/igiteam/ofp-server:latest .
docker push ghcr.io/igiteam/ofp-server:latest

📝 Step 2: PufferPanel Template

{
"type": "docker",
"display": "Operation Flashpoint: Project IGI",
"icon": "ofp",
"description": "OFP Linux server that reports to igiteam OpenSpy master",
"install": [
{
"type": "dockerpull",
"image": "ghcr.io/igiteam/ofp-server:latest"
}
],
"run": {
"command": "docker run -d --name ${server_id} -p ${port}:2302/udp -e HOSTNAME=\"${hostname}\" -e PASSWORD=\"${password}\" -e ADMIN_PASSWORD=\"${admin_password}\" -e REPORTING_IP=\"${reporting_ip}\" -e MAX_PLAYERS=${max_players} -e DEFAULT_MISSION=\"${default_mission}\" ghcr.io/igiteam/ofp-server:latest",
"stop": "docker stop ${server_id} && docker rm ${server_id}"
},
"data": {
"hostname": {
"display": "Server Name",
"default": "Project IGI - OFP Remake",
"required": true
},
"port": {
"type": "integer",
"value": 2302,
"display": "Game Port",
"required": true,
"userEdit": false
},
"password": {
"type": "string",
"value": "",
"display": "Server Password",
"required": false
},
"admin_password": {
"type": "string",
"value": "changeme",
"display": "Admin Password",
"required": true
},
"max_players": {
"type": "integer",
"value": 32,
"display": "Max Players",
"required": true
},
"default_mission": {
"type": "string",
"value": "1-8_D_Paintball.ABEL",
"display": "Default Mission",
"required": true
},
"reporting_ip": {
"type": "string",
"value": "wine.ofpigi.com",
"display": "Master Server (OpenSpy)",
"description": "Where the server reports its status - set to your OpenSpy instance",
"required": true,
"userEdit": true
}
}
}

🔗 Step 3: How the Reporting Works

In server.cfg:
reportingIP = "wine.ofpigi.com";

This sends heartbeat packets to wine.ofpigi.com:2303 (game port + 1)

THE FLOW:

1. PufferPanel creates OFP container with reporting_ip="wine.ofpigi.com"
2. OFP Server sends heartbeat UDP packets to wine.ofpigi.com:2303
3. OpenSpy Core receives heartbeats, stores in active list
4. OpenSpy Web API exposes list at https://wine.ofpigi.com/openspy/api/servers
5. ofpigi.com fetches API and displays all active servers

📡 OpenSpy API Expected Format

{
"servers": [
{
"ip": "165.232.107.127",
"port": 2302,
"hostname": "Project IGI Server 1",
"numplayers": 4,
"maxplayers": 32,
"mission": "1-8_D_Paintball.ABEL",
"gamever": "1.96",
"gstate": 14
}
]
}

🎯 Quick Commands to Test

docker logs winejs-openspy-core --tail 20
curl https://wine.ofpigi.com/openspy/api/servers
docker ps | grep ofp
nc -u -v wine.ofpigi.com 2303

📋 Summary

+----------------------------------+-----------------------------------+-----------------------------------+
| Component | Purpose | Key Setting |
+----------------------------------+-----------------------------------+-----------------------------------+
| ghcr.io/igiteam/ofp-server:latest | Your custom OFP Docker image | reportingIP set via env var |
| PufferPanel Template | Creates OFP servers | Sets reporting_ip="wine.ofpigi.com" |
| OpenSpy Core | Receives heartbeats | Listens on UDP ports 28900-29920 |
| OpenSpy Web API | Exposes server list | https://wine.ofpigi.com/openspy/api/servers |
| ofpigi.com | Displays browser | Fetches from OpenSpy API |
+----------------------------------+-----------------------------------+-----------------------------------+

This creates a complete, self-contained ecosystem where every OFP server you spin up
with PufferPanel automatically reports to your OpenSpy master and appears on your
server browser!
