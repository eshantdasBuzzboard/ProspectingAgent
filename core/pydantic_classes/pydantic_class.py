from pydantic import BaseModel, Field


class Business(BaseModel):
    company_name: str = Field(
        ..., description="The exact company name you have selected"
    )
    reason: str = Field(
        ..., description="Well desceptive reason why you have selected this Business"
    )
    rank: int = Field(
        ...,
        description="Rank of this business where you are comparing it to the other business",
    )
    rank_reason: str = Field(
        ..., description="The reason why it falls in that specific rank"
    )


class CompaniesSelected(BaseModel):
    companies: list[Business] = Field(
        ...,
        description="List of top companies you have selected along with the reason you have selected them",
    )


class Business_Filters(BaseModel):
    company_name: str = Field(
        ..., description="The exact company name you have selected"
    )
    reason: str = Field(
        ..., description="Well desceptive reason why you have selected this Business"
    )
    rank: int = Field(
        ...,
        description="Rank of this business where you are comparing it to the other business",
    )
    rank_reason: str = Field(
        ..., description="The reason why it falls in that specific rank"
    )
    products: str = Field(..., description="The product name which can be sold ")
    products_reason: str = Field(
        ..., description="Reason why the products will be important for the busines"
    )


class CompaniesSelected_Filters(BaseModel):
    companies: list[Business_Filters] = Field(
        ...,
        description="List of top companies you have selected along with the reason you have selected them",
    )


class Signal(BaseModel):
    signal_name: str | None = Field(
        ..., description="The signal which you have selected based on your analysis "
    )
    signal_value: list[str] = Field(
        ...,
        description="Choose the signal filter values(Make sure to check from examples it can be integer or yes and no)",
    )
    selected_reason: str = Field(
        ..., description="The reason why you have selected the signal"
    )


class Signals(BaseModel):
    signals: list[Signal] | None = Field(
        ...,
        description="List of signals you have selected and the reason why you have selected",
    )


class QuestionReformulatorOutput(BaseModel):
    """
    Output model for the question reformulation process.
    Stores the final reformulated question.
    """

    reformulated_question: str = Field(
        ...,
        description="""
    The reformulated question after processing, or the original current question if independent.
    """,
    )
