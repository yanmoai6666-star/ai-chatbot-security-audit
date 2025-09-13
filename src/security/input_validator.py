"""
输入验证模块 - 防止SQL注入和XSS攻击
"""
import re
import html

def validate_input(user_input, input_type="text"):
    """
    验证和清理用户输入
    
    Args:
        user_input: 用户输入的文本
        input_type: 输入类型 (text, email, number)
    
    Returns:
        清理后的安全文本
    """
    if not user_input:
        return ""
    
    # 移除多余空白字符
    cleaned_input = user_input.strip()
    
    # 根据输入类型进行特定验证
    if input_type == "email":
        if not re.match(r"[^@]+@[^@]+\.[^@]+", cleaned_input):
            raise ValueError("Invalid email format")
    elif input_type == "number":
        if not cleaned_input.isdigit():
            raise ValueError("Input must be numeric")
    
    # HTML转义防止XSS
    safe_input = html.escape(cleaned_input)
    
    return safe_input

def sanitize_sql(input_text):
    """
    清理SQL查询中的特殊字符
    
    Args:
        input_text: 可能包含SQL特殊字符的文本
        
    Returns:
        安全的SQL参数
    """
    # 移除SQL特殊字符
    sanitized = re.sub(r"[\;\-\-\"]", "", input_text)
    return sanitized
