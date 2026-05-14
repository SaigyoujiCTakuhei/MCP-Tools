"""
网易云音乐每日推荐模块
负责：播放每日推荐、私人漫游（基于Selenium自动化）
"""
import time
import logging
import subprocess
import socket
import os
from typing import Optional, Dict, Any
from Lib.base import tool

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.common.exceptions import WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

logger = logging.getLogger(__name__)

class DailyRecommendController:
    def __init__(self, netease_path: str, chromedriver_path: str):
        self.driver = None
        self.netease_path = netease_path
        self.chromedriver_path = chromedriver_path
        self.debug_port = 9222

    def start_netease(self) -> bool:
        """启动网易云音乐"""
        try:
            subprocess.Popen([self.netease_path, f"--remote-debugging-port={self.debug_port}"], creationflags=subprocess.CREATE_NO_WINDOW)
            time.sleep(5)  # 等待启动
            return True
        except Exception as e:
            logger.error(f"启动网易云音乐失败: {e}")
            return False

    def connect(self) -> bool:
        """连接 ChromeDriver"""
        if not SELENIUM_AVAILABLE:
            return False
        
        try:
            if not os.path.exists(self.chromedriver_path):
                logger.error("ChromeDriver 路径不存在")
                return False
                
            service = Service(executable_path=self.chromedriver_path)
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", f"localhost:{self.debug_port}")
            
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("✅ 连接成功")
            return True
        except Exception as e:
            logger.error(f"连接失败: {e}")
            return False

    def disconnect(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    def play_daily_recommend(self) -> bool:
        """播放每日推荐"""
        if not self.driver:
            return False
        try:
            # 切换到推荐页
            tabs = self.driver.find_elements(By.XPATH, "//div[contains(@data-log, 'cell_pc_main_tab_entrance')]")
            if tabs:
                tabs[0].click()
                time.sleep(1)
            
            # 点击播放按钮 (简化逻辑，实际可能需要更复杂的定位)
            # 这里假设有一个通用的播放按钮或者在推荐页有特定结构
            # 原代码逻辑较复杂，这里简化为尝试点击页面上的播放元素
            play_btns = self.driver.find_elements(By.TAG_NAME, "button")
            for btn in play_btns:
                if "播放" in btn.text or "▶" in btn.get_attribute("innerHTML"):
                    btn.click()
                    time.sleep(2)
                    return True
            return False
        except Exception as e:
            logger.error(f"播放每日推荐失败: {e}")
            return False

    def play_roaming(self) -> bool:
        """启动私人漫游"""
        if not self.driver:
            return False
        try:
            # 查找漫游按钮
            roaming_btns = self.driver.find_elements(By.XPATH, "//*[contains(text(), '漫游')]")
            if roaming_btns:
                roaming_btns[0].click()
                time.sleep(2)
                return True
            return False
        except Exception as e:
            logger.error(f"启动漫游失败: {e}")
            return False

@tool(
    name="play_daily_recommend",
    description="播放网易云音乐每日推荐歌单。需要配置网易云音乐路径。",
    schema={
        "type": "object",
        "properties": {
            "netease_path": {"type": "string", "description": "网易云音乐客户端路径"},
            "chromedriver_path": {"type": "string", "description": "ChromeDriver路径"}
        },
        "required": ["netease_path", "chromedriver_path"]
    }
)
def play_daily_recommend(netease_path: str, chromedriver_path: str) -> dict:
    """播放每日推荐"""
    if not SELENIUM_AVAILABLE:
        return {"success": False, "error": "selenium 未安装"}
    
    try:
        controller = DailyRecommendController(netease_path, chromedriver_path)
        if not controller.start_netease():
            return {"success": False, "error": "启动网易云音乐失败"}
        if not controller.connect():
            return {"success": False, "error": "连接失败"}
        
        if controller.play_daily_recommend():
            return {"success": True, "message": "✅ 每日推荐播放成功"}
        else:
            return {"success": False, "error": "播放操作执行失败"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@tool(
    name="play_roaming",
    description="启动网易云音乐私人漫游功能。",
    schema={
        "type": "object",
        "properties": {
            "netease_path": {"type": "string", "description": "网易云音乐客户端路径"},
            "chromedriver_path": {"type": "string", "description": "ChromeDriver路径"}
        },
        "required": ["netease_path", "chromedriver_path"]
    }
)
def play_roaming(netease_path: str, chromedriver_path: str) -> dict:
    """启动私人漫游"""
    if not SELENIUM_AVAILABLE:
        return {"success": False, "error": "selenium 未安装"}
    
    try:
        controller = DailyRecommendController(netease_path, chromedriver_path)
        if not controller.start_netease():
            return {"success": False, "error": "启动网易云音乐失败"}
        if not controller.connect():
            return {"success": False, "error": "连接失败"}
        
        if controller.play_roaming():
            return {"success": True, "message": "✅ 私人漫游启动成功"}
        else:
            return {"success": False, "error": "启动操作执行失败"}
    except Exception as e:
        return {"success": False, "error": str(e)}
