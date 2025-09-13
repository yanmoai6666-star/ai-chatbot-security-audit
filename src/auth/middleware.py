"""
认证中间件 - 处理用户认证和授权
"""
import jwt
from functools import wraps
from flask import request, jsonify

# 模拟用户数据库
USERS = {
    "admin": {
        "password": "secure_hashed_password_123",  # 实际应用中应使用加盐哈希
        "role": "admin"
    },
    "user": {
        "password": "another_hashed_password_456",
        "role": "user"
    }
}

SECRET_KEY = "your-secret-key-here"  # 应存储在环境变量中

def authenticate(username, password):
    """
    验证用户凭据
    
    Args:
        username: 用户名
        password: 密码
        
    Returns:
        token或None
    """
    user = USERS.get(username)
    if user and user["password"] == password:  # 实际应用中应使用密码哈希比较
        token = jwt.encode(
            {"username": username, "role": user["role"]},
            SECRET_KEY,
            algorithm="HS256"
        )
        return token
    return None

def requires_auth(role=None):
    """
    认证装饰器
    
    Args:
        role: 需要的角色级别
        
    Returns:
        装饰器函数
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({"error": "Authorization required"}), 401
            
            try:
                # 移除"Bearer "前缀（如果存在）
                if token.startswith("Bearer "):
                    token = token[7:]
                
                payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                
                # 检查角色权限
                if role and payload.get("role") != role:
                    return jsonify({"error": "Insufficient permissions"}), 403
                    
                # 将用户信息添加到请求上下文
                request.user = payload
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token"}), 401
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator
