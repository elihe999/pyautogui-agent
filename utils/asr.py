import requests
import os
from typing import Optional


def transcribe_audio(
    audio_file_path: str,
    host: str = "localhost",
    port: int = 9000,
    encode: bool = True,
    task: str = "transcribe",
    language: str = "zh",
    vad_filter: bool = False,
    word_timestamps: bool = False,
    output_format: str = "txt"
) -> Optional[str]:
    """
    通过HTTP调用ASR服务转录音频文件
    
    Args:
        audio_file_path: 音频文件路径
        host: ASR服务主机地址
        port: ASR服务端口号
        encode: 是否编码
        task: 任务类型，默认为"transcribe"
        language: 语言，默认为"zh"
        vad_filter: 是否使用VAD过滤，默认为False
        word_timestamps: 是否返回单词时间戳，默认为False
        output_format: 输出格式，默认为"txt"
        
    Returns:
        转录结果字符串，如果失败则返回None
    """
    url = f"http://{host}:{port}/asr"
    
    params = {
        "encode": str(encode).lower(),
        "task": task,
        "language": language,
        "vad_filter": str(vad_filter).lower(),
        "word_timestamps": str(word_timestamps).lower(),
        "output": output_format
    }
    
    headers = {
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
        "accept": "application/json"
        # 注意：不要手动设置content-type，requests会自动设置正确的boundary
    }
    
    if not os.path.exists(audio_file_path):
        print(f"音频文件不存在: {audio_file_path}")
        return None
    
    try:
        with open(audio_file_path, 'rb') as audio_file:
            files = {'audio_file': (os.path.basename(audio_file_path), audio_file, 'audio/wav')}
            
            response = requests.post(
                url=url,
                params=params,
                headers=headers,
                files=files
            )
            
            if response.status_code == 200:
                # 根据输出格式处理响应
                if output_format.lower() == "json":
                    return response.json()
                else:
                    return response.text
            else:
                print(f"ASR请求失败，状态码: {response.status_code}, 响应: {response.text}")
                return None
                
    except requests.exceptions.RequestException as e:
        print(f"请求ASR服务时发生错误: {e}")
        return None
    except Exception as e:
        print(f"处理音频文件时发生错误: {e}")
        return None


def transcribe_recorded_audio(
    recorded_file_path: str,
    output_file_path: Optional[str] = None
) -> Optional[str]:
    """
    转录录音文件
    
    Args:
        recorded_file_path: 录音文件路径
        output_file_path: 可选，保存转录结果的文件路径
        
    Returns:
        转录结果字符串
    """
    result = transcribe_audio(
        audio_file_path=recorded_file_path,
        language="zh"
    )
    
    if result and output_file_path:
        try:
            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"转录结果已保存到: {output_file_path}")
        except Exception as e:
            print(f"保存转录结果时发生错误: {e}")
    
    return result


if __name__ == "__main__":
    # 示例用法
    # result = transcribe_audio("./recording.wav")  # 使用record.py生成的录音文件
    # print("转录结果:", result)
    pass