import json
from typing import Any, Optional

class SSEMessage:
    """统一的 SSE 消息格式"""
    
    @staticmethod
    def create(
        content: str,
        event_type: str = "message",
        done: bool = False
    ) -> str:
        """创建 SSE 消息
        
        Args:
            content: 消息内容
            event_type: 事件类型
            done: 是否结束
        
        Returns:
            str: 格式化的 SSE 消息
        """
        if done:
            return "event: done\ndata: [DONE]\n\n"
            
        data = {
            "content": content,
            "type": event_type
        }
        return f"data: {json.dumps(data)}\n\n" 