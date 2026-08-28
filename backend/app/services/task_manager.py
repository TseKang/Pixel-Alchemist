"""
任务管理器 - 管理生成任务的状态
"""
import threading
from typing import Dict, Optional


class TaskManager:
    """任务管理器 (内存存储，后续可改为 Redis/数据库)"""

    def __init__(self):
        self._tasks: Dict[str, dict] = {}
        self._lock = threading.Lock()

    def create_task(self, task_id: str, params: dict):
        """创建新任务"""
        with self._lock:
            self._tasks[task_id] = {
                "status": "pending",
                "params": params,
                "result": None,
                "error": None
            }

    def update_status(self, task_id: str, status: str):
        """更新任务状态"""
        with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id]["status"] = status

    def complete_task(self, task_id: str, result: dict):
        """完成任务"""
        with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id]["status"] = "completed"
                self._tasks[task_id]["result"] = result

    def fail_task(self, task_id: str, error: str):
        """标记任务失败"""
        with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id]["status"] = "failed"
                self._tasks[task_id]["error"] = error

    def get_task(self, task_id: str) -> Optional[dict]:
        """获取任务信息"""
        with self._lock:
            return self._tasks.get(task_id)

    def delete_task(self, task_id: str):
        """删除任务"""
        with self._lock:
            self._tasks.pop(task_id, None)

    def list_tasks(self) -> Dict[str, dict]:
        """列出所有任务"""
        with self._lock:
            return dict(self._tasks)
