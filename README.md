# SHU-Campus-Net-Helper (上海大学校园网助手)

## 📖 项目简介
这是一个基于 Python 开发的上海大学校园网自动连接工具。
能够智能识别输入框并完成登录

**✨ 核心功能：**
* **自动连接**：开机自启，断网自动重连。
* **后台静默**：启动后自动隐藏至系统托盘，不打扰日常使用。
* **IP汇报**：连接成功后，自动抓取本机 `ipconfig` 信息并发送到指定邮箱（方便远程管理）。

---

## 🛠️ 使用指南

### 1. 下载与运行
1.  在右侧 **Releases** 页面下载最新版本的 `SHU校园网助手.exe`。
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

## ⚙️ 开机自启
1.  按 `Win + R`，输入 `shell:startup`。
2.  将 `exe` 文件的**快捷方式**拖入打开的文件夹中即可。

---

## 💻 开发者指南

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
