import os
import insightface
import face_recognition
import numpy as np
import time
import sys
from tqdm import tqdm
import signal
import urllib.request
import socket
import ssl
import bz2
from typing import Optional, Dict
import json
from concurrent.futures import ThreadPoolExecutor
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch

# 设置全局超时
socket.setdefaulttimeout(30)

def signal_handler(signum, frame):
    print("\n\n程序被强制中断")
    sys.exit(1)

signal.signal(signal.SIGINT, signal_handler)

# 定义需要下载的模型文件
required_models = {
    'insightface': {
        'files': ['buffalo_l/1k3d68.onnx', 'buffalo_l/det_10g.onnx', 'buffalo_l/w600k_r50.onnx'],
        'dir': 'insightface'
    },
    'face_recognition': {
        'files': [
            'shape_predictor_68_face_landmarks.dat',
            'dlib_face_recognition_resnet_model_v1.dat',
            'mmod_human_face_detector.dat'
        ],
        'dir': 'face_recognition'
    },
    'facenet': {
        'files': [
            'casia_weights.pt',  # CASIA-WebFace 模型
            'vggface2_weights.pt',  # VGGFace2 模型
            'mtcnn_weights.pt'  # MTCNN 模型
        ],
        'dir': 'facenet'
    }
}

def download_with_progress(url: str, dest_path: str, desc: Optional[str] = None):
    """改进的下载函数"""
    try:
        max_retries = 5
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                
                first_byte = 0
                if os.path.exists(dest_path):
                    first_byte = os.path.getsize(dest_path)
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                        'Accept': '*/*',
                        'Connection': 'keep-alive',
                        'Range': f'bytes={first_byte}-'
                    }
                else:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                        'Accept': '*/*',
                        'Connection': 'keep-alive'
                    }
                
                req = urllib.request.Request(url, headers=headers)
                
                with urllib.request.urlopen(req, context=context, timeout=60) as response:
                    file_size = int(response.headers.get('Content-Length', 0))
                    if 'Content-Range' in response.headers:
                        file_size = int(response.headers['Content-Range'].split('/')[-1])
                    
                    with tqdm(total=file_size, initial=first_byte,
                            unit='B', unit_scale=True, desc=desc) as pbar:
                        with open(dest_path, 'ab' if first_byte else 'wb') as f:
                            while True:
                                chunk = response.read(128 * 1024)
                                if not chunk:
                                    break
                                f.write(chunk)
                                pbar.update(len(chunk))
                
                if os.path.getsize(dest_path) == file_size:
                    print(f"\n✓ {desc} 下载成功")
                    break
                else:
                    raise Exception("文件大小不匹配，重试下载")
                
            except Exception as e:
                retry_count += 1
                print(f"\n下载失败 ({retry_count}/{max_retries}): {str(e)}")
                if retry_count == max_retries:
                    raise
                print(f"等待 {retry_count * 2} 秒后重试...")
                time.sleep(retry_count * 2)
                
    except Exception as e:
        print(f"\n下载失败: {str(e)}")
        if os.path.exists(dest_path):
            os.remove(dest_path)
        raise

def verify_model_exists(model_dir: str, models: Dict) -> bool:
    """验证模型文件是否存在"""
    for model_name, model_info in models.items():
        model_path = os.path.join(model_dir, model_info['dir'])
        for file in model_info['files']:
            file_path = os.path.join(model_path, file)
            if not os.path.exists(file_path):
                return False
    return True

def download_models():
    try:
        model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
        os.makedirs(model_dir, exist_ok=True)
        
        print("\n检查现有模型...")
        
        # 1. 检查和下载InsightFace模型
        print("\n[1/3] 检查InsightFace模型...")
        insightface_dir = os.path.join(model_dir, 'insightface')
        if verify_model_exists(model_dir, {'insightface': required_models['insightface']}):
            print("✓ InsightFace模型已存在，跳过下载")
        else:
            print("开始下载InsightFace模型...")
            os.makedirs(insightface_dir, exist_ok=True)
            face_analyzer = insightface.app.FaceAnalysis(
                name='buffalo_l',
                root=insightface_dir,
                allowed_modules=['detection', 'recognition'],
                providers=['CPUExecutionProvider']
            )
            face_analyzer.prepare(ctx_id=0, det_thresh=0.6)
            print("✓ InsightFace模型下载完成")
        
        # 2. 检查和下载face_recognition模型
        print("\n[2/3] 检查face_recognition模型...")
        face_recognition_dir = os.path.join(model_dir, 'face_recognition')
        if verify_model_exists(model_dir, {'face_recognition': required_models['face_recognition']}):
            print("✓ face_recognition模型已存在，跳过下载")
        else:
            print("开始下载face_recognition模型...")
            os.makedirs(face_recognition_dir, exist_ok=True)
            
            model_urls = {
                'shape_predictor_68_face_landmarks.dat': 'https://ghproxy.com/https://github.com/davisking/dlib-models/raw/master/shape_predictor_68_face_landmarks.dat.bz2',
                'dlib_face_recognition_resnet_model_v1.dat': 'https://ghproxy.com/https://github.com/davisking/dlib-models/raw/master/dlib_face_recognition_resnet_model_v1.dat.bz2',
                'mmod_human_face_detector.dat': 'https://ghproxy.com/https://github.com/davisking/dlib-models/raw/master/mmod_human_face_detector.dat.bz2'
            }
            
            for model_name, url in model_urls.items():
                model_path = os.path.join(face_recognition_dir, model_name)
                if not os.path.exists(model_path):
                    try:
                        download_with_progress(url, model_path + '.bz2', model_name)
                        print(f"解压 {model_name}...")
                        with open(model_path, 'wb') as new_file:
                            with bz2.BZ2File(model_path + '.bz2') as file:
                                new_file.write(file.read())
                        os.remove(model_path + '.bz2')
                    except Exception as e:
                        print(f"{model_name} 下载失败: {str(e)}")
                        raise
            
            print("✓ face_recognition模型下载完成")
        
        # 3. 检查和下载FaceNet模型
        print("\n[3/3] 检查FaceNet模型...")
        facenet_dir = os.path.join(model_dir, 'facenet')
        if verify_model_exists(model_dir, {'facenet': required_models['facenet']}):
            print("✓ FaceNet模型已存在，跳过下载")
        else:
            print("开始下载FaceNet模型...")
            os.makedirs(facenet_dir, exist_ok=True)
            
            try:
                # 1. 下载优化的MTCNN
                print("\n1. 下载MTCNN模型...")
                mtcnn = MTCNN(
                    image_size=160,
                    margin=14,
                    min_face_size=40,
                    thresholds=[0.7, 0.8, 0.8],
                    factor=0.709,
                    post_process=True,
                    device='cpu',
                    selection_method='probability'
                )
                mtcnn_path = os.path.join(facenet_dir, 'mtcnn_weights.pt')
                torch.save(mtcnn.state_dict(), mtcnn_path)
                print("✓ MTCNN模型下载完成")
                
                # 2. 下载CASIA-WebFace模型
                print("\n2. 下载CASIA-WebFace模型...")
                resnet_casia = InceptionResnetV1(
                    pretrained='casia-webface',
                    classify=True,
                    num_classes=10575,
                    device='cpu'
                ).eval()
                casia_path = os.path.join(facenet_dir, 'casia_weights.pt')
                torch.save(resnet_casia.state_dict(), casia_path)
                print("✓ CASIA-WebFace模型下载完成")
                
                # 3. 下载VGGFace2模型
                print("\n3. 下载VGGFace2模型...")
                resnet_vgg = InceptionResnetV1(
                    pretrained='vggface2',
                    classify=True,
                    num_classes=8631,
                    device='cpu'
                ).eval()
                vgg_path = os.path.join(facenet_dir, 'vggface2_weights.pt')
                torch.save(resnet_vgg.state_dict(), vgg_path)
                print("✓ VGGFace2模型下载完成")
                
                print("\n✓ FaceNet所有模型下载完成!")
                
            except Exception as e:
                print(f"FaceNet模型下载失败: {str(e)}")
                raise
        
        print("\n✓ 所有模型检查/下载完成!")
        
        # 更新配置文件
        config_path = os.path.join(model_dir, 'model_config.json')
        model_configs = {
            'insightface': {
                'det_thresh': 0.6,
                'det_size': [640, 640]
            },
            'face_recognition': {
                'num_jitters': 100,
                'model': 'large',
                'number_of_times_to_upsample': 2,
                'batch_size': 32
            },
            'facenet': {
                'image_size': 160,
                'margin': 14,
                'min_face_size': 40,
                'thresholds': [0.7, 0.8, 0.8],
                'factor': 0.709
            }
        }

        with open(config_path, 'w') as f:
            json.dump(model_configs, f, indent=4)
        
    except Exception as e:
        print(f"\n✗ 模型下载过程中出现错误: {str(e)}")
        raise

if __name__ == '__main__':
    download_models() 