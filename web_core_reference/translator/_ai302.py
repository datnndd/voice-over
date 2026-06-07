from dataclasses import dataclass

from web_core_reference.configure.config import params
from web_core_reference.translator._openaicompat import OpenAICampat


@dataclass
class AI302(OpenAICampat):
    def __post_init__(self):
        self.ainame="ai302"
        self.model_name = params.get('ai302_model','')
        self.api_key=params.get("ai302_key","")
        self.api_url='https://api.302.ai/v1/'
        self.max_tokens=65536
        super().__post_init__()
