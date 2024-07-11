from pydantic import BaseModel, Field
from typing import List, Union, Optional


__all__ = [
    "IndexField"
]


class IndexField(BaseModel):
    """"""
    # origin dataset
    db_name: Optional[Union[List[str], str]] = Field(None, description="数据库名")
    table_name: Optional[Union[List[str], str]] = Field(None, description="表名")
    columns: Union[List[str], str] = Field(..., description="数据列名")

    # index name
    index_name: str = Field(..., description="指标英文名")
    index_name_cn: Optional[str] = Field(None, description="指标中文名")

    # date
    start_date: Optional[str] = Field(None, description="依据start_date/end_date进行时间段内的数据衍生")
    end_date: Optional[str] = Field(None, description="依据start_date/end_date进行时间段内的数据衍生")
    load_date: Optional[str] = Field(None, description="依据load_date进行时间点的数据衍生")

    origin_op: Optional[str] = Field(None, description="在衍生之前需要处理的运算")
    operators: Optional[Union[List[str], str]] = Field(..., description="")
    alias_operators: Optional[Union[List[str], str]] = Field(None, description="")
    months: Optional[List[Union[str, int]]] = Field(..., description="衍生月份数")
    id_levels: Union[List[str], str] = Field(..., description="")
    save_db: str = Field(..., description="")
    save_table: str = Field(..., description="")
