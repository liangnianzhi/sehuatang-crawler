import json
import os
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sehuatang_crawler import SehuatangCrawler
from proxy_config import proxy_config

class ScheduledTask:
    def __init__(self, task_id: str, name: str, theme_id: str, mode: str, 
                 start_page: int, end_page: int, schedule_type: str, 
                 schedule_value: str, enabled: bool = True):
        self.task_id = task_id
        self.name = name
        self.theme_id = theme_id
        self.mode = mode
        self.start_page = start_page
        self.end_page = end_page
        self.schedule_type = schedule_type  # daily, weekly, interval
        self.schedule_value = schedule_value  # HH:MM, day_of_week, minutes
        self.enabled = enabled
        self.last_run = None
        self.next_run = None
        self.run_count = 0
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self):
        return {
            "task_id": self.task_id,
            "name": self.name,
            "theme_id": self.theme_id,
            "mode": self.mode,
            "start_page": self.start_page,
            "end_page": self.end_page,
            "schedule_type": self.schedule_type,
            "schedule_value": self.schedule_value,
            "enabled": self.enabled,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "next_run": self.next_run.isoformat() if self.next_run else None,
            "run_count": self.run_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    def calculate_next_run(self):
        """计算下次运行时间"""
        now = datetime.now()
        
        if self.schedule_type == "daily":
            # 每天固定时间运行
            hour, minute = map(int, self.schedule_value.split(":"))
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
        
        elif self.schedule_type == "weekly":
            # 每周固定时间运行
            day_of_week = int(self.schedule_value)
            hour, minute = 9, 0  # 默认上午9点
            if ":" in self.schedule_value:
                day_of_week, time_str = self.schedule_value.split(":")
                day_of_week = int(day_of_week)
                hour, minute = map(int, time_str.split(":"))
            
            days_ahead = day_of_week - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0) + timedelta(days=days_ahead)
        
        elif self.schedule_type == "interval":
            # 间隔时间运行
            minutes = int(self.schedule_value)
            if self.last_run:
                next_run = self.last_run + timedelta(minutes=minutes)
            else:
                next_run = now + timedelta(minutes=minutes)
        
        else:
            next_run = now + timedelta(hours=1)  # 默认1小时后
        
        self.next_run = next_run
        return next_run
    
    def should_run(self) -> bool:
        """检查是否应该运行"""
        if not self.enabled:
            return False
        
        if not self.next_run:
            self.calculate_next_run()
        
        return datetime.now() >= self.next_run

class TaskScheduler:
    def __init__(self, config_file: str = "scheduled_tasks.json"):
        self.config_file = config_file
        self.scheduled_tasks: Dict[str, ScheduledTask] = {}
        self.running = False
        self.thread = None
        self.load_tasks()
    
    def load_tasks(self):
        """加载定时任务"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for task_data in data.get("tasks", []):
                        task = self._create_task_from_dict(task_data)
                        if task:
                            self.scheduled_tasks[task.task_id] = task
            except Exception as e:
                print(f"加载定时任务失败: {e}")
    
    def save_tasks(self):
        """保存定时任务"""
        try:
            data = {
                "tasks": [task.to_dict() for task in self.scheduled_tasks.values()]
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存定时任务失败: {e}")
    
    def _create_task_from_dict(self, task_data: dict) -> Optional[ScheduledTask]:
        """从字典创建任务对象"""
        try:
            task = ScheduledTask(
                task_id=task_data["task_id"],
                name=task_data["name"],
                theme_id=task_data["theme_id"],
                mode=task_data["mode"],
                start_page=task_data["start_page"],
                end_page=task_data["end_page"],
                schedule_type=task_data["schedule_type"],
                schedule_value=task_data["schedule_value"],
                enabled=task_data.get("enabled", True)
            )
            
            if task_data.get("last_run"):
                task.last_run = datetime.fromisoformat(task_data["last_run"])
            if task_data.get("next_run"):
                task.next_run = datetime.fromisoformat(task_data["next_run"])
            if task_data.get("created_at"):
                task.created_at = datetime.fromisoformat(task_data["created_at"])
            if task_data.get("updated_at"):
                task.updated_at = datetime.fromisoformat(task_data["updated_at"])
            
            task.run_count = task_data.get("run_count", 0)
            return task
        except Exception as e:
            print(f"创建任务对象失败: {e}")
            return None
    
    def add_task(self, name: str, theme_id: str, mode: str, start_page: int, 
                 end_page: int, schedule_type: str, schedule_value: str) -> str:
        """添加定时任务"""
        task_id = f"scheduled_{int(time.time())}"
        task = ScheduledTask(
            task_id=task_id,
            name=name,
            theme_id=theme_id,
            mode=mode,
            start_page=start_page,
            end_page=end_page,
            schedule_type=schedule_type,
            schedule_value=schedule_value
        )
        task.calculate_next_run()
        
        self.scheduled_tasks[task_id] = task
        self.save_tasks()
        return task_id
    
    def update_task(self, task_id: str, **kwargs) -> bool:
        """更新定时任务"""
        if task_id not in self.scheduled_tasks:
            return False
        
        task = self.scheduled_tasks[task_id]
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        task.updated_at = datetime.now()
        task.calculate_next_run()
        self.save_tasks()
        return True
    
    def delete_task(self, task_id: str) -> bool:
        """删除定时任务"""
        if task_id in self.scheduled_tasks:
            del self.scheduled_tasks[task_id]
            self.save_tasks()
            return True
        return False
    
    def get_task(self, task_id: str) -> Optional[ScheduledTask]:
        """获取任务"""
        return self.scheduled_tasks.get(task_id)
    
    def get_all_tasks(self) -> List[ScheduledTask]:
        """获取所有任务"""
        return list(self.scheduled_tasks.values())
    
    def enable_task(self, task_id: str) -> bool:
        """启用任务"""
        return self.update_task(task_id, enabled=True)
    
    def disable_task(self, task_id: str) -> bool:
        """禁用任务"""
        return self.update_task(task_id, enabled=False)
    
    def execute_task(self, task: ScheduledTask):
        """执行任务"""
        try:
            print(f"执行定时任务: {task.name}")
            
            # 创建爬虫实例
            proxy = proxy_config.get_proxy()
            crawler = SehuatangCrawler(proxy=proxy)
            
            # 生成输出文件名
            output_file = f"scheduled_magnet_links_{task.task_id}_{int(time.time())}.txt"
            
            # 执行爬取
            result = crawler.crawl(
                theme_id=task.theme_id,
                mode=task.mode,
                start_page=task.start_page,
                end_page=task.end_page,
                output_file=output_file
            )
            
            # 更新任务状态
            task.last_run = datetime.now()
            task.run_count += 1
            task.calculate_next_run()
            self.save_tasks()
            
            print(f"定时任务执行完成: {task.name}, 结果: {result}")
            
        except Exception as e:
            print(f"执行定时任务失败: {task.name}, 错误: {e}")
            task.last_run = datetime.now()
            task.calculate_next_run()
            self.save_tasks()
    
    def check_and_run_tasks(self):
        """检查并运行到期的任务"""
        for task in self.scheduled_tasks.values():
            if task.should_run():
                # 在新线程中执行任务
                thread = threading.Thread(target=self.execute_task, args=(task,))
                thread.daemon = True
                thread.start()
    
    def start(self):
        """启动调度器"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._scheduler_loop)
        self.thread.daemon = True
        self.thread.start()
        print("定时任务调度器已启动")
    
    def stop(self):
        """停止调度器"""
        self.running = False
        if self.thread:
            self.thread.join()
        print("定时任务调度器已停止")
    
    def _scheduler_loop(self):
        """调度器主循环"""
        while self.running:
            try:
                self.check_and_run_tasks()
                time.sleep(60)  # 每分钟检查一次
            except Exception as e:
                print(f"调度器循环错误: {e}")
                time.sleep(60)

# 全局调度器实例
task_scheduler = TaskScheduler()
