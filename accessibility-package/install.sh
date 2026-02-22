#!/bin/bash
# 无障碍命令行功能安装脚本
# 支持Ubuntu/Debian和基于WSL的系统

# 设置颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # 无颜色

# 显示横幅
echo -e "${GREEN}====================================${NC}"
echo -e "${GREEN}    无障碍命令行功能安装程序     ${NC}"
echo -e "${GREEN}====================================${NC}"
echo ""

# 检查root权限
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}请以root权限运行此脚本:${NC}"
  echo "sudo $0"
  exit 1
fi

# 检测系统类型
IS_WSL=0
if grep -q Microsoft /proc/version || grep -q WSL /proc/version; then
  IS_WSL=1
  echo -e "${YELLOW}检测到WSL环境，将调整安装过程...${NC}"
fi

# 检查必要工具
echo "检查必要工具..."
MISSING_TOOLS=""

for tool in expect dialog; do
  if ! command -v $tool &> /dev/null; then
    MISSING_TOOLS="$MISSING_TOOLS $tool"
  fi
done

if [ -n "$MISSING_TOOLS" ]; then
  echo -e "${YELLOW}正在安装缺少的工具:$MISSING_TOOLS${NC}"
  apt-get update
  apt-get install -y $MISSING_TOOLS
fi

# 创建目录
echo "创建系统目录..."
mkdir -p /usr/local/bin/accessibility

