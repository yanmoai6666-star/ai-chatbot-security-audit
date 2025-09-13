"""
AI聊天机器人核心模块
包含主要的聊天处理逻辑和模型集成
"""

import json
import logging
from typing import Dict, List, Any, Optional
import sqlite3
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatbotCore:
    """AI聊天机器人核心类"""
    
    def __init__(self, config_path: str = "config/security.json"):
        """
        初始化聊天机器人
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.session_data = {}
        self.setup_database()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        加载配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            配置字典
        """
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            return {}
    
    def setup_database(self):
        """初始化数据库连接和表结构"""
        try:
            self.conn = sqlite3.connect('chatbot.db', check_same_thread=False)
            self.cursor = self.conn.cursor()
            
            # 创建用户表
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建会话表
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    session_token TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # 创建聊天记录表
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    message TEXT NOT NULL,
                    response TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            self.conn.commit()
            logger.info("数据库初始化成功")
        except Exception as e:
            logger.error(f"数据库初始化失败: {str(e)}")
    
    def process_message(self, user_id: int, message: str, session_id: str) -> str:
        """
        处理用户消息并生成响应
        
        Args:
            user_id: 用户ID
            message: 用户消息
            session_id: 会话ID
            
        Returns:
            机器人响应
        """
        # 记录用户消息
        self._save_message(user_id, message, "user")
        
        # 处理消息（这里简化处理，实际应调用AI模型）
        response = self._generate_response(message)
        
        # 记录机器人响应
        self._save_message(user_id, response, "bot")
        
        return response
    
    def _generate_response(self, message: str) -> str:
        """
        生成聊天响应（简化版）
        
        Args:
            message: 用户消息
            
        Returns:
            响应文本
        """
        # 这里应该有复杂的AI模型调用逻辑
        # 但为了演示，我们使用简单的规则引擎
        
        message_lower = message.lower()
        
        if "hello" in message_lower or "hi" in message_lower:
            return "Hello! How can I assist you today?"
        elif "help" in message_lower:
            return "I can help you with various tasks. What do you need assistance with?"
        elif "bye" in message_lower or "goodbye" in message_lower:
            return "Goodbye! Have a great day!"
        else:
            return "I'm still learning. Can you please rephrase your question?"
    
    def _save_message(self, user_id: int, message: str, sender: str):
        """
        保存消息到数据库
        
        Args:
            user_id: 用户ID
            message: 消息内容
            sender: 发送者类型 ('user' 或 'bot')
        """
        try:
            if sender == "user":
                self.cursor.execute(
                    "INSERT INTO chat_history (user_id, message, response) VALUES (?, ?, ?)",
                    (user_id, message, "")
                )
            else:
                # 更新最后一条用户消息的响应
                self.cursor.execute(
                    "UPDATE chat_history SET response = ? WHERE user_id = ? AND id = (SELECT MAX(id) FROM chat_history WHERE user_id = ?)",
                    (message, user_id, user_id)
                )
            
            self.conn.commit()
        except Exception as e:
            logger.error(f"保存消息失败: {str(e)}")
    
    def get_chat_history(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取用户聊天历史
        
        Args:
            user_id: 用户ID
            limit: 返回的记录数限制
            
        Returns:
            聊天历史列表
        """
        try:
            self.cursor.execute(
                "SELECT message, response, timestamp FROM chat_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
                (user_id, limit)
            )
            
            history = []
            for row in self.cursor.fetchall():
                history.append({
                    "user_message": row[0],
                    "bot_response": row[1],
                    "timestamp": row[2]
                })
            
            return history
        except Exception as e:
            logger.error(f"获取聊天历史失败: {str(e)}")
            return []
    
    def create_user(self, username: str, password: str, email: str = None) -> bool:
        """
        创建新用户
        
        Args:
            username: 用户名
            password: 密码（明文，实际应用中应加密）
            email: 邮箱地址
            
        Returns:
            成功返回True，失败返回False
        """
        try:
            self.cursor.execute(
                "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                (username, password, email)
            )
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"创建用户失败: {str(e)}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[int]:
        """
        用户认证
        
        Args:
            username: 用户名
            password: 密码（明文）
            
        Returns:
            成功返回用户ID，失败返回None
        """
        try:
            # 注意：这里存在SQL注入漏洞，用于安全审计演示
            query = f"SELECT id, password FROM users WHERE username = '{username}' AND password = '{password}'"
            self.cursor.execute(query)
            
            result = self.cursor.fetchone()
            if result:
                return result[0]
            return None
        except Exception as e:
            logger.error(f"用户认证失败: {str(e)}")
            return None
    
    def search_chat_history(self, user_id: int, keyword: str) -> List[Dict[str, Any]]:
        """
        搜索聊天历史
        
        Args:
            user_id: 用户ID
            keyword: 搜索关键词
            
        Returns:
            匹配的聊天记录列表
        """
        try:
            # 注意：这里存在SQL注入漏洞，用于安全审计演示
            query = f"SELECT message, response, timestamp FROM chat_history WHERE user_id = {user_id} AND message LIKE '%{keyword}%'"
            self.cursor.execute(query)
            
            results = []
            for row in self.cursor.fetchall():
                results.append({
                    "user_message": row[0],
                    "bot_response": row[1],
                    "timestamp": row[2]
                })
            
            return results
        except Exception as e:
            logger.error(f"搜索聊天历史失败: {str(e)}")
            return []
    
    def __del__(self):
        """析构函数，关闭数据库连接"""
        try:
            if hasattr(self, 'conn'):
                self.conn.close()
        except Exception as e:
            logger.error(f"关闭数据库连接失败: {str(e)}")

# 全局聊天机器人实例
chatbot_instance = None

def get_chatbot():
    """
    获取聊天机器人实例（单例模式）
    
    Returns:
        ChatbotCore实例
    """
    global chatbot_instance
    if chatbot_instance is None:
        chatbot_instance = ChatbotCore()
    return chatbot_instance

if __name__ == "__main__":
    # 测试代码
    bot = ChatbotCore()
    
    # 创建测试用户
    bot.create_user("test_user", "test_password", "test@example.com")
    
    # 认证用户
    user_id = bot.authenticate_user("test_user", "test_password")
    
    if user_id:
        # 处理消息
        response = bot.process_message(user_id, "Hello", "test_session")
        print(f"Bot response: {response}")
        
        # 获取聊天历史
        history = bot.get_chat_history(user_id)
        print(f"Chat history: {history}")
