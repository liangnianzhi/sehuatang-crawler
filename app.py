from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import logging
import time
import threading
import os
from datetime import datetime
import json
from werkzeug.utils import secure_filename
import tempfile

# 导入爬虫模块
from sehuatang_crawler import SehuatangCrawler
from proxy_config import proxy_config
from scheduler import task_scheduler

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)  # 允许跨域请求

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 全局变量存储爬取任务状态
crawl_tasks = {}
task_counter = 0

class CrawlTask:
    def __init__(self, task_id, theme_id, mode, start_page, end_page, proxy, output_file):
        self.task_id = task_id
        self.theme_id = theme_id
        self.mode = mode
        self.start_page = start_page
        self.end_page = end_page
        self.proxy = proxy
        self.output_file = output_file
        self.status = "pending"  # pending, running, completed, failed
        self.progress = 0
        self.total_links = 0
        self.found_links = 0
        self.error_message = ""
        self.start_time = None
        self.end_time = None
        self.thread = None
        self.logs = []

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "theme_id": self.theme_id,
            "mode": self.mode,
            "start_page": self.start_page,
            "end_page": self.end_page,
            "proxy": self.proxy,
            "status": self.status,
            "progress": self.progress,
            "total_links": self.total_links,
            "found_links": self.found_links,
            "error_message": self.error_message,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "logs": self.logs
        }

def crawl_worker(task):
    """后台爬取工作线程"""
    try:
        task.status = "running"
        task.start_time = datetime.now()
        
        # 创建爬虫实例，传入代理设置
        crawler = SehuatangCrawler(proxy=task.proxy)
        
        # 设置进度回调
        def progress_callback(current, total, found):
            task.progress = int((current / total) * 100) if total > 0 else 0
            task.total_links = total
            task.found_links = found
        
        crawler.set_progress_callback(progress_callback)
        
        # 开始爬取
        result = crawler.crawl(
            theme_id=task.theme_id,
            mode=task.mode,
            start_page=task.start_page,
            end_page=task.end_page,
            output_file=task.output_file
        )
        
        if result["success"]:
            task.status = "completed"
            task.found_links = result["magnet_count"]
            task.logs = result.get("logs", [])
        else:
            task.status = "failed"
            task.error_message = result["error"]
            task.logs = result.get("logs", [])
            
    except Exception as e:
        task.status = "failed"
        task.error_message = str(e)
        logging.error(f"爬取任务 {task.task_id} 失败: {str(e)}")
    finally:
        task.end_time = datetime.now()

@app.route('/api/themes', methods=['GET'])
def get_themes():
    """获取可用主题列表"""
    themes = {
        "36": {"name": "亚洲无码", "url": "https://sehuatang.org/forum-36-1.html", "hot": "https://sehuatang.org/forum.php?mod=forumdisplay&fid=36&filter=heat&orderby=heats"},
        "37": {"name": "亚洲有码", "url": "https://sehuatang.org/forum-37-1.html", "hot": None},
        "2": {"name": "国产原创", "url": "https://sehuatang.org/forum-2-1.html", "hot": "https://sehuatang.org/forum.php?mod=forumdisplay&fid=2&filter=heat&orderby=heats"},
        "103": {"name": "高清中文字幕", "url": "https://sehuatang.org/forum-103-1.html", "hot": "https://sehuatang.org/forum.php?mod=forumdisplay&fid=103&filter=heat&orderby=heats"},
        "104": {"name": "素人原创", "url": "https://sehuatang.org/forum-104-1.html", "hot": None},
        "39": {"name": "动漫原创", "url": "https://sehuatang.org/forum-39-1.html", "hot": None},
        "152": {"name": "韩国主播", "url": "https://sehuatang.org/forum-152-1.html", "hot": "https://sehuatang.org/forum.php?mod=forumdisplay&fid=152&filter=heat&orderby=heats"}
    }
    
    # 转换为前端需要的格式
    theme_list = []
    for theme_id, theme_info in themes.items():
        theme_list.append({
            "id": theme_id,
            "name": theme_info["name"],
            "supports_hot": theme_info["hot"] is not None
        })
    
    return jsonify({
        "success": True,
        "data": theme_list
    })

