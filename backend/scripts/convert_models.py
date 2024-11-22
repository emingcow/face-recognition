import torch
import onnx
import os

def convert_pytorch_to_onnx(model_path, save_path, input_shape=(1, 3, 112, 112)):
    """将PyTorch模型转换为ONNX格式"""
    import torch
    
    # 加载模型
    model = torch.load(model_path, map_location='cpu')
    model.eval()
    
    # 创建随机输入
    dummy_input = torch.randn(input_shape)
    
    # 导出ONNX
    torch.onnx.export(
        model,
        dummy_input,
        save_path,
        export_params=True,
        opset_version=11,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={
            'input': {0: 'batch_size'},
            'output': {0: 'batch_size'}
        }
    )
    
    # 验证ONNX模型
    onnx_model = onnx.load(save_path)
    onnx.checker.check_model(onnx_model)
    print(f"模型已成功转换并保存到: {save_path}")

def download_and_convert():
    # 创建模型目录
    model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
    
    # 1. AdaFace
    print("转换 AdaFace 模型...")
    adaface_dir = os.path.join(model_dir, 'adaface')
    os.makedirs(adaface_dir, exist_ok=True)
    
    # 下载PyTorch模型
    torch.hub.download_url_to_file(
        'https://github.com/mk-minchul/AdaFace/releases/download/v1.0/adaface_ir50_ms1mv2.pth',
        os.path.join(adaface_dir, 'adaface_ir50_ms1mv2.pth')
    )
    
    # 转换为ONNX
    convert_pytorch_to_onnx(
        os.path.join(adaface_dir, 'adaface_ir50_ms1mv2.pth'),
        os.path.join(adaface_dir, 'adaface_ir50_ms1mv2.onnx')
    )
    
    # 2. CosFace
    print("转换 CosFace 模型...")
    cosface_dir = os.path.join(model_dir, 'cosface')
    os.makedirs(cosface_dir, exist_ok=True)
    
    # 下载PyTorch模型
    torch.hub.download_url_to_file(
        'https://github.com/deepinsight/insightface/releases/download/v0.7/ms1mv3_arcface_r50_fp16.pth',
        os.path.join(cosface_dir, 'cosface_resnet50.pth')
    )
    
    # 转换为ONNX
    convert_pytorch_to_onnx(
        os.path.join(cosface_dir, 'cosface_resnet50.pth'),
        os.path.join(cosface_dir, 'cosface_resnet50.onnx')
    )
    
    # 3. SphereFace
    print("转换 SphereFace 模型...")
    sphereface_dir = os.path.join(model_dir, 'sphereface')
    os.makedirs(sphereface_dir, exist_ok=True)
    
    # 下载PyTorch模型
    torch.hub.download_url_to_file(
        'https://github.com/wy1iu/sphereface/releases/download/v1.0/sphereface_resnet50.pth',
        os.path.join(sphereface_dir, 'sphereface_resnet50.pth')
    )
    
    # 转换为ONNX
    convert_pytorch_to_onnx(
        os.path.join(sphereface_dir, 'sphereface_resnet50.pth'),
        os.path.join(sphereface_dir, 'sphereface_resnet50.onnx')
    )

if __name__ == "__main__":
    download_and_convert() 