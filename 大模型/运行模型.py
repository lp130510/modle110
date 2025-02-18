from modelscope import AutoModelForCausalLM, AutoTokenizer

# 模型名称或本地路径
model_name = "D:\\模型文件保存"

# 加载模型和分词器
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# 准备输入提示
prompt = "Give me a short introduction to large language model."
messages = [
    {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
    {"role": "user", "content": prompt}
]

# 应用对话模板
text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True
)

# 准备模型输入
model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

# 生成文本
generated_ids = model.generate(
    **model_inputs,
    max_new_tokens=512
)

# 提取生成的文本
generated_ids = [
    output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
]

# 解码生成的文本
response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
print(response)
