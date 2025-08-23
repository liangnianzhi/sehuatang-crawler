import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import re
import os

# 尝试导入webdriver-manager，如果失败则使用默认方式
try:
    from webdriver_manager.chrome import ChromeDriverManager
    USE_WEBDRIVER_MANAGER = True
except ImportError:
    USE_WEBDRIVER_MANAGER = False
    print("提示: 安装 webdriver-manager 可以自动管理ChromeDriver版本")
    print("运行: pip install webdriver-manager")

# 配置日志
logging.basicConfig(
    filename='debug_crawl.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def setup_driver():
    """设置 Selenium WebDriver。"""
    options = webdriver.ChromeOptions()
    # 暂时不使用无头模式，方便调试
    # options.add_argument("--headless")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/139.0.0.0 Safari/537.36")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_experimental_option('useAutomationExtension', False)
    
    try:
        if USE_WEBDRIVER_MANAGER:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
        else:
            driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        logging.error(f"Chrome WebDriver 初始化失败: {str(e)}")
        print(f"Chrome WebDriver 初始化失败: {str(e)}")
        raise

def debug_page_structure(url: str):
    """调试页面结构，查看实际的HTML内容"""
    driver = setup_driver()
    try:
        print(f"正在访问: {url}")
        driver.get(url)
        
        # 等待页面加载
        time.sleep(5)
        
        # 获取页面标题
        title = driver.title
        print(f"页面标题: {title}")
        
        # 获取页面源码
        html = driver.page_source
        
        # 保存HTML到文件
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("HTML已保存到 debug_page.html")
        
        # 分析链接
        soup = BeautifulSoup(html, 'html.parser')
        
        # 查找所有链接
        all_links = soup.find_all('a', href=True)
        print(f"找到 {len(all_links)} 个链接")
        
        # 查找包含thread的链接
        thread_links = []
        for link in all_links:
            href = link.get('href', '')
            if 'thread' in href:
                thread_links.append(href)
                print(f"找到thread链接: {href}")
        
        print(f"总共找到 {len(thread_links)} 个包含thread的链接")
        
        # 查找可能的主题链接模式
        patterns = [
            r'thread-\d+-\d+-\d+\.html',
            r'thread-\d+\.html',
            r'thread\.php\?tid=\d+',
            r'forum\.php\?mod=viewthread&tid=\d+'
        ]
        
        for pattern in patterns:
            matches = []
            for link in all_links:
                href = link.get('href', '')
                if re.search(pattern, href):
                    matches.append(href)
            if matches:
                print(f"模式 {pattern} 匹配到 {len(matches)} 个链接:")
                for match in matches[:5]:  # 只显示前5个
                    print(f"  {match}")
        
        # 查找可能的主题列表容器
        possible_containers = [
            'div.threadlist',
            'div.forumlist',
            'table.threadlist',
            'ul.threadlist',
            'div#threadlist',
            'div.forum'
        ]
        
        for selector in possible_containers:
            elements = soup.select(selector)
            if elements:
                print(f"找到容器 {selector}: {len(elements)} 个元素")
        
        return html
        
    except Exception as e:
        print(f"调试过程中发生错误: {str(e)}")
        logging.error(f"调试错误: {str(e)}")
    finally:
        driver.quit()

def main():
    """主函数"""
    print("=" * 50)
    print("色花堂网站结构调试工具")
    print("=" * 50)
    
    # 测试几个可能的URL
    test_urls = [
        "https://sehuatang.org/forum-36-1.html",
        "https://sehuatang.org/forum.php?mod=forumdisplay&fid=36",
        "https://sehuatang.org/"
    ]
    
    for url in test_urls:
        print(f"\n正在调试URL: {url}")
        print("-" * 50)
        try:
            debug_page_structure(url)
            break  # 如果成功，就停止
        except Exception as e:
            print(f"调试 {url} 失败: {str(e)}")
            continue

if __name__ == "__main__":
    main()