# 复制脚本
echo "安装无障碍脚本..."
cp ./scripts/* /usr/local/bin/accessibility/
chmod 755 /usr/local/bin/accessibility/*

# 创建符号链接
echo "创建全局命令链接..."
ln -sf /usr/local/bin/accessibility/autoyes.sh /usr/local/bin/autoyes
ln -sf /usr/local/bin/accessibility/autoinput.sh /usr/local/bin/autoinput
ln -sf /usr/local/bin/accessibility/autoexpect.exp /usr/local/bin/autoexpect
ln -sf /usr/local/bin/accessibility/auto-sudo.sh /usr/local/bin/auto-sudo
ln -sf /usr/local/bin/accessibility/auto-ssh.exp /usr/local/bin/auto-ssh
ln -sf /usr/local/bin/accessibility/easy-menu.sh /usr/local/bin/easy-menu

# 设置sudo无密码
echo "配置sudo无密码访问..."
if [ ! -d /etc/sudoers.d ]; then
  mkdir -p /etc/sudoers.d
fi

# 获取当前用户（如果是从sudo调用，使用SUDO_USER）
CURRENT_USER=${SUDO_USER:-$(logname 2>/dev/null || echo $USER)}

# 如果仍然无法获取用户名，尝试通过其他方式获取
if [ -z "$CURRENT_USER" ] || [ "$CURRENT_USER" = "root" ]; then
  CURRENT_USER=$(who am i | awk '{print $1}')
fi

if [ -z "$CURRENT_USER" ] || [ "$CURRENT_USER" = "root" ]; then
  echo -e "${YELLOW}警告: 无法确定实际用户名，将使用默认用户'${USER}'${NC}"
  CURRENT_USER=$USER
fi

echo "$CURRENT_USER ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/accessibility
chmod 0440 /etc/sudoers.d/accessibility

# 复制设置脚本
echo "安装设置脚本..."
cat > /usr/local/bin/accessibility-setup.sh << 'EOF'
#!/bin/bash
# 全局无障碍设置脚本

# 创建符号链接使脚本全局可用
ln -sf /usr/local/bin/accessibility/autoyes.sh /usr/local/bin/autoyes
ln -sf /usr/local/bin/accessibility/autoinput.sh /usr/local/bin/autoinput
ln -sf /usr/local/bin/accessibility/autoexpect.exp /usr/local/bin/autoexpect
ln -sf /usr/local/bin/accessibility/auto-sudo.sh /usr/local/bin/auto-sudo
ln -sf /usr/local/bin/accessibility/auto-ssh.exp /usr/local/bin/auto-ssh
ln -sf /usr/local/bin/accessibility/easy-menu.sh /usr/local/bin/easy-menu

# 为当前登录用户设置别名
if [ -n "$USER" ] && [ "$USER" != "root" ]; then
  # 确保.bash_aliases存在
  touch /home/$USER/.bash_aliases
  
  # 仅当别名不存在时才添加
  grep -q "alias apt-install" /home/$USER/.bash_aliases || cat >> /home/$USER/.bash_aliases << 'ALIASES'
# 无障碍命令别名
alias apt-install='/usr/local/bin/autoexpect "sudo apt-get install"'
alias apt-update='/usr/local/bin/autoexpect "sudo apt-get update"'
alias apt-upgrade='/usr/local/bin/autoexpect "sudo apt-get upgrade"'
alias apt-autoremove='/usr/local/bin/autoexpect "sudo apt-get autoremove"'

# 系统命令
alias service='/usr/local/bin/auto-sudo service'
alias systemctl='/usr/local/bin/auto-sudo systemctl'
alias reboot='/usr/local/bin/auto-sudo reboot'
alias shutdown='/usr/local/bin/auto-sudo shutdown'

# 常用管理任务
alias fdisk='/usr/local/bin/auto-sudo fdisk'
alias mount='/usr/local/bin/auto-sudo mount'
alias umount='/usr/local/bin/auto-sudo umount'

# 网络命令
alias ifconfig='/usr/local/bin/auto-sudo ifconfig'
alias ip='/usr/local/bin/auto-sudo ip'

# 可能需要特权的文件操作
alias cp-root='/usr/local/bin/auto-sudo cp'
alias mv-root='/usr/local/bin/auto-sudo mv'
alias rm-root='/usr/local/bin/auto-sudo rm'
alias chmod-root='/usr/local/bin/auto-sudo chmod'
alias chown-root='/usr/local/bin/auto-sudo chown'
ALIASES

  # 确保拥有正确的权限
  chown $USER:$USER /home/$USER/.bash_aliases
  chmod 644 /home/$USER/.bash_aliases

  # 创建桌面帮助文件
  mkdir -p /home/$USER/Desktop
  cat > /home/$USER/Desktop/无障碍命令行帮助.txt << 'HELP'
=== 命令行无障碍功能帮助 ===

以下工具可帮助您避免输入密码和y/n提示：

1. 无需密码运行sudo命令：
   - 正常使用'sudo'即可 - 已配置为不需要密码

2. 对于需要y/n确认的命令：
   - 使用 autoyes [命令]
   例如：autoyes apt-get upgrade

3. 对于需要特定输入的命令：
   - 使用 autoinput [输入内容] [命令]
   例如：autoinput "yes" apt-get install vim

4. 对于交互式命令（带有各种提示）：
   - 使用 autoexpect "[命令]"
   例如：autoexpect "sudo apt-get upgrade"

5. 无需密码提示的SSH连接：
   - 使用 auto-ssh [用户名] [主机名] [可选密码]
   例如：auto-ssh user server.example.com

6. 系统任务的简易图形菜单：
   - 运行 easy-menu
   - 或点击应用程序菜单中的"无障碍命令菜单"图标

7. 已设置常用命令的别名 - 查看 ~/.bash_aliases
HELP

  # 确保拥有正确的权限
  chown $USER:$USER /home/$USER/Desktop/无障碍命令行帮助.txt
  chmod 644 /home/$USER/Desktop/无障碍命令行帮助.txt
fi

# 通知用户已启用无障碍功能
if command -v notify-send &> /dev/null && [ -n "$DISPLAY" ]; then
  if [ -n "$USER" ] && [ "$USER" != "root" ]; then
    sudo -u $USER DISPLAY=$DISPLAY DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u $USER)/bus notify-send "无障碍功能" "命令行自动化功能已启用" 2>/dev/null || true
  fi
fi

# 记录已运行
echo "无障碍设置完成于 $(date)" >> /var/log/accessibility-setup.log 2>/dev/null || echo "无障碍设置完成于 $(date)" >> /tmp/accessibility-setup.log
EOF

chmod 755 /usr/local/bin/accessibility-setup.sh

# 创建桌面快捷方式
echo "创建桌面快捷方式..."
cat > /usr/share/applications/accessibility-menu.desktop << 'EOF'
[Desktop Entry]
Name=无障碍命令菜单
Name[en]=Accessibility Command Menu
Comment=易于使用的系统管理菜单
Comment[en]=Easy-to-use system management menu
Exec=/usr/local/bin/easy-menu
Terminal=true
Type=Application
Categories=System;Utility;Accessibility;
Icon=preferences-desktop-accessibility
Keywords=accessibility;command;menu;
Keywords[zh_CN]=无障碍;命令;菜单;
EOF

# 设置自启动 - 自动为当前用户配置
USER_HOME=$(eval echo ~$CURRENT_USER)
mkdir -p $USER_HOME/.config/autostart
cat > $USER_HOME/.config/autostart/accessibility-setup.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=Accessibility Setup
Comment=Setup accessibility features for command line
Exec=/usr/local/bin/accessibility-setup.sh
Terminal=false
Hidden=false
X-GNOME-Autostart-enabled=true
StartupNotify=false
EOF

chown $CURRENT_USER:$CURRENT_USER $USER_HOME/.config/autostart/accessibility-setup.desktop

# 非WSL系统才设置系统服务
if [ $IS_WSL -eq 0 ]; then
  echo "配置系统服务..."
  # 检查systemd可用性
  if command -v systemctl &> /dev/null; then
    cat > /etc/systemd/system/accessibility.service << 'EOF'
[Unit]
Description=Command Line Accessibility Service
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/accessibility-setup.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable accessibility.service
    systemctl start accessibility.service
  else
    echo -e "${YELLOW}未检测到systemd，将使用rc.local方式设置自启动${NC}"
    # 使用rc.local备选方案
    if [ -f /etc/rc.local ]; then
      sed -i '/exit 0/i /usr/local/bin/accessibility-setup.sh' /etc/rc.local
    else
      echo '#!/bin/sh -e' > /etc/rc.local
      echo '/usr/local/bin/accessibility-setup.sh' >> /etc/rc.local
      echo 'exit 0' >> /etc/rc.local
      chmod +x /etc/rc.local
    fi
  fi
else
  echo -e "${YELLOW}在WSL环境中跳过系统服务配置${NC}"
  echo "要在登录时自动运行设置，请将下面的行添加到您的.bashrc或.bash_profile:"
  echo "/usr/local/bin/accessibility-setup.sh"
fi

# 立即运行设置脚本
echo "应用设置..."
/usr/local/bin/accessibility-setup.sh

# 安静黑色屏保模块（用户级）
echo "安装安静黑色屏保模块..."
mkdir -p /usr/local/share/accessibility/quiet-black-screensaver
cp -r ./modules/quiet-black-screensaver/* /usr/local/share/accessibility/quiet-black-screensaver/
chmod -R a+rX /usr/local/share/accessibility/quiet-black-screensaver
install -m 0755 /usr/local/share/accessibility/quiet-black-screensaver/bin/qbsctl /usr/local/bin/qbsctl

if [ -n "$CURRENT_USER" ] && [ "$CURRENT_USER" != "root" ]; then
  echo "为用户 ${CURRENT_USER} 初始化安静黑色屏保..."
  su - "$CURRENT_USER" -c "MODULE_ROOT=/usr/local/share/accessibility/quiet-black-screensaver /usr/local/bin/qbsctl install" || true
  su - "$CURRENT_USER" -c "/usr/local/bin/qbsctl enable" || true
fi

echo -e "${GREEN}安装完成!${NC}"
echo "无障碍命令行功能已成功安装。"
echo "您现在可以使用以下命令:"
echo "  - autoyes"
echo "  - autoinput"
echo "  - autoexpect"
echo "  - auto-sudo"
echo "  - auto-ssh"
echo "  - easy-menu"
echo "  - qbsctl (安静黑色屏保控制)"
echo ""
echo "在桌面上也创建了帮助文件。"

# WSL特定说明
if [ $IS_WSL -eq 1 ]; then
  echo -e "${YELLOW}WSL特别说明:${NC}"
  echo "1. 请手动将此行添加到您的.bashrc文件以确保每次登录时加载设置:"
  echo "   echo '/usr/local/bin/accessibility-setup.sh' >> ~/.bashrc"
  echo "2. WSL不支持图形通知，某些功能可能需要额外配置"
fi

exit 0 
