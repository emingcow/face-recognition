import numpy as np
from typing import Optional, Dict, Union, Tuple, List
import cv2
from .database import db
import os
import face_recognition
import insightface
import onnxruntime
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch
from PIL import Image
from torchvision import transforms

class MultiFaceService:
    def __init__(self):
        try:
            self._init_models()
            print("所有模型初始化成功")
        except Exception as e:
            print(f"模型初始化失败: {str(e)}")
            raise e

    def _check_model_files(self, model_dir: str) -> bool:
        """检查所需的模型文件是否存在"""
        print(f"\n正在检查模型目录: {model_dir}")
        
        required_files = {
            'insightface': ['models/buffalo_l/1k3d68.onnx', 'models/buffalo_l/det_10g.onnx', 'models/buffalo_l/w600k_r50.onnx'],
            'face_recognition': ['dlib_face_recognition_resnet_model_v1.dat', 'mmod_human_face_detector.dat', 'shape_predictor_68_face_landmarks.dat']
        }
        
        for model, files in required_files.items():
            model_path = os.path.join(model_dir, model)
            print(f"\n检查 {model} 模型文件:")
            for file in files:
                file_path = os.path.join(model_path, file)
                if not os.path.exists(file_path):
                    print(f"❌ 缺少模型文件: {file_path}")
                    return False
                print(f"✓ 文件存在: {file_path}")
        return True

    def _init_models(self):
        try:
            print("\n开始加载模型...")
            model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
            print(f"模型根目录: {model_dir}")
            
            # 1. InsightFace模型加载
            print("\n1/3: 正在加载InsightFace模型...")
            insightface_dir = os.path.join(model_dir, 'insightface')
            self.insight_model = insightface.app.FaceAnalysis(
                name='buffalo_l',
                root=insightface_dir,
                allowed_modules=['detection', 'recognition'],
                providers=['CPUExecutionProvider']
            )
            self.insight_model.prepare(ctx_id=0, det_thresh=0.6)
            print("✓ InsightFace模型加载成功")
            
            # 2. face_recognition模型加载
            print("\n2/3: 正加载face_recognition模型...")
            face_recognition_dir = os.path.join(model_dir, 'face_recognition')
            os.environ['FACE_RECOGNITION_MODELS'] = face_recognition_dir
            print("✓ face_recognition模型加载成功")
            
            # 3. FaceNet模型加载
            print("\n3/3: 正在加载FaceNet模型...")
            # 初始化时就将模型转换为float类型
            self.facenet = InceptionResnetV1(
                pretrained='vggface2',
                classify=False,
                device='cpu'
            ).float().eval()  # 添加 float()
            print("✓ FaceNet模型加载成功")
            
            print("\n✓ 所有模型加载完成!")
            
        except Exception as e:
            print(f"\n✗ 模型初始化失败: {str(e)}")
            raise

    def _process_image(self, image_data: bytes) -> np.ndarray:
        """优化图像预处理 - 减少不必要的处理"""
        try:
            # 1. 快速解码
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("无法解码图像数据")
            
            # 2. 只在必要时调整大小
            height, width = image.shape[:2]
            max_size = 1024
            if max(height, width) > max_size:
                scale = max_size / max(height, width)
                new_width = int(width * scale)
                new_height = int(height * scale)
                image = cv2.resize(image, (new_width, new_height), 
                                 interpolation=cv2.INTER_AREA)
            
            return image
            
        except Exception as e:
            print(f"图像处理失败: {str(e)}")
            raise

    def _evaluate_face_quality_score(self, face_image: np.ndarray) -> float:
        """评估人脸图像质量"""
        try:
            if face_image.size == 0:
                return 0.0
            
            # 1. 计算清晰度分数
            gray = cv2.cvtColor(face_image, cv2.COLOR_RGB2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            clarity_score = min(laplacian_var / 500.0, 1.0)
            
            # 2. 计算对比度分数
            contrast = np.std(gray) / 128.0
            contrast_score = min(contrast, 1.0)
            
            # 3. 计算亮度分数
            brightness = np.mean(gray) / 255.0
            brightness_score = 1.0 - abs(brightness - 0.5) * 2
            
            # 4. 计算脸大小分数
            height, width = face_image.shape[:2]
            size_score = min((height * width) / (224 * 224), 1.0)
            
            # 5. 综合评分
            quality_score = (
                clarity_score * 0.4 +
                contrast_score * 0.2 +
                brightness_score * 0.2 +
                size_score * 0.2
            )
            
            return quality_score
            
        except Exception as e:
            print(f"质量评估失败: {str(e)}")
            return 0.0

    def _calculate_optimized_similarity(self, method: str, encoding1: np.ndarray, encoding2: np.ndarray) -> float:
        """优化的相似度计算方法"""
        try:
            if encoding1 is None or encoding2 is None:
                return 0.0
            
            if encoding1.shape != encoding2.shape:
                print(f"特征维度不匹配: {encoding1.shape} vs {encoding2.shape}")
                return 0.0
            
            # 确保特征向量已经归一化
            encoding1_norm = encoding1 / np.linalg.norm(encoding1)
            encoding2_norm = encoding2 / np.linalg.norm(encoding2)
            
            # 根据不同方法使用不同的相似度计算
            if method == 'insightface':
                # InsightFace 使用余弦相似度
                similarity = np.dot(encoding1_norm, encoding2_norm)
                
            elif method == 'face_recognition':
                # face_recognition 使用欧氏距离
                distance = np.linalg.norm(encoding1_norm - encoding2_norm)
                similarity = 1.0 / (1.0 + distance)
                
            elif method == 'facenet':
                # FaceNet 使用余弦相似度
                cosine_sim = np.dot(encoding1_norm, encoding2_norm)
                # 调整到 [0,1] 范围
                similarity = (cosine_sim + 1) / 2
                
                print(f"""
                FaceNet相似度计算:
                - 余弦相似度: {cosine_sim:.4f}
                - 最终相似度: {similarity:.4f}
                """)
                
            else:
                print(f"未知的方法: {method}")
                return 0.0
            
            return float(similarity)
            
        except Exception as e:
            print(f"相似度计算错误: {str(e)}")
            return 0.0

    def _get_method_threshold(self, method: str) -> float:
        """获取每个算法的阈值"""
        thresholds = {
            'insightface': 0.35,       # InsightFace保持原阈值
            'face_recognition': 0.75,  # face_recognition保持原阈值
            'facenet': 0.65          # FaceNet设置为0.65，平衡准确率和召回率
        }
        return thresholds.get(method, 0.6)

    def register_face(self, image_data: bytes, user_data: Dict) -> Tuple[bool, str]:
        """优化的人脸注册流程"""
        try:
            if not image_data or not user_data.get('id') or not user_data.get('name'):
                return False, "缺少必要的数据"
            
            user_id: str = str(user_data['id'])
            
            # 1. 图像预处理
            image = self._process_image(image_data)
            if image is None:
                return False, "图像处理失败"
            
            # 2. 执行所有算法的检测
            encodings = {}
            failed_methods = []
            
            # 2.1 InsightFace
            print("\n尝试使用InsightFace检测人脸...")
            insight_encoding = self._get_face_encoding_insightface(image)
            if insight_encoding is not None:
                encodings['insightface'] = insight_encoding
                print("✓ InsightFace检测成功")
            else:
                failed_methods.append('insightface')
                print("✗ InsightFace检测失败")
            
            # 2.2 face_recognition
            print("\n尝试使用face_recognition检测人脸...")
            face_rec_encoding = self._get_face_encoding_face_recognition(image)
            if face_rec_encoding is not None:
                encodings['face_recognition'] = face_rec_encoding
                print("✓ face_recognition检测成功")
            else:
                failed_methods.append('face_recognition')
                print("✗ face_recognition检测失败")
            
            # 2.4 FaceNet
            print("\n尝试使用FaceNet检测人脸...")
            facenet_encoding = self._get_face_encoding_facenet(image)
            if facenet_encoding is not None:
                encodings['facenet'] = facenet_encoding
                print("✓ FaceNet检测成功")
            else:
                failed_methods.append('facenet')
                print("✗ FaceNet检测失败")
            
            # 3. 结果验证
            if len(encodings) == 0:
                return False, "所有算法都未能检测到人脸，请确保\n1. 图片中有清晰的正面人脸\n2. 光线充足\n3. 人脸角度适中"
            
            # 4. 保存数据
            try:
                db.save_user(user_data)
                db.save_face_encodings_batch(user_id, encodings)
                
                # 5. 返回结果
                success_count = len(encodings)
                total_count = 3  # 总算数量更新为3
                success_methods = list(encodings.keys())
                result_msg = f"注册功 ({success_count}/{total_count} 算法成)\n"
                result_msg += f"成功的算法: {', '.join(success_methods)}\n"
                if failed_methods:
                    result_msg += f"失败的算法: {', '.join(failed_methods)}"
                
                return True, result_msg
                
            except Exception as e:
                print(f"数保存失败: {str(e)}")
                raise
                
        except Exception as e:
            print(f"注册失败: {str(e)}")
            return False, str(e)

    def recognize_face(self, image_data: bytes) -> Tuple[bool, Union[Dict, str]]:
        """优化的人脸识别流程"""
        try:
            # 1. 图像预理
            image = self._process_image(image_data)
            if image is None:
                return False, "图像处理失败"
            
            # 2. 执行所有算法的检测
            encodings = {}
            failed_methods = []
            
            # 2.1 InsightFace
            print("\n执行 InsightFace 识别...")
            insight_encoding = self._get_face_encoding_insightface(image)
            if insight_encoding is not None:
                encodings['insightface'] = insight_encoding
                print("✓ InsightFace 识别成功")
            else:
                failed_methods.append('insightface')
                print("✗ InsightFace 识别失败")
            
            # 2.2 face_recognition
            print("\n执行 face_recognition 识别...")
            face_rec_encoding = self._get_face_encoding_face_recognition(image)
            if face_rec_encoding is not None:
                encodings['face_recognition'] = face_rec_encoding
                print("✓ face_recognition 识别成功")
            else:
                failed_methods.append('face_recognition')
                print("✗ face_recognition 识别失败")
            
            # 2.4 FaceNet
            print("\n执行 FaceNet 识别...")
            facenet_encoding = self._get_face_encoding_facenet(image)
            if facenet_encoding is not None:
                encodings['facenet'] = facenet_encoding
                print("✓ FaceNet 识别成功")
            else:
                failed_methods.append('facenet')
                print("✗ FaceNet 识别失败")
            
            if not encodings:
                return False, "所有算法都未能检测到有效人脸"
            
            # 3. 获取所有注册用户
            users = db.get_users()
            if not users:
                return False, "数库中没有注册用户"
            
            # 4. 对每个算法进行身份匹配
            method_results = {}
            all_matches = []
            
            for method, encoding in encodings.items():
                matches = []
                print(f"\n{method} 开始匹配...")
                
                for user_id, user_data in users.items():
                    stored_encoding = db.get_face_encoding(user_id, method)
                    if stored_encoding is None:
                        continue
                    
                    # 计算似度
                    similarity = self._calculate_optimized_similarity(method, encoding, stored_encoding)
                    threshold = self._get_method_threshold(method)
                    
                    print(f"与用户 {user_data['name']} 的相似度: {similarity:.4f} (阈值: {threshold})")
                    
                    if similarity > threshold:
                        matches.append({
                            'user_id': user_id,
                            'name': user_data['name'],
                            'similarity': similarity,
                            'method': method
                        })
                
                if matches:
                    # 选择最佳匹配
                    best_match = max(matches, key=lambda x: x['similarity'])
                    method_results[method] = {
                        'success': True,
                        'match': best_match
                    }
                    all_matches.append(best_match)
                    print(f"✓ {method} 最佳匹配: {best_match['name']} (相似度: {best_match['similarity']:.4f})")
                else:
                    method_results[method] = {
                        'success': False,
                        'message': '未找到匹配的人脸'
                    }
                    print(f"✗ {method} 未找到匹配")
            
            # 5. 统计投票结果
            if all_matches:
                vote_counts = {}
                total_algorithms = len(encodings)  # 成功提取特征的算法总数
                
                for match in all_matches:
                    user_id = match['user_id']
                    if user_id not in vote_counts:
                        vote_counts[user_id] = {
                            'name': match['name'],
                            'count': 0,
                            'methods': [],
                            'similarities': []
                        }
                    vote_counts[user_id]['count'] += 1
                    vote_counts[user_id]['methods'].append(match['method'])
                    vote_counts[user_id]['similarities'].append(match['similarity'])
                
                # 找到得���多的身份
                best_match = max(vote_counts.items(), key=lambda x: x[1]['count'])
                user_id, match_info = best_match
                
                # 检查是否达到多数票（超过半数算法匹配）
                if match_info['count'] <= total_algorithms / 2:
                    print(f"""
                    投票结果不足以确认身份:
                    - 总算法数: {total_algorithms}
                    - 最高得票: {match_info['count']}
                    - 投票算法: {', '.join(match_info['methods'])}
                    """)
                    return False, "未找到可靠的身份配"
                
                # 均相似度
                avg_similarity = sum(match_info['similarities']) / len(match_info['similarities'])
                
                result = {
                    'id': user_id,
                    'name': match_info['name'],
                    'vote_count': match_info['count'],
                    'total_algorithms': total_algorithms,
                    'voting_methods': match_info['methods'],
                    'average_similarity': avg_similarity,
                    'method_results': method_results
                }
                
                print(f"""
                身份别成功:
                - 用户: {result['name']}
                - 得票数: {result['vote_count']}/{total_algorithms}
                - 投票算法: {', '.join(result['voting_methods'])}
                - 平均相似度: {avg_similarity:.4f}
                """)
                
                return True, result
            
            return False, "未找到配的身份"
            
        except Exception as e:
            print(f"识别过程发生错误: {str(e)}")
            return False, str(e)

    def _get_face_encoding_insightface(self, image: np.ndarray) -> Optional[np.ndarray]:
        """统一的InsightFace特提取方法"""
        try:
            print("InsightFace处理中...")
            
            # 1. 使用固定的配置
            self.insight_model.prepare(
                ctx_id=0,
                det_thresh=0.6,      # 统一的阈值
                det_size=(640, 640)  # 统一的尺寸
            )
            
            # 2. 直接检测
            faces = self.insight_model.get(image)
            
            if faces:
                # 3. 选择最佳人脸
                best_face = max(faces, key=lambda x: x.det_score)
                if best_face.det_score < 0.6:  # 统一的质量阈值
                    print(f"人质量得分过低: {best_face.det_score:.4f}")
                    return None
                    
                # 4. 特征提取和归一化
                embedding = best_face.embedding
                embedding = embedding / np.linalg.norm(embedding)
                
                print(f"检测到高质量人脸，得分: {best_face.det_score:.4f}")
                return embedding
            
            print("未检测到人脸")
            return None
            
        except Exception as e:
            print(f"InsightFace处理错误: {str(e)}")
            return None

    def _get_face_encoding_face_recognition(self, image: np.ndarray) -> Optional[np.ndarray]:
        """统一的face_recognition特征提取方法"""
        try:
            # 1. 图像预处理
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # 1.1 直方图均衡化
            lab = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            cl = clahe.apply(l)
            enhanced_lab = cv2.merge((cl,a,b))
            enhanced_image = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2RGB)
            
            # 2. 人脸检测
            # 2.1 使用CNN检测器
            locations = face_recognition.face_locations(
                enhanced_image,
                model="cnn",
                number_of_times_to_upsample=1
            )
            
            # 2.2 如果CNN失败，使用HOG检测器
            if not locations:
                print("CNN检测失败，尝试HOG检测器...")
                locations = face_recognition.face_locations(
                    enhanced_image,
                    model="hog",
                    number_of_times_to_upsample=2
                )
            
            if not locations:
                print("未检测到人脸")
                return None
            
            # 3. 选择最佳人脸
            best_location = None
            best_quality = 0
            
            for location in locations:
                top, right, bottom, left = location
                face_image = enhanced_image[top:bottom, left:right]
                
                # 3.1 计算质量分数
                quality_score = self._evaluate_face_quality_score(face_image)
                
                # 3.2 计算大小分数
                face_size = (right - left) * (bottom - top)
                size_score = min(face_size / (150 * 150), 1.0)
                
                # 3.3 计算位置分数
                center_x = (left + right) / 2 / enhanced_image.shape[1]
                center_y = (top + bottom) / 2 / enhanced_image.shape[0]
                position_score = 1 - (abs(0.5 - center_x) + abs(0.5 - center_y))
                
                # 3.4 综合评分
                total_score = (
                    quality_score * 0.4 +
                    size_score * 0.3 +
                    position_score * 0.3
                )
                
                if total_score > best_quality:
                    best_quality = total_score
                    best_location = location
            
            if best_quality < 0.5:
                print(f"最佳人脸质量得分过低: {best_quality:.4f}")
                return None
            
            # 4. 特征提取
            encodings = face_recognition.face_encodings(
                enhanced_image,
                known_face_locations=[best_location],
                num_jitters=5,     # 使用固定的抖动次数
                model="large"      # 使用大模
            )
            
            if not encodings:
                print("特征提取失败")
                return None
            
            encoding = encodings[0]
            
            # 5. 特征归一化
            encoding = encoding / np.linalg.norm(encoding)
            
            print(f"""
            face_recognition特征提取成功:
            - 质量得分: {best_quality:.4f}
            - 人脸位置: {best_location}
            - 人脸大小: {best_location[1]-best_location[3]}x{best_location[2]-best_location[0]}
            """)
            
            return encoding
            
        except Exception as e:
            print(f"face_recognition处理错误: {str(e)}")
            return None

    def _get_face_encoding_facenet(self, image: np.ndarray) -> Optional[np.ndarray]:
        """完全重写的FaceNet特征提取方法"""
        try:
            print("\n=== FaceNet特征提取开始 ===")
            
            def preprocess_face(face_img: np.ndarray) -> torch.Tensor:
                """优化的人脸预处理"""
                try:
                    print("\n1. 开始预处理...")
                    # 1. 调整大小
                    face_resized = cv2.resize(face_img, (160, 160))
                    print(f"- 调整大小后: shape={face_resized.shape}")
                    
                    # 2. 转换为float32并归一化
                    face_float = face_resized.astype(np.float32) / 255.0
                    print(f"- 归一化后范围: [{face_float.min():.4f}, {face_float.max():.4f}]")
                    
                    # 3. 标准化
                    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
                    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
                    face_normalized = (face_float - mean) / std
                    print(f"- 标准化后范围: [{face_normalized.min():.4f}, {face_normalized.max():.4f}]")
                    
                    # 4. 转换为tensor
                    face_tensor = torch.from_numpy(face_normalized).permute(2, 0, 1).unsqueeze(0)
                    print(f"- 最终tensor: shape={face_tensor.shape}, dtype={face_tensor.dtype}")
                    
                    return face_tensor
                except Exception as e:
                    print(f"预处理错误: {str(e)}")
                    raise
            
            # 1. 使用 InsightFace 的检测器进行人脸检测
            print("\n2. 人脸检测...")
            faces = self.insight_model.get(image)
            
            if faces:
                print(f"- 检测到 {len(faces)} 个人脸")
                # 2. 选择最佳人脸
                best_face = max(faces, key=lambda x: x.det_score)
                bbox = best_face.bbox.astype(int)
                det_score = best_face.det_score
                print(f"- 最佳人脸得分: {det_score:.4f}")
                
                # 3. 提取人脸区域
                x1, y1, x2, y2 = bbox
                margin = int(min(x2-x1, y2-y1) * 0.3)
                face_img = image[
                    max(0, y1-margin):min(image.shape[0], y2+margin),
                    max(0, x1-margin):min(image.shape[1], x2+margin)
                ]
                print(f"- 提取的人脸区域: shape={face_img.shape}")
                
                # 4. 转换为RGB
                face_rgb = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
                
                # 5. 特征提取
                print("\n3. 开始特征提取...")
                face_tensor = preprocess_face(face_rgb)
                
                with torch.no_grad():
                    # 检查模型状态
                    print(f"\n4. 模型息:")
                    print(f"- 模型类型: {type(self.facenet)}")
                    print(f"- 模型设备: {next(self.facenet.parameters()).device}")
                    print(f"- 模型状态: {'eval' if self.facenet.training == False else 'train'}")
                    
                    # 提取特征
                    embedding = self.facenet(face_tensor)
                    print(f"\n5. 原始特征:")
                    print(f"- shape: {embedding.shape}")
                    print(f"- range: [{embedding.min().item():.4f}, {embedding.max().item():.4f}]")
                    print(f"- mean: {embedding.mean().item():.4f}")
                    print(f"- std: {embedding.std().item():.4f}")
                    
                    # 转换为numpy并归一化
                    embedding = embedding.cpu().numpy().flatten()
                    embedding = embedding / np.linalg.norm(embedding)
                    
                    print(f"\n6. 归一化后特征:")
                    print(f"- shape: {embedding.shape}")
                    print(f"- range: [{embedding.min():.4f}, {embedding.max():.4f}]")
                    print(f"- mean: {embedding.mean():.4f}")
                    print(f"- std: {embedding.std():.4f}")
                    print(f"- norm: {np.linalg.norm(embedding):.4f}")
                    
                    return embedding
            
            print("未检测到人脸")
            return None
            
        except Exception as e:
            print(f"FaceNet处理错误: {str(e)}")
            print(f"错误类型: {type(e)}")
            print(f"错误位置: {e.__traceback__.tb_frame.f_code.co_filename}:{e.__traceback__.tb_lineno}")
            return None

    def _rotate_tensor(self, tensor: torch.Tensor, angle: float) -> Optional[torch.Tensor]:
        """辅助函数：旋转图像张量"""
        try:
            # 转换为PIL图像
            image = transforms.ToPILImage()(tensor)
            # 转
            rotated = image.rotate(angle, expand=True)
            # 转回tensor
            return transforms.ToTensor()(rotated)
        except Exception as e:
            print(f"图像旋转失败: {str(e)}")
            return None

    def _compare_facenet_embeddings(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """深度优化的特征比对方法"""
        try:
            print("\n=== 开始特征比对 ===")
            
            # 1. 基础验证
            if embedding1 is None or embedding2 is None:
                print("特征向量为空")
                return 0.0
            
            print(f"\n1. 特征向量信息:")
            print(f"- 特征1: shape={embedding1.shape}, dtype={embedding1.dtype}")
            print(f"- 特征2: shape={embedding2.shape}, dtype={embedding2.dtype}")
            print(f"- 特征1范围: [{embedding1.min():.4f}, {embedding1.max():.4f}]")
            print(f"- 特征2范围: [{embedding2.min():.4f}, {embedding2.max():.4f}]")
            print(f"- 特征1均值: {embedding1.mean():.4f}")
            print(f"- 特征2均值: {embedding2.mean():.4f}")
            
            if embedding1.shape != embedding2.shape:
                print(f"特征维度不匹配")
                return 0.0
            
            # 2. 检查特征向量是否包含 NaN 或 Inf
            if np.any(np.isnan(embedding1)) or np.any(np.isnan(embedding2)):
                print("特征向量包含 NaN")
                return 0.0
            
            if np.any(np.isinf(embedding1)) or np.any(np.isinf(embedding2)):
                print("特征向量包含 Inf")
                return 0.0
            
            # 3. 确保特征向量已经归一化
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            
            if norm1 == 0 or norm2 == 0:
                print("特征向量范数为0")
                return 0.0
            
            embedding1_norm = embedding1 / norm1
            embedding2_norm = embedding2 / norm2
            
            print(f"\n2. 归一化后的特征:")
            print(f"- 特征1范数: {np.linalg.norm(embedding1_norm):.4f}")
            print(f"- 特征2范数: {np.linalg.norm(embedding2_norm):.4f}")
            
            # 4. 计算相似度
            cosine_sim = np.dot(embedding1_norm, embedding2_norm)
            print(f"\n3. 原始余弦相似度: {cosine_sim:.4f}")
            
            # 5. 归一化到 [0,1] 范围
            similarity = (cosine_sim + 1) / 2
            print(f"4. 最终相似度: {similarity:.4f}")
            
            # 6. 添加额外的相似度检查
            l2_dist = np.linalg.norm(embedding1_norm - embedding2_norm)
            print(f"5. L2距离: {l2_dist:.4f}")
            
            # 7. 检查特征向量是否完全相同
            is_identical = np.allclose(embedding1_norm, embedding2_norm, rtol=1e-5, atol=1e-8)
            print(f"6. 特征向量是否完全相同: {is_identical}")
            
            return float(similarity)
            
        except Exception as e:
            print(f"特征比对错误: {str(e)}")
            print(f"错误类型: {type(e)}")
            return 0.0

    def _evaluate_feature_quality(self, embedding: np.ndarray) -> float:
        """评估特征向量的质量"""
        try:
            # 1. 检查特征向量的范数
            norm = np.linalg.norm(embedding)
            if not 0.99 < norm < 1.01:  # 检查是否接近单位向量
                return 0.5
            
            # 2. 检查特征分布
            mean = np.mean(embedding)
            std = np.std(embedding)
            if abs(mean) > 0.1 or std < 0.1:  # 检查是否分布合理
                return 0.7
            
            # 3. 检查特征稀疏性
            sparsity = np.sum(np.abs(embedding) < 0.01) / len(embedding)
            if sparsity > 0.9:  # 太���疏的特征可能质量不好
                return 0.8
            
            # 4. 综合评分
            quality_score = (
                0.4 * (1.0 - abs(1.0 - norm)) +  # 范数接近1.0
                0.3 * (1.0 - abs(mean)) +        # 均值接近0
                0.3 * (1.0 - sparsity)           # 适度的稀疏性
            )
            
            return float(quality_score)
            
        except Exception as e:
            print(f"特征质量评估错误: {str(e)}")
            return 0.5  # 返回中等质量分数作为默认值

    def _match_face_facenet(self, encoding: np.ndarray, user_encodings: Dict[str, np.ndarray], 
                           threshold: float = 0.4) -> Tuple[bool, float]:
        """优化的FaceNet人脸匹配方法"""
        try:
            print("\n=== 开始FaceNet匹配 ===")
            
            if 'facenet' not in user_encodings:
                print("用户特征中没有facenet特征")
                return False, 0.0
            
            stored_encoding = user_encodings['facenet']
            
            # 1. 基本验证
            if encoding is None or stored_encoding is None:
                print("特征向量为空")
                return False, 0.0
            
            # 2. 打印特征信息
            print(f"""
            当前特征:
            - shape: {encoding.shape}
            - range: [{encoding.min():.4f}, {encoding.max():.4f}]
            - mean: {encoding.mean():.4f}
            - std: {encoding.std():.4f}
            - norm: {np.linalg.norm(encoding):.4f}
            """)
            
            print(f"""
            存储特征:
            - shape: {stored_encoding.shape}
            - range: [{stored_encoding.min():.4f}, {stored_encoding.max():.4f}]
            - mean: {stored_encoding.mean():.4f}
            - std: {stored_encoding.std():.4f}
            - norm: {np.linalg.norm(stored_encoding):.4f}
            """)
            
            # 3. 维度检查
            if encoding.shape != stored_encoding.shape:
                print(f"特征维度不匹配: {encoding.shape} vs {stored_encoding.shape}")
                return False, 0.0
            
            # 4. 计算相似度
            similarity = self._compare_facenet_embeddings(encoding, stored_encoding)
            
            # 5. 动态阈值调整
            quality_score = self._calculate_feature_quality(encoding)
            adjusted_threshold = threshold * (1.0 - 0.2 * quality_score)
            
            # 6. 置信度评估
            is_match = similarity > adjusted_threshold
            
            print(f"""
            匹配结果:
            - 原始相似度: {similarity:.4f}
            - 特征质量: {quality_score:.4f}
            - 基准阈值: {threshold:.4f}
            - 调整后阈值: {adjusted_threshold:.4f}
            - 匹配结果: {'✓' if is_match else '✗'}
            """)
            
            return is_match, similarity
            
        except Exception as e:
            print(f"FaceNet匹配错误: {str(e)}")
            print(f"错误类型: {type(e)}")
            return False, 0.0

    def _calculate_feature_quality(self, embedding: np.ndarray) -> float:
        """评估特征向量的质量"""
        try:
            # 1. 检查特征向量的范数
            norm = np.linalg.norm(embedding)
            if not 0.99 < norm < 1.01:  # 检查是否接近单位向量
                return 0.0
            
            # 2. 检查特征分布
            mean = np.mean(embedding)
            std = np.std(embedding)
            if abs(mean) > 0.1 or std < 0.1:  # 检查是否分布合理
                return 0.5
            
            # 3. 检查特征稀疏性
            sparsity = np.sum(np.abs(embedding) < 0.01) / len(embedding)
            if sparsity > 0.9:  # 太稀疏的特征可能质量不好
                return 0.7
            
            # 4. 综合评分
            quality_score = (
                0.4 * (1.0 - abs(1.0 - norm)) +  # 范数接近1.0
                0.3 * (1.0 - abs(mean)) +        # 均值接0
                0.3 * (1.0 - sparsity)           # 适度的稀疏性
            )
            
            return float(quality_score)
            
        except Exception as e:
            print(f"特征质量评估错误: {str(e)}")
            return 0.0

# 在文件最后添加这行代码
face_service = MultiFaceService()
