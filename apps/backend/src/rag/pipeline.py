from langchain_huggingface import HuggingFaceEmbeddings

from rag.chroma_store import load_vectorstore
from rag.config import RAGConfig
from rag.context_builder import build_context
from rag.gate import RetrievalGate
from rag.generator import AnswerGenerator
from rag.processor import QueryProcessor
from rag.reranker import BGEReranker
from rag.retriever import VectorRetriever
from rag.schemas import RAGResponse


class RAGPipeline:
    def __init__(self, config: RAGConfig | None = None) -> None:
        self.config = config or RAGConfig.from_env()
        self.query_processor = QueryProcessor()

        # Retrieval embeddings always use MiniLM from ingest settings, not LLM_OPTION.
        embeddings = HuggingFaceEmbeddings(
            model_name=self.config.embedding_model,
            model_kwargs={"token": self.config.hf_token},
            encode_kwargs={"normalize_embeddings": True},
        )
        vectorstore = load_vectorstore(self.config, embeddings)

        self.retriever = VectorRetriever(vectorstore, self.config)
        self.reranker = BGEReranker(self.config)
        self.gate = RetrievalGate(self.config)
        self.generator = AnswerGenerator(self.config)

    def ask(self, user_query: str) -> RAGResponse:
        query = self.query_processor.process(user_query)
        candidates = self.retriever.retrieve(query)
        ranked = self.reranker.rerank(query, candidates)

        if not self.gate.passes(ranked):
            return RAGResponse(
                answer=(
                    "I could not find sufficient information in the textbook "
                    "to answer this question."
                ),
                confidence="insufficient",
                in_scope=False,
                sources=[],
                refusal_reason=(
                    "Retrieval scores were below the confidence threshold or "
                    "no relevant chunks were found."
                ),
            )

        docs = [doc for doc, _ in ranked]
        context = build_context(docs)
        response = self.generator.generate(query, context)
        return self._validate_sources(response, len(docs))

    @staticmethod
    def _validate_sources(response: RAGResponse, source_count: int) -> RAGResponse:
        valid_sources = [
            source for source in response.sources if 1 <= source.source_id <= source_count
        ]
        if not valid_sources and response.in_scope:
            return RAGResponse(
                answer=response.answer,
                confidence="low",
                in_scope=False,
                sources=[],
                refusal_reason="Generated citations could not be verified against context.",
            )
        return response.model_copy(update={"sources": valid_sources})
