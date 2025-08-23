import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import os

# 配置日志
logging.basicConfig(
    filename='sehuatang_crawl.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def setup_driver():
    """设置 Selenium WebDriver。"""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 无头模式
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/139.0.0.0 Safari/537.36")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    return driver

def fetch_page(url: str, driver, retries: int = 3) -> str:
    """使用 Selenium 抓取页面内容，包含重试机制和年龄确认处理。"""
    for attempt in range(retries):
        try:
            logging.info(f"尝试抓取 {url} (第 {attempt + 1}/{retries} 次)")
            driver.get(url)
            wait = WebDriverWait(driver, 10)
            # 处理年龄确认
            try:
                confirm_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "If you are over 18, please click here")]')))  # 根据截图调整XPath
                confirm_button.click()
                logging.info("已点击年龄确认按钮")
                time.sleep(2)  # 等待页面重定向
            except:
                logging.info("未找到年龄确认按钮，假设已通过")
            html = driver.page_source
            logging.info(f"成功抓取 {url}")
            return html
        except Exception as e:
            logging.error(f"抓取 {url} 失败: {str(e)}")
            if attempt < retries - 1:
                wait_time = 2 ** (attempt + 1)
                logging.info(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            else:
                logging.error(f"达到最大重试次数，跳过 {url}")
                return ""
    return ""

def extract_thread_urls(html: str) -> list:
    """从主页面提取所有主题的第一页链接，去重。"""
    soup = BeautifulSoup(html, 'html.parser')
    thread_urls = set()
    thread_base = {}
    for a_tag in soup.select('a[href*="thread-"]'):
        href = a_tag.get('href', '')
        if href and re.search(r'thread-\d+-\d+-\d+\.html', href):
            base_match = re.match(r'(thread-\d+)-(\d+)-(\d+)\.html', href)
            if base_match:
                thread_id = base_match.group(1)
                if thread_id not in thread_base:
                    full_url = f"https://sehuatang.org/{thread_id}-1-1.html"
                    thread_urls.add(full_url)
                    thread_base[thread_id] = full_url
                    logging.info(f"找到主题第一页链接: {full_url}")
    if not thread_urls:
        logging.warning("未找到任何主题链接，检查HTML结构或选择器。")
        logging.debug(f"页面完整HTML: {html[:2000]}...")
    return list(thread_urls)

def extract_magnet_links(html: str) -> list:
    """从二级页面提取磁力链接。"""
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
    if not magnet_links:
        logging.debug(f"页面HTML片段: {html[:500]}...")
    return magnet_links

def crawl_magnet_links(start_url: str, driver, output_file: str = "magnet_links.txt"):
    """爬取所有磁力链接并保存。"""
    # 抓取主页面
    main_html = fetch_page(start_url, driver=driver)
    if not main_html:
        logging.error(f"无法访问主页面 {start_url}，程序终止。")
        return
    
    # 提取所有主题第一页链接
    thread_urls = extract_thread_urls(main_html)
    if not thread_urls:
        logging.error(f"未找到任何主题链接，检查 {start_url} 的结构。")
        return
    
    # 遍历二级页面提取磁力链接
    all_magnet_links = set()
    for thread_url in thread_urls:
        print(f"处理 {thread_url}...")  # 进度提示
        thread_html = fetch_page(thread_url, driver=driver)
        if thread_html:
            magnet_links = extract_magnet_links(thread_html)
            if magnet_links:
                all_magnet_links.update(magnet_links)
                logging.info(f"从 {thread_url} 提取到 {len(magnet_links)} 个磁力链接")
            else:
                logging.warning(f"未在 {thread_url} 中找到磁力链接")
        time.sleep(0.5)  # 加快速度

    # 保存结果
    if all_magnet_links:
        with open(output_file, "w", encoding="utf-8") as f:
            for link in all_magnet_links:
                f.write(link + "\n")
        logging.info(f"总共找到 {len(all_magnet_links)} 个磁力链接，已保存到 {output_file}")
    else:
        logging.warning("未找到任何磁力链接。")

def main():
    """主函数，允许用户选择主题和页面页码，支持热门模式。"""
    # 定义主题与论坛URL映射
    themes = {
        "36": {"name": "亚洲无码", "url": "https://sehuatang.org/forum-36-1.html", "hot": "https://sehuatang.org/forum.php?mod=forumdisplay&fid=36&filter=heat&orderby=heats"},
        "37": {"name": "亚洲有码", "url": "https://sehuatang.org/forum-37-1.html", "hot": None},
        "2": {"name": "国产原创", "url": "https://sehuatang.org/forum-2-1.html", "hot": "https://sehuatang.org/forum.php?mod=forumdisplay&fid=2&filter=heat&orderby=heats"},
        "103": {"name": "高清中文字幕", "url": "https://sehuatang.org/forum-103-1.html", "hot": "https://sehuatang.org/forum.php?mod=forumdisplay&fid=103&filter=heat&orderby=heats"},
        "104": {"name": "素人原创", "url": "https://sehuatang.org/forum-104-1.html", "hot": None},
        "39": {"name": "动漫原创", "url": "https://sehuatang.org/forum-39-1.html", "hot": None},
        "152": {"name": "韩国主播", "url": "https://sehuatang.org/forum-152-1.html", "hot": "https://sehuatang.org/forum.php?mod=forumdisplay&fid=152&filter=heat&orderby=heats"}
    }
    
    # 显示主题选项
    print("可用主题：")
    for forum_id, value in themes.items():
        hot_info = f" (热门: {value['hot']})" if value["hot"] else ""
        print(f"{forum_id}. {value['name']} ({value['url']} {hot_info})")
    
    while True:
        try:
            theme_choice = input("请输入主题编号（例如：36、103）：")
            if theme_choice not in themes:
                print("无效的主题编号，请重试。")
                continue
            mode = input("选择模式 (1: 普通, 2: 热门, 留空为普通): ").strip()
            page = int(input("请输入要爬取的页面页码（例如：1、2、3）：")) if mode != "2" else 1  # 热门模式默认第1页
            if page <= 0:
                print("页码必须大于0，请重试。")
                continue
            if mode == "2" and themes[theme_choice]["hot"]:
                start_url = themes[theme_choice]["hot"]
            else:
                start_url = themes[theme_choice]["url"].replace("-1.html", f"-{page}.html")
            print(f"将爬取 {themes[theme_choice]['name']} 的第 {page if mode != '2' else '热门'} 页")
            driver = setup_driver()
            crawl_magnet_links(start_url, driver)
            driver.quit()
            break
        except ValueError:
            print("请输入有效的数字页码，请重试。")
        except KeyError:
            print("该主题不支持热门模式，请选择普通模式。")

if __name__ == "__main__":
    main()dall(r'magnet:\?xt=urn:[a-z0-9]+:[a-z0-9]{32,}', text, re.IGNORECASE)
        magnet_links.extend(magnet_matches)
    for a_tag in soup.select('a'):
        href = a_tag.get('href', '')
        if href.startswith('magnet:'):
            magnet_links.append(href)
    if not magnet_links:
        logging.debug(f"页面HTML片段: {html[:500]}...")
    return magnet_links

def crawl_magnet_links(start_url: str, driver, output_file: str = "magnet_links.txt"):
    """爬取所有磁力链接并保存。"""
    try:
        # 抓取主页面
        main_html = fetch_page(start_url, driver=driver)
        if not main_html:
            logging.error(f"无法访问主页面 {start_url}，程序终止。")
            print(f"无法访问主页面 {start_url}，程序终止。")
            return
        
        # 提取所有主题第一页链接
        thread_urls = extract_thread_urls(main_html)
        if not thread_urls:
            logging.error(f"未找到任何主题链接，检查 {start_url} 的结构。")
            print(f"未找到任何主题链接，检查 {start_url} 的结构。")
            return
        
        print(f"找到 {len(thread_urls)} 个主题链接，开始提取磁力链接...")
        
        # 遍历二级页面提取磁力链接
        all_magnet_links = set()
        for i, thread_url in enumerate(thread_urls, 1):
            print(f"处理 {i}/{len(thread_urls)}: {thread_url}...")
            thread_html = fetch_page(thread_url, driver=driver)
            if thread_html:
                magnet_links = extract_magnet_links(thread_html)
                if magnet_links:
                    all_magnet_links.update(magnet_links)
                    logging.info(f"从 {thread_url} 提取到 {len(magnet_links)} 个磁力链接")
                    print(f"  ✓ 找到 {len(magnet_links)} 个磁力链接")
                else:
                    logging.warning(f"未在 {thread_url} 中找到磁力链接")
                    print(f"  ✗ 未找到磁力链接")
            time.sleep(0.5)  # 避免请求过快

        # 保存结果
        if all_magnet_links:
            with open(output_file, "w", encoding="utf-8") as f:
                for link in all_magnet_links:
                    f.write(link + "\n")
            logging.info(f"总共找到 {len(all_magnet_links)} 个磁力链接，已保存到 {output_file}")
            print(f"✓ 总共找到 {len(all_magnet_links)} 个磁力链接，已保存到 {output_file}")
        else:
            logging.warning("未找到任何磁力链接。")
            print("✗ 未找到任何磁力链接。")
    except Exception as e:
        logging.error(f"爬取过程中发生错误: {str(e)}")
        print(f"爬取过程中发生错误: {str(e)}")

def main():
    """主函数，允许用户选择主题和页面页码，支持热门模式。"""
    # 定义主题与论坛URL映射
    themes = {
        "36": {"name": "亚洲无码", "url": "https://sehuatang.org/forum-36-1.html", "hot": "https://sehuatang.org/forum.php?mod=forumdisplay&fid=36&filter=heat&orderby=heats"},
        "37": {"name": "亚洲有码", "url": "https://sehuatang.org/forum-37-1.html", "hot": None},
        "2": {"name": "国产原创", "url": "https://sehuatang.org/forum-2-1.html", "hot": "https://sehuatang.org/forum.php?mod=forumdisplay&fid=2&filter=heat&orderby=heats"},
        "103": {"name": "高清中文字幕", "url": "https://sehuatang.org/forum-103-1.html", "hot": "https://sehuatang.org/forum.php?mod=forumdisplay&fid=103&filter=heat&orderby=heats"},
        "104": {"name": "素人原创", "url": "https://sehuatang.org/forum-104-1.html", "hot": None},
        "39": {"name": "动漫原创", "url": "https://sehuatang.org/forum-39-1.html", "hot": None},
        "152": {"name": "韩国主播", "url": "https://sehuatang.org/forum-152-1.html", "hot": "https://sehuatang.org/forum.php?mod=forumdisplay&fid=152&filter=heat&orderby=heats"}
    }
    
    print("=" * 50)
    print("色花堂磁力链接爬虫工具")
    print("=" * 50)
    
    # 显示主题选项
    print("\n可用主题：")
    for forum_id, value in themes.items():
        hot_info = " (支持热门模式)" if value["hot"] else ""
        print(f"{forum_id}. {value['name']}{hot_info}")
    
    while True:
        try:
            print("\n" + "-" * 30)
            theme_choice = input("请输入主题编号（例如：36、103）：").strip()
            if theme_choice not in themes:
                print("❌ 无效的主题编号，请重试。")
                continue
                
            mode = input("选择模式 (1: 普通, 2: 热门, 留空为普通): ").strip()
            if mode == "2" and not themes[theme_choice]["hot"]:
                print("❌ 该主题不支持热门模式，请选择普通模式。")
                continue
                
            if mode != "2":
                try:
                    page = int(input("请输入要爬取的页面页码（例如：1、2、3）："))
                    if page <= 0:
                        print("❌ 页码必须大于0，请重试。")
                        continue
                except ValueError:
                    print("❌ 请输入有效的数字页码，请重试。")
                    continue
            else:
                page = 1  # 热门模式默认第1页
                
            if mode == "2" and themes[theme_choice]["hot"]:
                start_url = themes[theme_choice]["hot"]
                print(f"🎯 将爬取 {themes[theme_choice]['name']} 的热门页面")
            else:
                start_url = themes[theme_choice]["url"].replace("-1.html", f"-{page}.html")
                print(f"🎯 将爬取 {themes[theme_choice]['name']} 的第 {page} 页")
            
            print(f"📡 目标URL: {start_url}")
            print("\n开始爬取...")
            
            try:
                driver = setup_driver()
                crawl_magnet_links(start_url, driver)
            except Exception as e:
                logging.error(f"爬取过程中发生错误: {str(e)}")
                print(f"❌ 爬取失败: {str(e)}")
            finally:
                try:
                    driver.quit()
                except:
                    pass
            break
            
        except KeyboardInterrupt:
            print("\n\n⚠️ 用户中断操作")
            break
        except Exception as e:
            print(f"❌ 发生未知错误: {str(e)}")
            logging.error(f"主函数错误: {str(e)}")

if __name__ == "__main__":
    main()