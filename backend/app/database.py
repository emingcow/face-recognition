import json
import os
import numpy as np
from typing import Dict, Optional, Any

class Database:
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        self.users_file = os.path.join(self.data_dir, 'users.json')
        self.encodings_dir = os.path.join(self.data_dir, 'encodings')
        
        # 创建必要的目录
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.encodings_dir, exist_ok=True)
        
        # 初始化用户数据
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)

    def save_user(self, user_data: Dict):
        """保存用户数据"""
        try:
            # 数据验证
            if not isinstance(user_data, dict):
                raise ValueError("用户数据必须是字典类型")
            
            if 'id' not in user_data or 'name' not in user_data:
                raise ValueError("用户数据必须包含id和name字段")
            
            # 确保id是字符串类型
            user_id = str(user_data['id'])
            user_data['id'] = user_id
            
            # 读取现有用户数据
            users = {}
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    users = json.load(f)
            
            # 更新用户数据
            users[user_id] = user_data
            
            # 保存用户数据
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(users, f, ensure_ascii=False, indent=2)
            
            print(f"用户数据保存成功: {user_id}")
            
        except Exception as e:
            print(f"保存用户数据失败: {str(e)}")
            raise

    def save_face_encodings_batch(self, user_id: str, encodings: Dict[str, np.ndarray]):
        """批量保存人脸编码"""
        try:
            for method, encoding in encodings.items():
                encoding_file = os.path.join(self.encodings_dir, f"{user_id}_{method}.npy")
                np.save(encoding_file, encoding)
                print(f"保存{method}编码成功: {user_id}")
                
        except Exception as e:
            print(f"保存人脸编码失败: {str(e)}")
            raise

    def get_users(self) -> Dict:
        """获取所有用户"""
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"获取用户数据失败: {str(e)}")
            return {}

    def get_face_encoding(self, user_id: str, method: str) -> Optional[np.ndarray]:
        """获取人脸编码"""
        try:
            encoding_file = os.path.join(self.encodings_dir, f"{user_id}_{method}.npy")
            if os.path.exists(encoding_file):
                return np.load(encoding_file)
            return None
        except Exception as e:
            print(f"获取人脸编码失败: {str(e)}")
            return None

db = Database() 