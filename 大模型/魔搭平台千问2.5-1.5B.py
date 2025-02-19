import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from modelscope import AutoModelForCausalLM, AutoTokenizer
import torch
import uvicorn

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

# 指定模型本地路径
model_path = r"D:\gguf\qwenQwen2.5-1.5B-Instruct"
model_name = "qwen/Qwen2.5-1.5B-Instruct"

# 定义请求数据模型
class GenerateRequest(BaseModel):
    prompt: str

try:
    logging.info("正在尝试加载模型...")
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype="auto",
        device_map="auto",
        cache_dir=model_path
    )
    logging.info("模型加载成功！")
except Exception as e:
    logging.error(f"模型加载失败: {e}")
    raise

try:
    logging.info("正在尝试加载分词器...")
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        cache_dir=model_path
    )
    logging.info("分词器加载成功！")
except Exception as e:
    logging.error(f"分词器加载失败: {e}")
    raise


@app.post("/generate")
async def generate_text(request: GenerateRequest):
    try:
        prompt = request.prompt
        messages = [
            {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=512
        )
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating text: {str(e)}")


if __name__ == "__main__":
    try:
        logging.info("正在启动 FastAPI 服务...")
        uvicorn.run(app, host="0.0.0.0", port=8012)
    except Exception as e:
        logging.error(f"服务启动失败: {e}")
