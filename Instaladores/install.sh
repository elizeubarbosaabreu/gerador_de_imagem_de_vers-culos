#!/bin/bash

# Verifica se está sendo executado como root
if [ "$EUID" -ne 0 ]; then
  echo "Por favor, execute este script como root (sudo)." 
  exit 1
fi

# Caminhos de destino
BIN_PATH="/usr/local/bin/gerador_image_de_versiculo"
ICON_PATH="/usr/share/pixmaps/gerador_vers.png"
DESKTOP_PATH="/usr/share/applications/gerador_de_imagem_de_stories.desktop"

# Copiar executável
echo "Copiando executável para $BIN_PATH..."
cp gerador_image_de_versiculo "$BIN_PATH"
chmod +x "$BIN_PATH"

# Copiar ícone
echo "Copiando ícone para $ICON_PATH..."
cp gerador_vers.png "$ICON_PATH"

# Criar arquivo .desktop
echo "Criando atalho em $DESKTOP_PATH..."
cat > "$DESKTOP_PATH" <<EOF
[Desktop Entry]
Name=Gerador de Imagens de Versículos
Comment=Aplicativo para gerar imagens de versículos bíblicos
Exec=$BIN_PATH
Icon=$ICON_PATH
Terminal=false
Type=Application
Categories=Utility;
EOF

echo "Instalação concluída com sucesso!"

