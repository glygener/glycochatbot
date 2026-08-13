# Keep this module import-light. Importing IngestionPipeline here caused a
# circular import: query.config -> Ingestion -> retrieval -> query.config
