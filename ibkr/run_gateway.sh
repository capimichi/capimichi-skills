#!/usr/bin/env bash
set -e

# ibkr Gateway Launcher
# Gestisce l'avvio del Gateway in conformità con gli standard XDG Base Directory:
# - Configurazione Docker: $XDG_CONFIG_HOME/ibkr/docker (default: ~/.config/ibkr/docker)
# - Dati e runtime persistenti: $XDG_DATA_HOME/ibkr (default: ~/.local/share/ibkr)
# Porta predefinita host: 5001 (per evitare conflitti con macOS AirPlay su porta 5000)

MODE="${1:-docker}"

CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/ibkr/docker"
DATA_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/ibkr"

# Inizializza i file di configurazione Docker se non presenti in XDG_CONFIG_HOME
init_docker_configs() {
    mkdir -p "$CONFIG_DIR" "$DATA_DIR/logs"

    if [ ! -f "$CONFIG_DIR/conf.yaml" ]; then
        cat << 'EOF' > "$CONFIG_DIR/conf.yaml"
    ip2loc: "US"
    proxyRemoteSsl: true
    proxyRemoteHost: "https://api.ibkr.com"
    listenPort: 5000
    listenSsl: true
    ccp: false
    svcEnvironment: "v1"
    sslCert: "vertx.jks"
    sslPwd: "mywebapi"
    authDelay: 3000
    portalBaseURL: ""
    serverOptions:
        blockedThreadCheckInterval: 1000000
        eventLoopPoolSize: 20
        workerPoolSize: 20
        maxWorkerExecuteTime: 100
        internalBlockingPoolSize: 20
    cors:
        origin.allowed: "*"
        allowCredentials: false
    webApps:
        - name: "demo"
          index: "index.html"
    ips:
      allow:
        - 127.0.0.1
        - 172.*
        - 10.*
        - 192.*
        - 131.216.*
        - localhost
      deny:
        - 212.90.324.10
EOF
    fi

    if [ ! -f "$CONFIG_DIR/Dockerfile" ]; then
        cat << 'EOF' > "$CONFIG_DIR/Dockerfile"
FROM amazoncorretto:17-alpine

WORKDIR /opt/cpgw

RUN apk add --no-cache curl unzip bash

# Download official IBKR Client Portal Gateway
RUN curl -sSL https://download2.interactivebrokers.com/portal/clientportal.gw.zip -o cpgw.zip \
    && unzip -q cpgw.zip \
    && rm cpgw.zip \
    && chmod +x bin/run.sh

# Copy customized conf.yaml with Docker bridge subnet whitelisting
COPY conf.yaml root/conf.yaml

EXPOSE 5000

CMD ["bin/run.sh", "root/conf.yaml"]
EOF
    fi

    if [ ! -f "$CONFIG_DIR/docker-compose.yml" ]; then
        cat << 'EOF' > "$CONFIG_DIR/docker-compose.yml"
services:
  cpgw:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: ibkr-cpgw
    ports:
      - "5001:5000"
    restart: unless-stopped
EOF
    fi
}

if [ "$MODE" = "docker" ]; then
    echo "🐳 Avvio di Interactive Brokers Client Portal Gateway..."
    echo "📁 Directory configurazione XDG: $CONFIG_DIR"
    
    init_docker_configs

    if ! docker info >/dev/null 2>&1; then
        echo "⚠️ Docker daemon non è attivo. Se usi Colima, esegui prima: colima start"
        echo "Oppure esegui in modalità nativa: $0 native"
        exit 1
    fi

    echo "🔨 Build dell'immagine Docker (se necessaria)..."
    DOCKER_BUILDKIT=0 docker build -q -t ibkr-cpgw "$CONFIG_DIR" >/dev/null

    echo "🚀 Avvio container 'ibkr-cpgw' su https://localhost:5001..."
    docker rm -f ibkr-cpgw 2>/dev/null || true
    docker run -d --name ibkr-cpgw -p 5001:5000 --restart unless-stopped ibkr-cpgw >/dev/null

    echo "✅ Gateway attivo in background su https://localhost:5001"
    echo "👉 Apri https://localhost:5001 nel browser per effettuare il login e confermare il 2FA (IB Key)."
elif [ "$MODE" = "native" ]; then
    echo "☕ Avvio di Interactive Brokers Client Portal Gateway in modalità nativa (Java)..."
    GATEWAY_DIR="$DATA_DIR/gateway"
    mkdir -p "$GATEWAY_DIR"
    init_docker_configs

    if [ ! -f "$GATEWAY_DIR/bin/run.sh" ]; then
        echo "📥 Download di Client Portal Gateway da Interactive Brokers..."
        curl -sSL "https://download2.interactivebrokers.com/portal/clientportal.gw.zip" -o "$GATEWAY_DIR/cpgw.zip"
        unzip -q "$GATEWAY_DIR/cpgw.zip" -d "$GATEWAY_DIR"
        rm -f "$GATEWAY_DIR/cpgw.zip"
        chmod +x "$GATEWAY_DIR/bin/run.sh"
    fi

    # Assicura conf.yaml aggiornato su porta 5001
    sed 's/listenPort: 5000/listenPort: 5001/g' "$CONFIG_DIR/conf.yaml" > "$GATEWAY_DIR/root/conf.yaml"

    echo "🚀 Esecuzione Gateway da $GATEWAY_DIR su porta 5001..."
    cd "$GATEWAY_DIR"
    exec bin/run.sh root/conf.yaml
elif [ "$MODE" = "stop" ]; then
    echo "🛑 Arresto del Gateway Docker..."
    docker rm -f ibkr-cpgw 2>/dev/null || true
    echo "✅ Container arrestato."
else
    echo "Uso: $0 [docker|native|stop]"
    exit 1
fi