@app.route('/api/crawl', methods=['POST'])
def start_crawl():
    """开始爬取任务"""
    global task_counter
    
    try:
        data = request.get_json()
        theme_id = data.get('theme_id')
        mode = data.get('mode', '1')  # 1: 普通, 2: 热门
        start_page = data.get('start_page', 1)
        end_page = data.get('end_page', 1)
        proxy = data.get('proxy', '')  # 代理设置
        
        if not theme_id:
            return jsonify({"success": False, "error": "缺少主题ID"}), 400
        
        if start_page > end_page:
            return jsonify({"success": False, "error": "起始页不能大于结束页"}), 400
        
        # 生成任务ID和输出文件名
        task_counter += 1
        task_id = f"task_{task_counter}_{int(time.time())}"
        output_file = f"magnet_links_{task_id}.txt"
        
        # 创建任务
        task = CrawlTask(task_id, theme_id, mode, start_page, end_page, proxy, output_file)
        crawl_tasks[task_id] = task
        
        # 启动后台线程
        task.thread = threading.Thread(target=crawl_worker, args=(task,))
        task.thread.daemon = True
        task.thread.start()
        
        return jsonify({
            "success": True,
            "task_id": task_id,
            "message": "爬取任务已启动"
        })
        
    except Exception as e:
        logging.error(f"启动爬取任务失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/tasks/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """获取任务状态"""
    if task_id not in crawl_tasks:
        return jsonify({"success": False, "error": "任务不存在"}), 404
    
    task = crawl_tasks[task_id]
    return jsonify({
        "success": True,
        "data": task.to_dict()
    })

@app.route('/api/tasks', methods=['GET'])
def get_all_tasks():
    """获取所有任务"""
    tasks = [task.to_dict() for task in crawl_tasks.values()]
    return jsonify({
        "success": True,
        "data": tasks
    })

@app.route('/api/download/<task_id>', methods=['GET'])
def download_result(task_id):
    """下载爬取结果"""
    if task_id not in crawl_tasks:
        return jsonify({"success": False, "error": "任务不存在"}), 404
    
    task = crawl_tasks[task_id]
    if task.status != "completed":
        return jsonify({"success": False, "error": "任务尚未完成"}), 400
    
    if not os.path.exists(task.output_file):
        return jsonify({"success": False, "error": "结果文件不存在"}), 404
    
    return send_file(
        task.output_file,
        as_attachment=True,
        download_name=f"magnet_links_{task.theme_id}_{task.mode}_{task.start_page}-{task.end_page}.txt"
    )

@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """删除任务"""
    if task_id not in crawl_tasks:
        return jsonify({"success": False, "error": "任务不存在"}), 404
    
    task = crawl_tasks[task_id]
    
    # 删除结果文件
    if os.path.exists(task.output_file):
        os.remove(task.output_file)
    
    # 从任务列表中移除
    del crawl_tasks[task_id]
    
    return jsonify({
        "success": True,
        "message": "任务已删除"
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "success": True,
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_tasks": len([t for t in crawl_tasks.values() if t.status == "running"])
    })

@app.route('/api/logs', methods=['GET'])
def get_recent_logs():
    """获取最近的日志"""
    try:
        # 获取所有任务的日志
        all_logs = []
        for task in crawl_tasks.values():
            if hasattr(task, 'logs') and task.logs:
                all_logs.extend(task.logs)
        
        # 按时间排序，返回最近的50条日志
        all_logs.sort(reverse=True)
        recent_logs = all_logs[:50]
        
        return jsonify({
            "success": True,
            "data": recent_logs
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/proxy/config', methods=['GET'])
def get_proxy_config():
    """获取代理配置"""
    try:
        config = proxy_config.get_config()
        return jsonify({
            "success": True,
            "data": config
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/proxy/config', methods=['POST'])
def set_proxy_config():
    """设置代理配置"""
    try:
        data = request.get_json()
        proxy_url = data.get('proxy_url', '')
        enabled = data.get('enabled', False)
        
        if enabled and not proxy_url:
            return jsonify({"success": False, "error": "启用代理时必须提供代理地址"}), 400
        
        proxy_config.set_proxy(proxy_url, enabled)
        
        return jsonify({
            "success": True,
            "message": "代理配置已保存"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# 定时任务相关API
@app.route('/api/scheduled-tasks', methods=['GET'])
def get_scheduled_tasks():
    """获取所有定时任务"""
    try:
        tasks = task_scheduler.get_all_tasks()
        return jsonify({
            "success": True,
            "data": [task.to_dict() for task in tasks]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/scheduled-tasks', methods=['POST'])
def create_scheduled_task():
    """创建定时任务"""
    try:
        data = request.get_json()
        required_fields = ['name', 'theme_id', 'mode', 'start_page', 'end_page', 'schedule_type', 'schedule_value']
        
        for field in required_fields:
            if field not in data:
                return jsonify({"success": False, "error": f"缺少必要字段: {field}"}), 400
        
        task_id = task_scheduler.add_task(
            name=data['name'],
            theme_id=data['theme_id'],
            mode=data['mode'],
            start_page=data['start_page'],
            end_page=data['end_page'],
            schedule_type=data['schedule_type'],
            schedule_value=data['schedule_value']
        )
        
        return jsonify({
            "success": True,
            "data": {"task_id": task_id},
            "message": "定时任务创建成功"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/scheduled-tasks/<task_id>', methods=['PUT'])
def update_scheduled_task(task_id):
    """更新定时任务"""
    try:
        data = request.get_json()
        success = task_scheduler.update_task(task_id, **data)
        
        if success:
            return jsonify({
                "success": True,
                "message": "定时任务更新成功"
            })
        else:
            return jsonify({"success": False, "error": "任务不存在"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/scheduled-tasks/<task_id>', methods=['DELETE'])
def delete_scheduled_task(task_id):
    """删除定时任务"""
    try:
        success = task_scheduler.delete_task(task_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": "定时任务删除成功"
            })
        else:
            return jsonify({"success": False, "error": "任务不存在"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/scheduled-tasks/<task_id>/enable', methods=['POST'])
def enable_scheduled_task(task_id):
    """启用定时任务"""
    try:
        success = task_scheduler.enable_task(task_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": "定时任务已启用"
            })
        else:
            return jsonify({"success": False, "error": "任务不存在"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/scheduled-tasks/<task_id>/disable', methods=['POST'])
def disable_scheduled_task(task_id):
    """禁用定时任务"""
    try:
        success = task_scheduler.disable_task(task_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": "定时任务已禁用"
            })
        else:
            return jsonify({"success": False, "error": "任务不存在"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """服务前端静态文件"""
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    # 启动定时任务调度器
    task_scheduler.start()
    app.run(host='0.0.0.0', port=5000, debug=False)
