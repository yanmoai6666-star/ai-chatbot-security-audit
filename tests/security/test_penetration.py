"""
渗透测试用例
"""
import unittest
from src.security.input_validator import validate_input, sanitize_sql
from src.auth.middleware import authenticate

class TestPenetration(unittest.TestCase):
    
    def test_sql_injection_prevention(self):
        """测试SQL注入防护"""
        malicious_input = "test'; DROP TABLE users; --"
        safe_input = sanitize_sql(malicious_input)
        self.assertNotIn(";", safe_input)
        self.assertNotIn("--", safe_input)
        self.assertEqual(safe_input, "test DROP TABLE users ")
    
    def test_xss_prevention(self):
        """测试XSS防护"""
        malicious_input = "<script>alert('xss')</script>"
        safe_input = validate_input(malicious_input)
        self.assertIn("&lt;script&gt;", safe_input)
        self.assertIn("&lt;/script&gt;", safe_input)
        self.assertNotIn("<script>", safe_input)
    
    def test_authentication_bypass(self):
        """测试认证绕过漏洞"""
        # 测试无效凭据
        token = authenticate("admin", "wrong_password")
        self.assertIsNone(token)
        
        # 测试SQL注入式用户名
        token = authenticate("admin' --", "any_password")
        self.assertIsNone(token)

if __name__ == "__main__":
    unittest.main()
