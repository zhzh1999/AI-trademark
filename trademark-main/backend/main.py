########################################
# backend/main.py
########################################

from openai import OpenAI
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict


# 初始化 OpenAI 客户端
client = OpenAI(api_key="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")

# 定义 Pydantic 数据模型，用于描述解析结果
class TrademarkTranslation(BaseModel):
    US: str = Field(..., description="美国的商标术语")
    China: str = Field(..., description="中国的商标术语")
    EU: str = Field(..., description="欧盟的商标术语")
    Germany: str = Field(..., description="德国的商标术语")
    Japan: str = Field(..., description="日本的商标术语")
    Korea: str = Field(..., description="韩国的商标术语")
    India: str = Field(..., description="印度的商标术语")
    UK: str = Field(..., description="英国的商标术语")
    France: str = Field(..., description="法国的商标术语")
    Russia: str = Field(..., description="俄罗斯的商标术语")



class ClassificationEntry(BaseModel):
    mainclass: int = Field(..., description="商品的大类（class）")
    subclass: int = Field(..., description="商品的子类（subclass）")

class ClassificationResponse(BaseModel):
    US: ClassificationEntry = Field(..., description="美国的商标分类")
    China: ClassificationEntry = Field(..., description="中国的商标分类")
    EU: ClassificationEntry = Field(..., description="欧盟的商标分类")
    Germany: ClassificationEntry = Field(..., description="德国的商标分类")
    Japan: ClassificationEntry = Field(..., description="日本的商标分类")
    Korea: ClassificationEntry = Field(..., description="韩国的商标分类")
    India: ClassificationEntry = Field(..., description="印度的商标分类")
    UK: ClassificationEntry = Field(..., description="英国的商标分类")
    France: ClassificationEntry = Field(..., description="法国的商标分类")
    Russia: ClassificationEntry = Field(..., description="俄罗斯的商标分类")
    
class RegistrationEntry(BaseModel):
    status: str = Field(..., description="商标的注册状态 ('Registered', 'Pending', 或 'Not Registered')")
    info: str = Field(..., description="其他相关信息，例如注册号或申请号")

class RegistrationStatusResponse(BaseModel):
    """
    用于表示功能3的返回结果
    """
    US: RegistrationEntry = Field(..., description="美国的商标注册状态")
    China: RegistrationEntry = Field(..., description="中国的商标注册状态")
    EU: RegistrationEntry = Field(..., description="欧盟的商标注册状态")
    Germany: RegistrationEntry = Field(..., description="德国的商标注册状态")
    Japan: RegistrationEntry = Field(..., description="日本的商标注册状态")
    Korea: RegistrationEntry = Field(..., description="韩国的商标注册状态")
    India: RegistrationEntry = Field(..., description="印度的商标注册状态")
    UK: RegistrationEntry = Field(..., description="英国的商标注册状态")
    France: RegistrationEntry = Field(..., description="法国的商标注册状态")
    Russia: RegistrationEntry = Field(..., description="俄罗斯的商标注册状态")

class ProductDescription(BaseModel):
    product_description: str = Field(..., example="智能手机")


class ProductAndTrademark(BaseModel):
    product_description: str = Field(..., example="智能手机")
    trademark_name: str = Field(..., example="AIPhone")


# FastAPI 实例
app = FastAPI()

# 允许跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


########################################
# 功能1：翻译商标术语
########################################
@app.post("/translate_terms", response_model=Dict[str, str])
async def translate_terms(data: ProductDescription):
    """
    输入自然语言商品描述，返回十个国家的标准化商标描述。
    """
    user_input = data.product_description

    prompt = (
        f"用户输入的商品描述：'{user_input}'\n"
        "请将其翻译成以下国家的标准化商标术语，以 JSON 格式输出："
        "美国, 中国, 欧盟, 德国, 日本, 韩国, 印度, 英国, 法国, 俄罗斯。"
    )

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "You are an expert in trademark classifications."},
            {"role": "user", "content": prompt},
        ],
        response_format=TrademarkTranslation,
    )

    # 提取解析后的结果
    parsed_result = completion.choices[0].message.parsed
    print("\n商品描述", user_input)
    print("\n商标翻译结果:", parsed_result.dict())
    return parsed_result.dict()


########################################
# 功能2：查询商品class和subclass
########################################
@app.post("/get_classification", response_model=ClassificationResponse)
async def get_classification(data: ProductDescription):
    """
    输入商品描述，查询十个国家（或地区）的 class 和 subclass。
    """
    user_input = data.product_description

    prompt = (
        f"用户输入的商品：'{user_input}'\n"
        "请为此商品提供以下国家的商标分类 (class) 和子分类 (subclass)，以 JSON 格式输出："
        "美国, 中国, 欧盟, 德国, 日本, 韩国, 印度, 英国, 法国, 俄罗斯。"
    )

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "You are an expert in global trademark classifications."},
            {"role": "user", "content": prompt},
        ],
        response_format=ClassificationResponse,  # 使用完整的结构化 Pydantic 模型
    )

    # 提取解析后的结果
    parsed_result = completion.choices[0].message.parsed
    print("\n商品描述", user_input)
    print("\n商标分类结果:", parsed_result.dict())
    return parsed_result.dict()  # 返回结构化的 JSON 数据


########################################
# 功能3：查询商标注册情况
########################################
@app.post("/get_registration_status", response_model=RegistrationStatusResponse)
async def get_registration_status(data: ProductAndTrademark):
    """
    输入商品描述和商标名称，查询商标在十个国家的注册状态。
    """
    product = data.product_description
    trademark = data.trademark_name

    prompt = (
        f"用户输入的商品描述：'{product}'，商标：'{trademark}'。\n"
        "请查询此商标在以下国家的注册状态，并以 JSON 格式输出："
        "美国, 中国, 欧盟, 德国, 日本, 韩国, 印度, 英国, 法国, 俄罗斯。\n"
        "返回的信息需包含 'status' 和 'info' 两个字段："
        "'status' 表示注册状态 ('Registered', 'Pending', 或 'Not Registered')，"
        "'info' 提供其他相关信息。"
    )

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "You are an expert in global trademark status reporting."},
            {"role": "user", "content": prompt},
        ],
        response_format=RegistrationStatusResponse,  # 使用完整的结构化 Pydantic 模型

    )

    # 提取解析后的结果
    parsed_result = completion.choices[0].message.parsed
    print("\n商品描述", product, "商标名称", trademark)
    print("\n注册状态结果:", parsed_result.dict())
    return parsed_result.dict()  # 返回结构化的 JSON 数据