#!/bin/bash

# 安裝 minimap2 和 k8 工具

echo "Installing Minimap2..."
# 下載並安裝 minimap2
git clone https://github.com/lh3/minimap2.git
cd minimap2
make
cd ..

echo "Installing k8..."
# 下載並安裝 k8
git clone https://github.com/lh3/k8.git
cd k8
make
cd ..

echo "Minimap2 and k8 have been installed successfully."

