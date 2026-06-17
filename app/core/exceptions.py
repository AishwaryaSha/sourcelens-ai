"""Application-specific exceptions."""


class SourceLensError(Exception):
    """Base exception for SourceLens AI."""


class ProviderError(SourceLensError):
    """Raised when an external provider fails."""


class SearchError(SourceLensError):
    """Raised when web search fails."""


class PlanningError(SourceLensError):
    """Raised when planning fails."""


class SummarizationError(SourceLensError):
    """Raised when summarization fails."""


class WorkflowError(SourceLensError):
    """Raised when the research workflow fails."""
