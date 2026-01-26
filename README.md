# SHU-Campus-Net-Helper (上海大学校园网助手)
<img width="803" height="884" alt="5f93b4419500c53552cdeb871ad4ce9b" src="https://github.com/user-attachments/assets/b19fe8c1-23ea-4eff-9ebb-d6b46e2893ef" />

##  项目简介
这是一个基于 Python 开发的上海大学校园网自动连接工具。
能够智能识别输入框并完成登录
默认访问地址是10.10.9.9，可用于实验室服务器周期性自动网络验证
当前开发版本仅支持windows系统，提供python源码便于拓展linux版本

**✨ 核心功能：**
* **自动连接**：开机自启，断网自动重连。
* **后台静默**：启动后自动隐藏至系统托盘，不打扰日常使用。
* **IP汇报**：连接成功后，自动抓取本机 `ipconfig` 信息并发送到指定邮箱（方便远程管理）。

---

##  使用步骤

### 1. 下载与运行
1.  在右侧 **Releases** 页面下载最新版本的 `SHU校园网助手.exe`：[最新版本下载](https://github.com/labourer-bobo/SHU-Campus-Net-Helper/releases/latest)
2.  双击运行，程序会自动隐藏到右下角系统托盘（绿色小方块图标）。

### 2. 初始化配置
1.  **右键托盘图标** -> 点击 **“显示主界面”**。
2.  点击 **“🛠️ 1. 录制登录配置”**：
    * 浏览器弹出后，依次点击网页上的：**账号框** -> **密码框** -> **登录按钮**。
    * 在弹窗中输入**真实账号密码**。
3.  点击 **“🚀 3. 测试连接”** 验证是否成功。

### 3. (可选) 开启 IP 邮件汇报
如果你需要远程管理电脑，可点击 **“📧 2. 配置汇报邮箱”**。
* **SMTP服务器**：如 QQ 邮箱填 `smtp.qq.com`。
* **授权码**：请在邮箱设置中开启 POP3/SMTP 服务获取（非登录密码）。
* QQ邮箱配置教程： https://help.mail.qq.com/detail/106/985

---

## 开机自启
### 一键进入自启动目录
1.  按 `Win + R`，输入 `shell:startup`。
2.  将 `exe` 文件的**快捷方式**拖入打开的文件夹中即可。

### 手动进入自启动目录
如果直接访问失败，可以手动找到类似如下地址
C:\Users\你的用户名\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup

* 在顶部的菜单栏，点击 “查看”，然后把 “隐藏的项目” 勾选上
* 依次进入以下路径：
* C 盘
* 用户 (Users)
* 你的用户名文件夹 (例如 xxx 或 Administrator)
* AppData (是半透明的隐藏文件夹)
* Roaming 
* Microsoft
* Windows
* 「开始」菜单 (Start Menu)
* 程序 (Programs)  程序
* 启动 (Startup)

---

##  开发者指南

### 环境依赖
* Python 3.8+
* 依赖库：见 `requirements.txt`

### 如何运行源码
```bash
git clone https://github.com/labourer-bobo/SHU-Campus-Net-Helper.git
pip install -r requirements.txt
python auto_net_v0.2.0.py

### 如何打包为 .exe 文件
pyinstaller -F -w --distpath output_exe --name "SHU校园网助手" SHU_net_helper.py
