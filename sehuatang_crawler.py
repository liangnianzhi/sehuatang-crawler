import logging
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import re

# 尝试导入webdriver-manager，如果失败则使用默认方式
try:
    from webdriver_manager.chrome import ChromeDriverManager
    USE_WEBDRIVER_MANAGER = True
except ImportError:
    USE_WEBDRIVER_MANAGER = False

class SehuatangCrawler:
    def __init__(self, proxy=None):
        self.driver = None
        self.progress_callback = None
        self.proxy = proxy
        self.logs = []  # 存储操作日志
        self.themes = {
            "36": {"name": "亚洲无码", "url": "https://sehuatang.org/forum-36-1.html", "hot": "https://sehuatang.org/forum.php?mod=forumdisplay&fid=36&filter=heat&orderby=heats"},
            "37": {"name": "亚洲有码", "url": "https://sehuatang.org/forum-37-1.html", "hot": None},
            "2": {"name": "国产原创", "url": "https://sehuatang.org/forum-2-1.html", "hot": "https://sehuatang.org/forum.php?mod=forumdisplay&fid=2&filter=heat&orderby=heats"},
            "103": {"name": "高清中文字幕", "url": "https://sehuatang.org/forum-103-1.html", "hot": "https://sehuatang.org/forum.php?mod=forumdisplay&fid=103&filter=heat&orderby=heats"},
            "104": {"name": "素人原创", "url": "https://sehuatang.org/forum-104-1.html", "hot": None},
            "39": {"name": "动漫原创", "url": "https://sehuatang.org/forum-39-1.html", "hot": None},
            "152": {"name": "韩国主播", "url": "https://sehuatang.org/forum-152-1.html", "hot": "https://sehuatang.org/forum.php?mod=forumdisplay&fid=152&filter=heat&orderby=heats"}
        }

    def add_log(self, message, level="INFO"):
        """添加日志"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        self.logs.append(log_entry)
        logging.info(message)

    def get_logs(self):
        """获取所有日志"""
        return self.logs

    def add_log(self, message, level="INFO"):
        """添加日志"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        self.logs.append(log_entry)
        logging.info(message)

    def get_logs(self):
        """获取所有日志"""
        return self.logs

    def set_progress_callback(self, callback):
        """设置进度回调函数"""
        self.progress_callback = callback

    def setup_driver(self):
        """设置 Selenium WebDriver，支持代理"""
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # 无头模式
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/139.0.0.0 Safari/537.36")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # 添加代理支持
        if self.proxy:
            self.add_log(f"使用代理: {self.proxy}")
            options.add_argument(f'--proxy-server={self.proxy}')
        
        try:
            if USE_WEBDRIVER_MANAGER:
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
            else:
                driver = webdriver.Chrome(options=options)
            return driver
        except Exception as e:
            self.add_log(f"Chrome WebDriver 初始化失败: {str(e)}", "ERROR")
            raise

    def fetch_page(self, url: str, retries: int = 3) -> str:
        """使用 Selenium 抓取页面内容，包含重试机制和年龄确认处理"""
        for attempt in range(retries):
            try:
                self.add_log(f"尝试抓取 {url} (第 {attempt + 1}/{retries} 次)")
                self.driver.get(url)
                wait = WebDriverWait(self.driver, 10)
                
                # 检查是否是年龄验证页面
                current_url = self.driver.current_url
                page_title = self.driver.title
                
                if "SEHUATANG.ORG" in page_title and "满18岁" in self.driver.page_source:
                    self.add_log("检测到年龄验证页面，尝试点击进入按钮")
                    try:
                        # 尝试点击中文的进入按钮
                        enter_buttons = self.driver.find_elements(By.CSS_SELECTOR, 'a.enter-btn')
                        if enter_buttons:
                            enter_buttons[0].click()
                            self.add_log("已点击年龄验证进入按钮")
                            time.sleep(3)  # 等待页面重定向
                        else:
                            # 尝试点击英文按钮
                            enter_buttons = self.driver.find_elements(By.XPATH, '//a[contains(text(), "If you are over 18")]')
                            if enter_buttons:
                                enter_buttons[0].click()
                                self.add_log("已点击英文年龄验证按钮")
                                time.sleep(3)
                    except Exception as age_error:
                        self.add_log(f"年龄验证处理: {str(age_error)}")
                
                # 等待页面加载完成
                time.sleep(2)
                
                # 再次检查页面内容
                html = self.driver.page_source
                if "满18岁" in html or "SEHUATANG.ORG" in self.driver.title:
                    self.add_log("仍然在年龄验证页面，可能需要手动处理", "WARNING")
                    return ""
                
                self.add_log(f"成功抓取 {url}")
                return html
                
            except Exception as e:
                self.add_log(f"抓取 {url} 失败 (第 {attempt + 1}/{retries} 次): {str(e)}", "ERROR")
                if attempt < retries - 1:
                    wait_time = 2 ** (attempt + 1)
                    self.add_log(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    self.add_log(f"达到最大重试次数，跳过 {url}", "ERROR")
                    return ""
        return ""

    def extract_thread_urls(self, html: str) -> list:
        """从主页面提取所有主题的第一页链接，去重"""
        soup = BeautifulSoup(html, 'html.parser')
        thread_urls = set()
        thread_base = {}
        
        # 多种可能的链接模式
        patterns = [
            r'thread-\d+-\d+-\d+\.html',
            r'thread-\d+\.html',
            r'thread\.php\?tid=\d+',
            r'forum\.php\?mod=viewthread&tid=\d+'
        ]
        
        # 查找所有链接
        for a_tag in soup.find_all('a', href=True):
            href = a_tag.get('href', '')
            
            # 检查是否匹配任何模式
            for pattern in patterns:
                if re.search(pattern, href):
                    # 处理相对URL
                    if href.startswith('/'):
                        href = f"https://sehuatang.org{href}"
                    elif not href.startswith('http'):
                        href = f"https://sehuatang.org/{href}"
                    
                    # 提取主题ID并生成第一页链接
                    if 'thread-' in href and '.html' in href:
                        # 处理 thread-xxx-xxx-xxx.html 格式
                        match = re.match(r'.*?(thread-\d+)-\d+-\d+\.html', href)
                        if match:
                            thread_id = match.group(1)
                            if thread_id not in thread_base:
                                full_url = f"https://sehuatang.org/{thread_id}-1-1.html"
                                thread_urls.add(full_url)
                                thread_base[thread_id] = full_url
                                self.add_log(f"找到主题第一页链接: {full_url}")
                    elif 'tid=' in href:
                        # 处理 tid=xxx 格式
                        match = re.search(r'tid=(\d+)', href)
                        if match:
                            tid = match.group(1)
                            thread_id = f"thread-{tid}"
                            if thread_id not in thread_base:
                                full_url = f"https://sehuatang.org/{thread_id}-1-1.html"
                                thread_urls.add(full_url)
                                thread_base[thread_id] = full_url
                                self.add_log(f"找到主题第一页链接: {full_url}")
                    break  # 匹配到一个模式就够了
        
        if not thread_urls:
            self.add_log("未找到任何主题链接，检查HTML结构或选择器", "WARNING")
        
        return list(thread_urls)

    def extract_magnet_links(self, html: str) -> list:
        """从二级页面提取磁力链接"""
        soup = BeautifulSoup(html, 'html.parser')
        magnet_links = []
        for tag in soup.select('div.blockcode, div.t_msgfont, div.postcontent, div.message, p'):
            text = tag.get_text()
            magnet_matches = re.findall(r'magnet:\?xt=urn:[a-z0-9]+:[a-z0-9]{32,}', text, re.IGNORECASE)
            magnet_links.extend(magnet_matches)
        for a_tag in soup.select('a'):
            href = a_tag.get('href', '')
            if href.startswith('magnet:'):
                magnet_links.append(href)
        return magnet_links

    def crawl(self, theme_id: str, mode: str = '1', start_page: int = 1, end_page: int = 1, output_file: str = "magnet_links.txt"):
        """执行爬取任务，支持多页爬取"""
        try:
            # 验证主题ID
            if theme_id not in self.themes:
                return {"success": False, "error": f"无效的主题ID: {theme_id}"}
            
            theme_info = self.themes[theme_id]
            self.add_log(f"开始爬取主题: {theme_info['name']} (ID: {theme_id})")
            self.add_log(f"爬取模式: {'热门' if mode == '2' else '普通'}")
            self.add_log(f"爬取页数: 第{start_page}页到第{end_page}页")
            
            # 初始化WebDriver
            self.driver = self.setup_driver()
            
            all_magnet_links = set()
            total_threads = 0
            processed_threads = 0
            
            # 遍历指定页数
            for page_num in range(start_page, end_page + 1):
                self.add_log(f"开始处理第 {page_num} 页")
                
                # 构建URL
                if mode == "2" and theme_info["hot"]:
                    start_url = theme_info["hot"]
                else:
                    start_url = theme_info["url"].replace("-1.html", f"-{page_num}.html")
                
                # 抓取主页面
                main_html = self.fetch_page(start_url)
                if not main_html:
                    self.add_log(f"无法访问第 {page_num} 页: {start_url}", "ERROR")
                    continue
                
                # 提取所有主题第一页链接
                thread_urls = self.extract_thread_urls(main_html)
                if not thread_urls:
                    self.add_log(f"第 {page_num} 页未找到任何主题链接", "WARNING")
                    continue
                
                total_threads += len(thread_urls)
                self.add_log(f"第 {page_num} 页找到 {len(thread_urls)} 个主题")
                
                # 遍历二级页面提取磁力链接
                for i, thread_url in enumerate(thread_urls, 1):
                    self.add_log(f"处理第 {page_num} 页 {i}/{len(thread_urls)}: {thread_url}")
                    
                    thread_html = self.fetch_page(thread_url)
                    if thread_html:
                        magnet_links = self.extract_magnet_links(thread_html)
                        if magnet_links:
                            all_magnet_links.update(magnet_links)
                            self.add_log(f"从 {thread_url} 提取到 {len(magnet_links)} 个磁力链接")
                    
                    processed_threads += 1
                    
                    # 更新进度
                    if self.progress_callback:
                        self.progress_callback(processed_threads, total_threads, len(all_magnet_links))
                    
                    time.sleep(0.5)  # 避免请求过快

            # 保存结果
            if all_magnet_links:
                with open(output_file, "w", encoding="utf-8") as f:
                    for link in all_magnet_links:
                        f.write(link + "\n")
                self.add_log(f"总共找到 {len(all_magnet_links)} 个磁力链接，已保存到 {output_file}")
                
                return {
                    "success": True,
                    "magnet_count": len(all_magnet_links),
                    "output_file": output_file,
                    "theme_name": theme_info["name"],
                    "logs": self.logs
                }
            else:
                return {"success": False, "error": "未找到任何磁力链接", "logs": self.logs}
                
        except Exception as e:
            self.add_log(f"爬取过程中发生错误: {str(e)}", "ERROR")
            return {"success": False, "error": str(e), "logs": self.logs}
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass

