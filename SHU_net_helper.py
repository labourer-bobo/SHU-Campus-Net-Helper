import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext
import threading
import time
import requests
import pystray
from PIL import Image, ImageDraw
from datetime import datetime
import os
import sys
import json
import traceback
import subprocess  # 用于获取ipconfig
import smtplib     # 用于发送邮件
from email.mime.text import MIMEText
from email.header import Header
from DrissionPage import ChromiumPage, ChromiumOptions

# ==================== 配置常量区 ====================
DEFAULT_LOGIN_URL = "http://10.10.9.9"
CHECK_URL = "http://connect.rom.miui.com/generate_204"
CHECK_INTERVAL = 30
LOGIN_CONFIG_FILE = "login_config.json"
EMAIL_CONFIG_FILE = "email_config.json"
# ====================================================

class NetworkAutoLoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SHU校园网助手 v0.2.0")
        self.root.geometry("520x550")
        
        # 点击窗口关闭按钮时，隐藏到托盘而不是退出
        self.root.protocol('WM_DELETE_WINDOW', self.hide_window)

        self.is_running = True
        self.is_processing = False
        
        # 界面显示变量
        self.status_var = tk.StringVar(value="后台监控中...")
        self.last_check_var = tk.StringVar(value="--:--:--")
        
        # 加载配置
        self.login_config = self.load_json(LOGIN_CONFIG_FILE)
        self.email_config = self.load_json(EMAIL_CONFIG_FILE)
        
        self.create_widgets()
        
        # 启动托盘图标线程
        try:
            self.tray_thread = threading.Thread(target=self.setup_tray, daemon=True)
            self.tray_thread.start()
        except: pass
        
        # 启动网络监控线程
        self.monitor_thread = threading.Thread(target=self.monitor_network, daemon=True)
        self.monitor_thread.start()

        # 【默认隐藏】启动时直接隐藏窗口，在后台运行
        self.root.withdraw()

    def load_json(self, filepath):
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return None
        return None

    def save_json(self, filepath, data):
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f)
            return True
        except Exception as e:
            self.log(f"保存配置失败: {e}")
            return False

    def create_widgets(self):
        tk.Label(self.root, text="校园网助手 v0.2.0 (IP汇报版)", font=("微软雅黑", 16, "bold")).pack(pady=10)
        
        # 状态显示区
        f = tk.Frame(self.root, relief="groove", bd=2)
        f.pack(fill="x", padx=20, pady=5)
        
        tk.Label(f, text="当前网络状态：", font=("微软雅黑", 10, "bold")).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        tk.Label(f, textvariable=self.status_var, fg="blue", font=("微软雅黑", 10)).grid(row=0, column=1, sticky="w")
        
        tk.Label(f, text="上次检测时间：", font=("微软雅黑", 10, "bold")).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        tk.Label(f, textvariable=self.last_check_var, font=("微软雅黑", 10)).grid(row=1, column=1, sticky="w")

        # 功能按钮区
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="🛠️ 1. 录制登录配置", 
                 command=lambda: self.run_thread_safe(self.start_capture),
                 bg="#FF5722", fg="white", width=25).pack(pady=5)
        
        tk.Button(btn_frame, text="📧 2. 配置汇报邮箱", 
                 command=self.configure_email,
                 bg="#2196F3", fg="white", width=25).pack(pady=5)
        
        tk.Button(btn_frame, text="🚀 3. 测试连接 & 发信", 
                 command=lambda: self.run_thread_safe(self.perform_login),
                 bg="#4CAF50", fg="white", width=25).pack(pady=5)

        tk.Button(btn_frame, text="🔽 隐藏到后台", 
                 command=self.hide_window,
                 bg="#607D8B", fg="white", width=25).pack(pady=5)

        # 日志区
        tk.Label(self.root, text="运行日志:", anchor="w").pack(fill="x", padx=20)
        self.log_text = scrolledtext.ScrolledText(self.root, height=8, state='disabled', font=("Consolas", 9))
        self.log_text.pack(fill="x", padx=20, pady=5)

    # 线程安全的UI更新方法
    def log(self, msg):
        def _log():
            try:
                self.log_text.config(state='normal')
                self.log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
                self.log_text.see(tk.END)
                self.log_text.config(state='disabled')
            except: pass
        self.root.after(0, _log)

    def safe_status(self, msg):
        self.root.after(0, lambda: self.status_var.set(msg))

    def show_info(self, title, msg):
        self.root.after(0, lambda: messagebox.showinfo(title, msg))

    def run_thread_safe(self, target_func):
        if self.is_processing:
            self.show_info("提示", "当前有任务正在执行，请稍候...")
            return
        threading.Thread(target=target_func, daemon=True).start()

    # ==================== 邮件功能模块 ====================
    def get_ipconfig_info(self):
        """获取本机完整的网络配置信息"""
        try:
            # Windows 中文系统通常是 gbk 编码
            result = subprocess.check_output("ipconfig /all", shell=True).decode('gbk', errors='ignore')
            return result
        except Exception as e:
            return f"获取 IP 信息失败: {e}"

    def configure_email(self):
        """弹出配置邮箱的对话框"""
        # 必须先显示窗口，否则弹窗可能看不见
        self.show_window(None, None)
        
        smtp = simpledialog.askstring("邮箱配置(1/4)", "请输入SMTP服务器：\n(如QQ邮箱: smtp.qq.com)", initialvalue="smtp.qq.com")
        if not smtp: return
        sender = simpledialog.askstring("邮箱配置(2/4)", "请输入发件人邮箱：")
        if not sender: return
        pwd = simpledialog.askstring("邮箱配置(3/4)", "请输入【授权码】(非登录密码)：")
        if not pwd: return
        target = simpledialog.askstring("邮箱配置(4/4)", "请输入接收通知的邮箱：", initialvalue=sender)
        if not target: return

        data = {"smtp": smtp, "sender": sender, "pwd": pwd, "target": target}
        if self.save_json(EMAIL_CONFIG_FILE, data):
            self.email_config = data
            self.log("邮箱配置已保存")
            messagebox.showinfo("成功", "邮箱配置已保存！\n下次联网成功后将发送IP信息。")

    def send_email_task(self):
        """发送邮件的具体执行逻辑"""
        if not self.email_config:
            self.log("未配置邮箱，跳过发送")
            return

        self.log("正在准备发送 IP 邮件...")
        try:
            content = self.get_ipconfig_info()
            cfg = self.email_config
            
            # 构建邮件
            msg = MIMEText(content, 'plain', 'utf-8')
            pc_name = os.getenv('COMPUTERNAME', 'MyPC')
            subject = f"【网络已连接】{pc_name} IP配置报告 - {datetime.now().strftime('%m-%d %H:%M')}"
            
            msg['Subject'] = Header(subject, 'utf-8')
            msg['From'] = cfg['sender']
            msg['To'] = cfg['target']

            # 发送 (使用 SSL 465端口)
            server = smtplib.SMTP_SSL(cfg['smtp'], 465)
            server.login(cfg['sender'], cfg['pwd'])
            server.sendmail(cfg['sender'], [cfg['target']], msg.as_string())
            server.quit()
            
            self.log("✅ IP 邮件发送成功！")
        except Exception as e:
            self.log(f"❌ 邮件发送失败: {e}")

    # ==================== 浏览器核心模块 ====================
    def get_browser(self):
        try:
            co = ChromiumOptions()
            co.auto_port()
            return ChromiumPage(co)
        except:
            self.log(f"浏览器启动异常:\n{traceback.format_exc()}")
            return None

    def start_capture(self):
        self.is_processing = True
        self.safe_status("正在录制...")
        self.show_window(None, None) # 强制前台显示
        self.log("启动浏览器进行录制...")
        
        page = None
        try:
            page = self.get_browser()
            if not page: return

            self.log(f"访问: {DEFAULT_LOGIN_URL}")
            page.get(DEFAULT_LOGIN_URL)
            
            # JS 获取 XPath 工具
            js_xpath = """
            return new Promise(resolve => {
                function getPath(e) {
                    if (e.id) return '//*[@id="'+e.id+'"]';
                    if (e === document.body) return e.tagName;
                    var ix = 0;
                    var siblings = e.parentNode.childNodes;
                    for (var i = 0; i < siblings.length; i++) {
                        var sibling = siblings[i];
                        if (sibling === e) return getPath(e.parentNode) + '/' + e.tagName + '[' + (ix + 1) + ']';
                        if (sibling.nodeType === 1 && sibling.tagName === e.tagName) ix++;
                    }
                }
                document.addEventListener('click', function handler(e) {
                    e.preventDefault(); e.stopPropagation();
                    document.removeEventListener('click', handler, true);
                    resolve(getPath(e.target));
                }, true);
            });
            """

            self.show_info("录制", "步骤 1/3：\n请点击网页上的【账号输入框】")
            u_xp = page.run_js(js_xpath)
            self.log(f"账号位置: {u_xp}")

            self.show_info("录制", "步骤 2/3：\n请点击网页上的【密码输入框】")
            p_xp = page.run_js(js_xpath)
            self.log(f"密码位置: {p_xp}")

            self.show_info("录制", "步骤 3/3：\n请点击网页上的【登录按钮】")
            b_xp = page.run_js(js_xpath)
            self.log(f"按钮位置: {b_xp}")

            self.root.after(0, lambda: self._input_dialogs(u_xp, p_xp, b_xp))

        except Exception:
            self.log(f"录制错误:\n{traceback.format_exc()}")
            if page: page.quit()
        finally:
            self.is_processing = False

    def _input_dialogs(self, u, p, b):
        self.show_window(None, None)
        user = simpledialog.askstring("配置", "输入真实【账号】：")
        if not user: return
        pwd = simpledialog.askstring("配置", "输入真实【密码】：")
        if not pwd: return
        
        cfg = {"url": DEFAULT_LOGIN_URL, "u_xp": u, "p_xp": p, "b_xp": b, "user": user, "pwd": pwd}
        if self.save_json(LOGIN_CONFIG_FILE, cfg):
            self.login_config = cfg
            self.log("登录配置保存成功")
            messagebox.showinfo("完成", "登录配置已保存！")

    def perform_login(self):
        if not self.login_config:
            self.show_info("提示", "请先录制登录配置")
            return
        
        self.is_processing = True
        self.safe_status("正在连接...")
        self.log("开始自动连接...")
        page = None
        
        try:
            page = self.get_browser()
            page.get(self.login_config['url'])
            
            cfg = self.login_config

            # 1. 填账号 (穿透式填表)
            js_user = f"""
            var e = document.evaluate('{cfg['u_xp']}', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            if (e && e.tagName !== 'INPUT') e = e.querySelector('input') || e;
            if(e) {{ 
                e.value = '{cfg['user']}'; 
                e.dispatchEvent(new Event('input', {{bubbles:true}})); 
                return "OK";
            }}
            return "Fail";
            """
            page.run_js(js_user)
            
            # 2. 填密码 (智能识别 input[type=password])
            js_pwd = f"""
            var pwd = '{cfg['pwd']}';
            var e = document.querySelector('input[type="password"]'); 
            if (!e) e = document.evaluate('{cfg['p_xp']}', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            if (e && e.tagName !== 'INPUT') e = e.querySelector('input') || e;
            
            if(e) {{ 
                e.focus(); 
                e.value = pwd; 
                e.dispatchEvent(new Event('input', {{bubbles:true}})); 
                e.dispatchEvent(new Event('change', {{bubbles:true}})); 
                return "OK";
            }}
            return "Fail";
            """
            page.run_js(js_pwd)
            
            time.sleep(0.5)
            
            # 3. 点击按钮
            js_btn = f"""
            var e = document.evaluate('{cfg['b_xp']}', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            if(e) {{ e.click(); return "OK"; }} return "Fail";
            """
            page.run_js(js_btn)
            
            self.log("登录动作完成，等待网络恢复...")
            page.quit()
            
            # 等待几秒后检查网络
            time.sleep(3)
            if self.check_net():
                self.log("网络已通，准备发送IP报告...")
                self.send_email_task()
            else:
                self.log("网络似乎未通，跳过发信")

        except Exception:
            self.log(f"连接过程出错:\n{traceback.format_exc()}")
            if page: page.quit()
        finally:
            self.is_processing = False

    # ==================== 后台监控与托盘 ====================
    def check_net(self):
        try:
            return requests.get(CHECK_URL, timeout=3).status_code == 204
        except:
            return False

    def monitor_network(self):
        while self.is_running:
            try:
                if not self.is_processing:
                    now = datetime.now().strftime("%H:%M:%S")
                    self.root.after(0, lambda: self.last_check_var.set(now))
                    
                    if self.check_net():
                        self.safe_status("在线")
                    else:
                        self.safe_status("离线 - 重连中...")
                        if self.login_config:
                            self.root.after(0, lambda: self.run_thread_safe(self.perform_login))
            except: pass
            time.sleep(CHECK_INTERVAL)

    def create_image(self):
        # 绘制托盘图标 (绿色方块)
        image = Image.new('RGB', (64, 64), (0, 150, 136))
        dc = ImageDraw.Draw(image)
        dc.rectangle((16, 16, 48, 48), fill="white")
        return image

    def setup_tray(self):
        try:
            icon = pystray.Icon("shu_helper", self.create_image(), "SHU校园网助手", 
                              menu=(pystray.MenuItem('显示主界面', self.show_window), 
                                    pystray.MenuItem('彻底退出', self.quit_app_force)))
            icon.run()
        except: pass

    def show_window(self, icon, item):
        self.root.after(0, self.root.deiconify)

    def hide_window(self):
        self.root.withdraw()

    def quit_app_force(self, icon=None, item=None):
        self.is_running = False
        os._exit(0)

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = NetworkAutoLoginApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Error", str(e))